function normalizeApiBase(rawValue) {
  const raw = (rawValue || "").trim();
  if (!raw) return "/api";

  const withoutTrailingSlash = raw.replace(/\/+$/, "");
  if (withoutTrailingSlash === "/api") return "/api";
  if (/\/api$/i.test(withoutTrailingSlash)) {
    return withoutTrailingSlash.replace(/\/api$/i, "");
  }
  return withoutTrailingSlash;
}

const API_BASE = normalizeApiBase(import.meta.env.VITE_API_BASE_URL);

function getToken() {
  return localStorage.getItem("resumate_token") || "";
}

export function setToken(token) {
  if (token) localStorage.setItem("resumate_token", token);
  else localStorage.removeItem("resumate_token");
}

async function request(path, { method = "GET", headers, body } = {}) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      ...(body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers || {}),
    },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  const data = text ? safeJson(text) : null;
  if (!res.ok) {
    const message = extractErrorMessage(data, res.statusText || "Request failed");
    const err = new Error(message);
    err.status = res.status;
    throw err;
  }
  return data;
}

function safeJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return { raw: text };
  }
}

function extractErrorMessage(data, fallback) {
  if (!data) return fallback;
  const detail = data.detail ?? data.message ?? data.error ?? null;
  if (!detail) return fallback;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    // FastAPI validation errors look like: [{loc:..., msg:..., type:...}, ...]
    const msgs = detail
      .map((item) => {
        if (!item) return null;
        if (typeof item === "string") return item;
        if (typeof item === "object" && item.msg) return item.msg;
        try {
          return JSON.stringify(item);
        } catch {
          return String(item);
        }
      })
      .filter(Boolean);
    return msgs.length ? msgs.join("; ") : fallback;
  }
  if (typeof detail === "object") {
    if (detail.msg && typeof detail.msg === "string") return detail.msg;
    try {
      return JSON.stringify(detail);
    } catch {
      return fallback;
    }
  }
  return String(detail);
}

export const api = {
  health: () => request("/health"),
  roles: () => request("/roles"),
  signup: (email, password) => request("/auth/signup", { method: "POST", body: { email, password } }),
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/me"),
  resetRequest: (email) => request("/auth/reset/request", { method: "POST", body: { email } }),
  resetConfirm: (email, code, new_password) =>
    request("/auth/reset/confirm", { method: "POST", body: { email, code, new_password } }),
  analyze: (role, file) => {
    const form = new FormData();
    form.append("selected_role", role);
    form.append("file", file);
    return request("/analyze", { method: "POST", body: form });
  },
  history: () => request("/history"),
  historyDetail: (id) => request(`/history/${id}`),
};
