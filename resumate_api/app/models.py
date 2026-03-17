from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ResetRequest(BaseModel):
    email: EmailStr


class ResetConfirmRequest(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=128)
    new_password: str = Field(min_length=6)


class TokenResponse(BaseModel):
    token: str


class MeResponse(BaseModel):
    email: EmailStr
    display_name: str


class RoleItem(BaseModel):
    sector: str
    name: str
    description: str


class AnalyzeResponse(BaseModel):
    submission_id: int
    submitted_at: str
    selected_role: str
    job_description: str
    details: dict[str, str]
    extracted_text: str
    match_score: float
    ats_score: float
    expected_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    match_explanation: str
    section_insights: list[dict[str, object]]
    learning_plan: list[dict[str, object]]
    ai_summary: str
    ai_strengths: list[str]
    ai_risks: list[str]
    ai_next_steps: list[str]


class HistoryItem(BaseModel):
    id: int
    submitted_at: str
    applied_role: str
    match_score: float
    ats_score: float
    resume_file: Optional[str] = None


class HistoryDetail(BaseModel):
    id: int
    submitted_at: str
    applied_role: str
    match_score: float
    ats_score: float
    details: dict[str, str]
    extracted_text: str
    ai_summary: str
    ai_strengths: list[str]
    ai_risks: list[str]
    ai_next_steps: list[str]
