// Thin fetch wrapper around the Slate API. Attaches the bearer token and
// normalises error handling so callers get a readable message.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOKEN_KEY = "slate_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

async function request(path, { method = "GET", body, isForm = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  let payload = body;
  if (body && !isForm) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(`${BASE_URL}${path}`, { method, headers, body: payload });
  } catch {
    throw new ApiError(0, "Cannot reach the server. Is the API running?");
  }

  if (res.status === 204) return null;

  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  if (!res.ok) {
    const detail =
      (data && data.detail) ||
      (typeof data === "string" ? data : "Request failed");
    // FastAPI validation errors arrive as arrays of objects.
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail;
    throw new ApiError(res.status, message);
  }

  return data;
}

export const api = {
  login: (email, password) =>
    request("/login", { method: "POST", body: { email, password } }),
  me: () => request("/me"),
  users: () => request("/users"),
  listDocuments: () => request("/documents"),
  createDocument: (title, content_json = "") =>
    request("/documents", { method: "POST", body: { title, content_json } }),
  getDocument: (id) => request(`/documents/${id}`),
  updateDocument: (id, patch) =>
    request(`/documents/${id}`, { method: "PUT", body: patch }),
  shareDocument: (id, email) =>
    request(`/documents/${id}/share`, { method: "POST", body: { email } }),
  importDocument: (file, title) => {
    const form = new FormData();
    form.append("file", file);
    if (title) form.append("title", title);
    return request("/documents/import", {
      method: "POST",
      body: form,
      isForm: true,
    });
  },
};
