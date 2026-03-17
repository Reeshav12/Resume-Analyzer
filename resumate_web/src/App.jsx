import React, { useEffect, useMemo, useState } from "react";
import { api, setToken } from "./api.js";

const SECTIONS = ["Dashboard", "Extracted details", "AI analyzer", "Learning plan", "Extracted text", "History"];

function classNames(...parts) {
  return parts.filter(Boolean).join(" ");
}

function hashStringToInt(value) {
  const str = String(value || "");
  let hash = 2166136261;
  for (let i = 0; i < str.length; i += 1) {
    hash ^= str.charCodeAt(i);
    hash = Math.imul(hash, 16777619);
  }
  return hash >>> 0;
}

function makeLogoStyle(seed) {
  const h = hashStringToInt(seed) % 360;
  const h2 = (h + 32) % 360;
  return {
    background: `linear-gradient(135deg, hsl(${h} 70% 22%), hsl(${h2} 78% 44%))`,
  };
}

function initialsForUser(displayName, email) {
  const name = String(displayName || "").trim();
  const parts = name
    .split(/\s+/)
    .map((p) => p.trim())
    .filter(Boolean);
  if (parts.length >= 2) return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  if (parts.length === 1 && parts[0].length >= 2) return parts[0].slice(0, 2).toUpperCase();

  const local = String(email || "").split("@")[0] || "rm";
  return local.slice(0, 2).toUpperCase();
}

function Pill({ tone = "neutral", children }) {
  return <span className={classNames("pill", `pill--${tone}`)}>{children}</span>;
}

function Card({ title, children, className }) {
  return (
    <section className={classNames("card", className)}>
      {title ? <h3 className="card__title">{title}</h3> : null}
      {children}
    </section>
  );
}

function Metric({ label, value, hint }) {
  return (
    <div className="metric">
      <div className="metric__label">{label}</div>
      <div className="metric__value">{value}</div>
      {hint ? <div className="metric__hint">{hint}</div> : null}
    </div>
  );
}

function AuthView({ onAuthed }) {
  const [tab, setTab] = useState("Sign in");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [signupEmail, setSignupEmail] = useState("");
  const [signupPassword, setSignupPassword] = useState("");

  const [resetEmail, setResetEmail] = useState("");
  const [resetCode, setResetCode] = useState("");
  const [resetPassword, setResetPassword] = useState("");
  const [demoCode, setDemoCode] = useState("");

  async function handleLogin(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      const data = await api.login(email, password);
      setToken(data.token);
      onAuthed();
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleSignup(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      await api.signup(signupEmail, signupPassword);
      setInfo("Account created. Please sign in.");
      setTab("Sign in");
      setEmail(signupEmail);
      setPassword("");
    } catch (err) {
      setError(err.message || "Sign up failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleResetRequest(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      const data = await api.resetRequest(resetEmail);
      setDemoCode(data.code || "");
      setInfo("Reset code generated (demo). Use it below to set a new password.");
    } catch (err) {
      setError(err.message || "Reset request failed");
    } finally {
      setBusy(false);
    }
  }

  async function handleResetConfirm(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    setInfo("");
    try {
      await api.resetConfirm(resetEmail, resetCode, resetPassword);
      setInfo("Password updated. You can sign in now.");
      setTab("Sign in");
      setEmail(resetEmail);
      setPassword("");
      setResetCode("");
      setResetPassword("");
      setDemoCode("");
    } catch (err) {
      setError(err.message || "Reset confirm failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell shell--auth">
      <header className="hero">
        <div className="hero__eyebrow">ResuMate</div>
        <h1 className="hero__title">Resume screening that looks sharp and stays simple.</h1>
        <p className="hero__subtitle">
          Sign in to your dashboard, upload a PDF resume, and get Ollama-powered role match + ATS guidance with clear next steps.
        </p>
      </header>

      <div className="auth-grid">
        <Card title="Access">
          <div className="tabs">
            {["Sign in", "Sign up", "Reset"].map((label) => (
              <button
                key={label}
                className={classNames("tabs__tab", tab === label && "is-active")}
                onClick={() => {
                  setTab(label);
                  setError("");
                  setInfo("");
                }}
                type="button"
              >
                {label}
              </button>
            ))}
          </div>

          {error ? <div className="notice notice--error">{error}</div> : null}
          {info ? <div className="notice notice--info">{info}</div> : null}

          {tab === "Sign in" ? (
            <form onSubmit={handleLogin} className="form">
              <label className="field">
                <span>Email</span>
                <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
              </label>
              <label className="field">
                <span>Password</span>
                <input
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  type="password"
                  placeholder="••••••••"
                />
              </label>
              <button className="btn btn--primary" disabled={busy}>
                {busy ? "Signing in..." : "Sign in"}
              </button>
              <div className="form__hint">Demo: applicant@example.com / applicant123</div>
            </form>
          ) : null}

          {tab === "Sign up" ? (
            <form onSubmit={handleSignup} className="form">
              <label className="field">
                <span>Email</span>
                <input
                  value={signupEmail}
                  onChange={(e) => setSignupEmail(e.target.value)}
                  placeholder="newuser@example.com"
                />
              </label>
              <label className="field">
                <span>Password</span>
                <input
                  value={signupPassword}
                  onChange={(e) => setSignupPassword(e.target.value)}
                  type="password"
                  placeholder="At least 6 characters"
                />
              </label>
              <button className="btn btn--primary" disabled={busy}>
                {busy ? "Creating..." : "Create account"}
              </button>
            </form>
          ) : null}

          {tab === "Reset" ? (
            <div className="stack">
              <form onSubmit={handleResetRequest} className="form">
                <label className="field">
                  <span>Registered email</span>
                  <input
                    value={resetEmail}
                    onChange={(e) => setResetEmail(e.target.value)}
                    placeholder="you@example.com"
                  />
                </label>
                <button className="btn" disabled={busy}>
                  {busy ? "Generating..." : "Generate reset code"}
                </button>
                {demoCode ? <div className="notice notice--demo">Demo reset code: {demoCode}</div> : null}
              </form>

              <form onSubmit={handleResetConfirm} className="form">
                <label className="field">
                  <span>Reset code</span>
                  <input value={resetCode} onChange={(e) => setResetCode(e.target.value)} />
                </label>
                <label className="field">
                  <span>New password</span>
                  <input
                    value={resetPassword}
                    onChange={(e) => setResetPassword(e.target.value)}
                    type="password"
                  />
                </label>
                <button className="btn btn--primary" disabled={busy}>
                  {busy ? "Updating..." : "Update password"}
                </button>
              </form>
            </div>
          ) : null}
        </Card>

        <div className="feature-stack">
          <Card title="What you get">
            <ul className="list">
              <li>Role match score (keyword-based)</li>
              <li>Ollama-backed ATS score with clear improvements</li>
              <li>Learning plan for missing skills</li>
              <li>History of your analyses</li>
            </ul>
          </Card>
          <Card title="No recruiter mode">
            <p className="muted">
              This React version is single-user and dashboard-first. Upload, analyze, iterate.
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ user, section, setSection, onLogout, roles, selectedRole, setSelectedRole }) {
  const initials = initialsForUser(user.display_name, user.email);
  const logoStyle = makeLogoStyle(user.email || user.display_name || initials);

  return (
    <aside className="sidebar">
      <div className="sidebar__top">
        <div className="sidebar__brand">
          <div className="logo" style={logoStyle} aria-label="User logo">
            {initials}
          </div>
          <div>
            <div className="sidebar__title">{user.display_name}</div>
            <div className="sidebar__subtitle">ResuMate dashboard</div>
          </div>
        </div>

        <div className="sidebar__user">
          <div className="sidebar__userName">{user.display_name}</div>
          <div className="sidebar__userEmail">{user.email}</div>
        </div>

        <div className="sidebar__sectionLabel">Sections</div>
        <nav className="nav">
          {SECTIONS.map((item) => (
            <button
              key={item}
              className={classNames("nav__item", section === item && "is-active")}
              onClick={() => setSection(item)}
              type="button"
            >
              {item}
            </button>
          ))}
        </nav>
      </div>

      <div className="sidebar__bottom">
        <button className="btn btn--ghost sidebar__logout" onClick={onLogout} type="button">
          Logout
        </button>
      </div>
    </aside>
  );
}

function EmptyState({ title, body }) {
  return (
    <Card>
      <h2 className="h2">{title}</h2>
      <p className="muted">{body}</p>
    </Card>
  );
}

export default function App() {
  const [authed, setAuthed] = useState(false);
  const [user, setUser] = useState(null);
  const [roles, setRoles] = useState([]);
  const [selectedRole, setSelectedRole] = useState("Software Engineer");
  const [section, setSection] = useState("Dashboard");

  const [jobDescription, setJobDescription] = useState("");
  const [file, setFile] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [history, setHistory] = useState([]);

  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const roleGroups = useMemo(() => {
    return roles.reduce((acc, role) => {
      const current = acc[role.sector] || [];
      current.push(role);
      acc[role.sector] = current;
      return acc;
    }, {});
  }, [roles]);

  async function bootstrap() {
    const [rolesData, meData, historyData] = await Promise.all([api.roles(), api.me(), api.history()]);
    setRoles(rolesData);
    setUser(meData);
    setHistory(historyData);

    const defaultRole = rolesData.find((r) => r.name === selectedRole) || rolesData[0];
    setSelectedRole(defaultRole?.name || "Software Engineer");
    setJobDescription(defaultRole?.description || "");
  }

  useEffect(() => {
    // Try to reuse token from a previous session.
    (async () => {
      try {
        await bootstrap();
        setAuthed(true);
      } catch (err) {
        setAuthed(false);
      }
    })();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const item = roles.find((r) => r.name === selectedRole);
    if (item) setJobDescription(item.description);
  }, [roles, selectedRole]);

  const selectedRoleItem = useMemo(() => roles.find((r) => r.name === selectedRole) || null, [roles, selectedRole]);

  async function onAuthed() {
    await bootstrap();
    setAuthed(true);
  }

  function onLogout() {
    setToken("");
    setAuthed(false);
    setUser(null);
    setAnalysis(null);
    setHistory([]);
  }

  async function runAnalyze() {
    if (!file) {
      setError("Please choose a PDF resume first.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const data = await api.analyze(selectedRole, file);
      setAnalysis(data);
      const hist = await api.history();
      setHistory(hist);
      setSection("Dashboard");
    } catch (err) {
      setError(err.message || "Analyze failed");
    } finally {
      setBusy(false);
    }
  }

  const selectedHistory = useMemo(() => {
    if (!analysis) return null;
    return null;
  }, [analysis]);

  if (!authed) return <AuthView onAuthed={onAuthed} />;
  if (!user) return <div className="shell">Loading...</div>;

  const metrics = analysis
    ? [
        { label: "Match", value: `${analysis.match_score.toFixed(2)}%` },
        { label: "ATS", value: `${analysis.ats_score.toFixed(2)}%` },
        { label: "Matched skills", value: `${analysis.matched_skills.length}` },
        { label: "Missing skills", value: `${analysis.missing_skills.length}` },
      ]
    : [];

  return (
    <div className="app">
      <Sidebar
        user={user}
        section={section}
        setSection={setSection}
        onLogout={onLogout}
      />

      <main className="main">
        <header className="main__hero">
          <div className="main__heroEyebrow">{user.display_name}</div>
          <h2 className="main__heroTitle">Your resume dashboard</h2>
          <p className="main__heroSubtitle">Ollama-backed ATS scoring and role keyword matching.</p>
        </header>

        <div className="grid">
          <Card title="Role description" className="span-2">
            <div className="role-panel">
              <div className="role-panel__meta">
                <span className="badge badge--soft">{selectedRole}</span>
              </div>
              <p className="muted">{jobDescription}</p>
            </div>
          </Card>

          <Card title="Upload & analyze">
            <div className="stack">
              <label className="field">
                <span>Target role by sector</span>
                <select className="select select--inline" value={selectedRole} onChange={(e) => setSelectedRole(e.target.value)}>
                  {Object.entries(roleGroups).map(([sector, sectorRoles]) => (
                    <optgroup key={sector} label={sector}>
                      {sectorRoles.map((r) => (
                        <option key={r.name} value={r.name}>
                          {r.name}
                        </option>
                      ))}
                    </optgroup>
                  ))}
                </select>
              </label>
              <div className="form__hint">
                Choose a sector first in the dropdown group, then pick the closest target role for more accurate keyword matching.
              </div>
              <input
                className="file"
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
              />
              <button className="btn btn--primary" onClick={runAnalyze} disabled={busy}>
                {busy ? "Analyzing..." : "Analyze resume"}
              </button>
              {error ? <div className="notice notice--error">{error}</div> : null}
              <div className="form__hint">Tip: use a PDF with selectable text for best extraction.</div>
            </div>
          </Card>
        </div>

        {analysis ? (
          <div className="metrics">
            {metrics.map((m) => (
              <Metric key={m.label} label={m.label} value={m.value} />
            ))}
          </div>
        ) : (
          <EmptyState title="No analysis yet" body="Upload a PDF resume and run the analyzer to populate the dashboard." />
        )}

        {analysis ? (
          <div className="content">
            {section === "Dashboard" ? (
              <div className="two-col">
                <Card title="Role keywords (match)">
                  <div className="stack">
                    <div className="muted">{analysis.match_explanation || ""}</div>
                    <div>
                      <div className="label">Matched</div>
                      <div className="pill-row">
                        {analysis.matched_skills.length ? (
                          analysis.matched_skills.map((s) => <Pill key={s} tone="good">{s}</Pill>)
                        ) : (
                          <span className="muted">No matched keywords detected yet.</span>
                        )}
                      </div>
                    </div>
                    <div>
                      <div className="label">Missing (add only if you can prove it)</div>
                      <div className="pill-row">
                        {analysis.missing_skills.length ? (
                          analysis.missing_skills.map((s) => <Pill key={s} tone="warn">{s}</Pill>)
                        ) : (
                          <span className="muted">No missing keywords detected.</span>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>

                <Card title="Section-wise improvements (ATS + role-fit)">
                  {analysis.section_insights?.length ? (
                    <div className="stack">
                      {analysis.section_insights.map((ins) => (
                        <div
                          key={ins.section}
                          className={classNames("insight", `insight--${ins.tone || "warn"}`)}
                        >
                          <div className="insight__head">
                            <div className="insight__title">{ins.section}</div>
                            <div className="insight__score">{Number(ins.score || 0)}%</div>
                          </div>
                          {Array.isArray(ins.actions) && ins.actions.length ? (
                            <ul className="list">
                              {ins.actions.map((a) => (
                                <li key={a}>{a}</li>
                              ))}
                            </ul>
                          ) : (
                            <div className="muted">No actions for this section.</div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="muted">No section insights available.</div>
                  )}
                  <div className="muted small">
                    Tip: The fastest ATS wins usually come from headings, clean bullets, and adding measurable impact.
                  </div>
                </Card>
              </div>
            ) : null}

            {section === "Extracted details" ? (
              <div className="details-grid">
                {Object.entries(analysis.details).map(([k, v]) => (
                  <Card key={k} title={k}>
                    <div className="mono">{v}</div>
                  </Card>
                ))}
              </div>
            ) : null}

            {section === "AI analyzer" ? (
              <div className="two-col">
                <Card title="Summary">
                  <p className="muted">{analysis.ai_summary}</p>
                </Card>
                <Card title="Strengths / Risks / Next steps">
                  <div className="stack">
                    <div>
                      <div className="label">Strengths</div>
                      <ul className="list">
                        {analysis.ai_strengths.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="label">Risks</div>
                      <ul className="list">
                        {analysis.ai_risks.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <div className="label">Next steps</div>
                      <ul className="list">
                        {analysis.ai_next_steps.map((x) => (
                          <li key={x}>{x}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </Card>
              </div>
            ) : null}

            {section === "Learning plan" ? (
              <Card title="Learning plan">
                {analysis.learning_plan?.length ? (
                  <div className="stack">
                    {analysis.learning_plan.map((item) => (
                      <div key={item.skill} className="learn">
                        <div className="learn__title">{item.skill}</div>
                        <div className="learn__grid">
                          <div>
                            <div className="label">Courses and sources</div>
                            {Array.isArray(item.resources) && item.resources.length ? (
                              <ul className="list">
                                {item.resources.slice(0, 4).map((r) => (
                                  <li key={r.url}>
                                    <a className="link" href={r.url} target="_blank" rel="noreferrer">
                                      {r.title}
                                    </a>
                                  </li>
                                ))}
                              </ul>
                            ) : (
                              <div className="muted">No resources found.</div>
                            )}
                          </div>
                          <div>
                            <div className="label">What to add in your resume</div>
                            <ul className="list">
                              <li>One project bullet proving {item.skill} with a result metric (time saved, accuracy, users, latency).</li>
                              <li>Add {item.skill} in Skills only if it’s used in Projects/Experience.</li>
                              <li>Use the same wording as the role description when it’s true.</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted">No gaps detected for this role.</p>
                )}
              </Card>
            ) : null}

            {section === "Extracted text" ? (
              <Card title="Extracted text">
                <textarea className="textarea" value={analysis.extracted_text || ""} readOnly />
              </Card>
            ) : null}

            {section === "History" ? (
              <Card title="History">
                {history.length ? (
                  <div className="table">
                    <div className="table__head">
                      <div>Date</div>
                      <div>Role</div>
                      <div>Match</div>
                      <div>ATS</div>
                      <div>File</div>
                    </div>
                    {history.map((h) => (
                      <div className="table__row" key={h.id}>
                        <div>{h.submitted_at}</div>
                        <div>{h.applied_role}</div>
                        <div>{Number(h.match_score).toFixed(1)}%</div>
                        <div>{Number(h.ats_score).toFixed(1)}%</div>
                        <div className="muted">{h.resume_file || "-"}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="muted">No saved analyses yet.</p>
                )}
              </Card>
            ) : null}
          </div>
        ) : null}
      </main>
    </div>
  );
}
