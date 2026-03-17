from __future__ import annotations

from datetime import datetime, timedelta
from io import BytesIO
from typing import Optional

import pdfplumber
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import db
from .config import settings
from .models import (
    AnalyzeResponse,
    HistoryDetail,
    HistoryItem,
    LoginRequest,
    MeResponse,
    ResetConfirmRequest,
    ResetRequest,
    RoleItem,
    SignupRequest,
    TokenResponse,
)
from .scoring import JOB_DESCRIPTIONS, ROLE_CATALOG, analyze_resume
from .security import hash_password, new_token, token_hash, verify_password


app = FastAPI(title="ResuMate API", version="1.0.0")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bearer = HTTPBearer(auto_error=False)


@app.on_event("startup")
def _startup():
    db.init_db()
    # Demo user for quick testing.
    demo_email = "applicant@example.com"
    if not db.fetch_one("SELECT id FROM users WHERE email = ?", (_normalize_email(demo_email),)):
        timestamp = db.now_text()
        db.execute(
            "INSERT INTO users (email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (_normalize_email(demo_email), hash_password("applicant123"), timestamp, timestamp),
        )


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _display_name_for_email(email: str) -> str:
    local_part = _normalize_email(email).split("@")[0]
    cleaned = local_part.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    if local_part in {"applicant", "user", "recruiter"} or not cleaned:
        return _normalize_email(email) or "User"
    return " ".join(part.capitalize() for part in cleaned.split())


def _looks_like_real_name(value: str) -> bool:
    name = (value or "").strip()
    if not name or len(name) > 60:
        return False
    if "@" in name or any(ch.isdigit() for ch in name):
        return False
    lowered = name.lower()
    if any(w in lowered for w in ["resume", "curriculum vitae", "cv", "portfolio", "linkedin", "github"]):
        return False
    if any(w in lowered.split() for w in ["engineer", "developer", "intern", "analyst", "designer", "manager", "student"]):
        return False
    # Require at least one space for "First Last" style names.
    if " " not in name:
        return False
    return True


def require_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> dict:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token.")

    raw_token = credentials.credentials
    hashed = token_hash(raw_token)
    token_row = db.fetch_one("SELECT * FROM auth_tokens WHERE token_hash = ?", (hashed,))
    if not token_row:
        raise HTTPException(status_code=401, detail="Invalid token.")
    if token_row["expires_at"] < db.now_text():
        raise HTTPException(status_code=401, detail="Token expired.")

    user = db.fetch_one("SELECT * FROM users WHERE id = ?", (token_row["user_id"],))
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/roles", response_model=list[RoleItem])
def roles():
    items: list[RoleItem] = []
    for sector, sector_roles in ROLE_CATALOG.items():
        for role in sector_roles:
            items.append(RoleItem(sector=sector, name=role["name"], description=role["description"]))
    return items


@app.post("/auth/signup")
def signup(payload: SignupRequest):
    email = _normalize_email(payload.email)
    if db.fetch_one("SELECT id FROM users WHERE email = ?", (email,)):
        raise HTTPException(status_code=400, detail="Email already registered.")

    timestamp = db.now_text()
    db.execute(
        "INSERT INTO users (email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?)",
        (email, hash_password(payload.password), timestamp, timestamp),
    )
    return {"ok": True}


@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest):
    email = _normalize_email(payload.email)
    user = db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    token = new_token()
    hashed = token_hash(token)
    now = datetime.now()
    expires_at = (now + timedelta(minutes=settings.token_ttl_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO auth_tokens (token_hash, user_id, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (hashed, int(user["id"]), now.strftime("%Y-%m-%d %H:%M:%S"), expires_at),
    )
    return TokenResponse(token=token)


@app.post("/auth/reset/request")
def reset_request(payload: ResetRequest):
    email = _normalize_email(payload.email)
    user = db.fetch_one("SELECT id FROM users WHERE email = ?", (email,))
    if not user:
        raise HTTPException(status_code=404, detail="No account exists for that email.")

    code = new_token()[:10]
    now = datetime.now()
    expires_at = (now + timedelta(minutes=settings.reset_token_ttl_minutes)).strftime("%Y-%m-%d %H:%M:%S")
    db.execute(
        "INSERT INTO password_resets (email, reset_code, expires_at, created_at) VALUES (?, ?, ?, ?)",
        (email, code, expires_at, now.strftime("%Y-%m-%d %H:%M:%S")),
    )
    # Demo: return code. Production should email instead.
    return {"ok": True, "code": code, "expires_at": expires_at}


@app.post("/auth/reset/confirm")
def reset_confirm(payload: ResetConfirmRequest):
    email = _normalize_email(payload.email)
    row = db.fetch_one(
        "SELECT * FROM password_resets WHERE email = ? AND reset_code = ?",
        (email, payload.code.strip()),
    )
    if not row:
        raise HTTPException(status_code=400, detail="Invalid reset code.")
    if row["expires_at"] < db.now_text():
        raise HTTPException(status_code=400, detail="Reset code expired.")

    timestamp = db.now_text()
    db.execute(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE email = ?",
        (hash_password(payload.new_password), timestamp, email),
    )
    db.execute("DELETE FROM password_resets WHERE email = ?", (email,))
    return {"ok": True}


@app.get("/me", response_model=MeResponse)
def me(user: dict = Depends(require_user)):
    email = user["email"]
    latest = db.fetch_one(
        "SELECT candidate_name FROM resume_submissions WHERE submitted_by = ? ORDER BY submitted_at DESC LIMIT 1",
        (_normalize_email(email),),
    )
    display_name = None
    if latest:
        candidate = (latest.get("candidate_name") or "").strip()
        if candidate and candidate != "Not found" and _looks_like_real_name(candidate):
            display_name = candidate
    return MeResponse(email=email, display_name=display_name or _display_name_for_email(email))


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(selected_role: str = Form(...), file: UploadFile = File(...), user: dict = Depends(require_user)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF file.")

    content = file.file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file.")

    with pdfplumber.open(BytesIO(content)) as pdf:
        extracted = "\n".join((page.extract_text() or "") for page in pdf.pages).strip()

    if not extracted:
        raise HTTPException(status_code=400, detail="No readable text found in the PDF.")

    try:
        result = analyze_resume(extracted, selected_role)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    submitted_at = db.now_text()
    applied_role = selected_role if selected_role in JOB_DESCRIPTIONS else "Software Engineer"
    submission_id = db.execute_returning_id(
        """
        INSERT INTO resume_submissions (
            user_id, submitted_by, resume_file, applied_role, match_score, ats_score,
            candidate_name, candidate_email, candidate_phone, skills, education, experience,
            extracted_text, ai_summary, ai_strengths, ai_risks, ai_next_steps, submitted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            int(user["id"]),
            _normalize_email(user["email"]),
            file.filename,
            applied_role,
            float(result.match_score),
            float(result.ats_score),
            result.details.get("Name", ""),
            result.details.get("Email", ""),
            result.details.get("Phone", ""),
            result.details.get("Skills", ""),
            result.details.get("Education", ""),
            result.details.get("Experience", ""),
            extracted,
            result.ai_summary,
            "\n".join(result.ai_strengths),
            "\n".join(result.ai_risks),
            "\n".join(result.ai_next_steps),
            submitted_at,
        ),
    )

    return AnalyzeResponse(
        submission_id=submission_id,
        submitted_at=submitted_at,
        selected_role=applied_role,
        job_description=JOB_DESCRIPTIONS[applied_role],
        details=result.details,
        extracted_text=extracted,
        match_score=result.match_score,
        ats_score=result.ats_score,
        expected_skills=result.expected_skills,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        match_explanation=result.match_explanation,
        section_insights=result.section_insights,
        learning_plan=result.learning_plan,
        ai_summary=result.ai_summary,
        ai_strengths=result.ai_strengths,
        ai_risks=result.ai_risks,
        ai_next_steps=result.ai_next_steps,
    )


@app.get("/history", response_model=list[HistoryItem])
def history(user: dict = Depends(require_user)):
    rows = db.fetch_all(
        """
        SELECT id, submitted_at, applied_role, match_score, ats_score, resume_file
        FROM resume_submissions
        WHERE submitted_by = ?
        ORDER BY submitted_at DESC
        """,
        (_normalize_email(user["email"]),),
    )
    return [
        HistoryItem(
            id=int(row["id"]),
            submitted_at=row["submitted_at"],
            applied_role=row["applied_role"],
            match_score=float(row["match_score"]),
            ats_score=float(row["ats_score"]),
            resume_file=row.get("resume_file"),
        )
        for row in rows
    ]


@app.get("/history/{submission_id}", response_model=HistoryDetail)
def history_detail(submission_id: int, user: dict = Depends(require_user)):
    row = db.fetch_one(
        """
        SELECT *
        FROM resume_submissions
        WHERE id = ? AND submitted_by = ?
        """,
        (submission_id, _normalize_email(user["email"])),
    )
    if not row:
        raise HTTPException(status_code=404, detail="Not found.")

    strengths = [line for line in (row.get("ai_strengths") or "").splitlines() if line.strip()]
    risks = [line for line in (row.get("ai_risks") or "").splitlines() if line.strip()]
    next_steps = [line for line in (row.get("ai_next_steps") or "").splitlines() if line.strip()]

    details = {
        "Name": row.get("candidate_name") or "Not found",
        "Email": row.get("candidate_email") or "Not found",
        "Phone": row.get("candidate_phone") or "Not found",
        "Skills": row.get("skills") or "Not found",
        "Education": row.get("education") or "Not found",
        "Experience": row.get("experience") or "Not found",
    }

    return HistoryDetail(
        id=int(row["id"]),
        submitted_at=row["submitted_at"],
        applied_role=row["applied_role"],
        match_score=float(row["match_score"]),
        ats_score=float(row["ats_score"]),
        details=details,
        extracted_text=row.get("extracted_text") or "",
        ai_summary=row.get("ai_summary") or "",
        ai_strengths=strengths,
        ai_risks=risks,
        ai_next_steps=next_steps,
    )
