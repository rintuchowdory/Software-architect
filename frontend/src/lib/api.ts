// Same-origin "/api" always: Vite proxies it to the local backend in dev,
// and Vercel rewrites it to the Render API in production (see vercel.json).
// This keeps the browser away from cross-origin/CORS and stale build env vars.
const BASE = "/api";

function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("sa_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: "POST", body: data ? JSON.stringify(data) : undefined }),
  patch: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: "PATCH", body: data ? JSON.stringify(data) : undefined }),
  del: <T>(path: string) => request<T>(path, { method: "DELETE" }),
};

export type User = { id: string; name: string; email: string };

export type LoginResponse = { access_token: string; user: User };

export function logout() {
  localStorage.removeItem("sa_token");
  localStorage.removeItem("sa_user");
}

export function currentUser(): User | null {
  const raw = localStorage.getItem("sa_user");
  return raw ? (JSON.parse(raw) as User) : null;
}

export async function register(name: string, email: string, password: string) {
  const res = await api.post<LoginResponse>("/auth/register", { name, email, password });
  localStorage.setItem("sa_token", res.access_token);
  localStorage.setItem("sa_user", JSON.stringify(res.user));
  return res.user;
}

export async function loginWithEmail(email: string, password: string) {
  const res = await api.post<LoginResponse>("/auth/login", { email, password });
  localStorage.setItem("sa_token", res.access_token);
  localStorage.setItem("sa_user", JSON.stringify(res.user));
  return res.user;
}
