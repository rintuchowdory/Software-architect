const BASE = import.meta.env.VITE_API_BASE || "/api";

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

export async function loginWithGoogle(credential: string) {
  const res = await api.post<LoginResponse>("/auth/google", { credential });
  localStorage.setItem("sa_token", res.access_token);
  localStorage.setItem("sa_user", JSON.stringify(res.user));
  return res.user;
}

export function logout() {
  localStorage.removeItem("sa_token");
  localStorage.removeItem("sa_user");
}

export function currentUser() {
  const raw = localStorage.getItem("sa_user");
  return raw ? JSON.parse(raw) : null;
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

// ── Social providers (GitHub / Microsoft OAuth code flow) ────────────────────

export type Providers = { google: boolean; github: boolean; microsoft: boolean };

export async function getProviders(): Promise<Providers> {
  return api.get<Providers>("/auth/providers");
}

export type OAuthProvider = "github" | "microsoft";

export function authorizeUrl(provider: OAuthProvider): string {
  const redirect_uri = `${window.location.origin}/login`;
  return `${BASE}/auth/${provider}/authorize?${new URLSearchParams({ redirect_uri })}`;
}

/** Completes the OAuth code-flow login returned by the backend. */
export function completeOAuthLogin(token: string, name: string, email: string): User {
  // The backend signs the actual database user ID into the JWT subject claim.
  // Reuse it rather than creating a client-only ID or storing an empty ID.
  const parts = token.split(".");
  if (parts.length !== 3 || !parts[1]) {
    throw new Error("The sign-in provider returned an invalid session token.");
  }

  const base64 = parts[1].replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
  let claims: { sub?: unknown };
  try {
    const binary = atob(padded);
    const bytes = Uint8Array.from(binary, (character) => character.charCodeAt(0));
    claims = JSON.parse(new TextDecoder().decode(bytes)) as { sub?: unknown };
  } catch {
    throw new Error("The sign-in provider returned an unreadable session token.");
  }

  if (typeof claims.sub !== "string" || claims.sub.trim() === "") {
    throw new Error("The session token did not contain a user ID.");
  }

  const user: User = { id: claims.sub, name, email };
  localStorage.setItem("sa_token", token);
  localStorage.setItem("sa_user", JSON.stringify(user));
  return user;
}
