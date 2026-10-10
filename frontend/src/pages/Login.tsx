import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { CodeXml } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { getProviders, authorizeUrl, completeOAuthLogin, type Providers } from "@/lib/api";

const GitHubIcon = () => (
  <svg viewBox="0 0 16 16" width="18" height="18" fill="currentColor" aria-hidden>
    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z" />
  </svg>
);

const MicrosoftIcon = () => (
  <svg viewBox="0 0 23 23" width="17" height="17" aria-hidden>
    <path fill="#f25022" d="M1 1h10v10H1z" />
    <path fill="#7fba00" d="M12 1h10v10H12z" />
    <path fill="#00a4ef" d="M1 12h10v10H1z" />
    <path fill="#ffb900" d="M12 12h10v10H12z" />
  </svg>
);

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

export default function Login() {
  const { loginWithGoogle, loginWithEmail, register, loading, error } = useAuth();
  const navigate = useNavigate();
  const buttonRef = useRef<HTMLDivElement>(null);

  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [providers, setProviders] = useState<Providers>({ google: false, github: false, microsoft: false });

  // Discover which social providers the backend has credentials for.
  useEffect(() => {
    getProviders()
      .then(setProviders)
      .catch(() => setProviders({ google: false, github: false, microsoft: false }));
  }, []);

  // OAuth code-flow completion: backend redirected back to /login?token=…
  const oauthHandled = useRef(false);
  useEffect(() => {
    if (oauthHandled.current) return;
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (!token) return;
    oauthHandled.current = true;
    const name2 = params.get("name") || "";
    const email2 = params.get("email") || "";
    completeOAuthLogin(token, name2, email2);
    window.history.replaceState({}, document.title, window.location.pathname);
    navigate("/app");
  }, [navigate]);

  // --- Google button (kept as before) ---------------------------------------
  useEffect(() => {
    if (!GOOGLE_CLIENT_ID || !buttonRef.current) return;

    function renderButton() {
      if (!window.google || !buttonRef.current) return;
      window.google.accounts.id.initialize({
        client_id: GOOGLE_CLIENT_ID,
        callback: async (response: { credential: string }) => {
          try {
            await loginWithGoogle(response.credential);
            navigate("/app");
          } catch {
            // error is surfaced via auth context
          }
        },
      });
      window.google.accounts.id.renderButton(buttonRef.current, {
        theme: "filled_black",
        size: "large",
        width: 320,
        text: "signin_with",
      });
    }

    if (window.google) {
      renderButton();
    } else {
      const interval = setInterval(() => {
        if (window.google) {
          clearInterval(interval);
          renderButton();
        }
      }, 100);
      return () => clearInterval(interval);
    }
  }, [loginWithGoogle, navigate]);

  // --- Email / password form -------------------------------------------------
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    if (password.length < 8) {
      setFormError("Password must be at least 8 characters long.");
      return;
    }

    try {
      if (mode === "signin") {
        await loginWithEmail(email.trim(), password);
      } else {
        await register(name.trim(), email.trim(), password);
      }
      navigate("/app");
    } catch {
      // error is surfaced via auth context
    }
  }

  function switchMode(next: "signin" | "signup") {
    setMode(next);
    setFormError(null);
  }

  const inputCls =
    "w-full rounded-lg border border-white/10 bg-ink-950/60 px-3.5 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 outline-none transition focus:border-signal-400/60 focus:ring-2 focus:ring-signal-400/20";

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink-950 px-6">
      <div className="w-full max-w-sm">
        <Link to="/" className="mb-8 flex items-center justify-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
            <CodeXml size={18} strokeWidth={2.5} />
          </span>
          <span className="font-display text-[15px] font-semibold text-slate-100">Software Architect</span>
        </Link>

        <div className="rounded-2xl border border-white/5 bg-ink-800/60 p-8">
          <h1 className="font-display text-xl font-semibold text-slate-100">
            {mode === "signin" ? "Sign in" : "Create account"}
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            {mode === "signin"
              ? "Sign in with your email or Google account to continue."
              : "Sign up with your email, or use Google instead."}
          </p>

          {/* Mode tabs */}
          <div className="mt-5 grid grid-cols-2 gap-1 rounded-lg bg-ink-950/60 p-1" role="tablist">
            {(["signin", "signup"] as const).map((m) => (
              <button
                key={m}
                type="button"
                role="tab"
                aria-selected={mode === m}
                onClick={() => switchMode(m)}
                className={`rounded-md px-3 py-1.5 text-sm font-medium transition ${
                  mode === m
                    ? "bg-signal-400 text-ink-950"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {m === "signin" ? "Sign in" : "Sign up"}
              </button>
            ))}
          </div>

          <form onSubmit={handleSubmit} className="mt-5 space-y-3.5" noValidate>
            {mode === "signup" && (
              <input
                type="text"
                autoComplete="name"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className={inputCls}
              />
            )}
            <input
              type="email"
              autoComplete="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={inputCls}
              required
            />
            <input
              type="password"
              autoComplete={mode === "signin" ? "current-password" : "new-password"}
              placeholder="Password (min. 8 characters)"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className={inputCls}
              required
            />

            {formError && <p className="text-sm text-red-400">{formError}</p>}
            {loading && <p className="text-sm text-slate-400">Signing in…</p>}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-lg bg-signal-400 px-4 py-2.5 text-sm font-semibold text-ink-950 transition hover:bg-signal-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {mode === "signin" ? "Sign in" : "Create account"}
            </button>
          </form>

          {/* Divider + social providers */}
          <div className="my-5 flex items-center gap-3" aria-hidden>
            <span className="h-px flex-1 bg-white/10" />
            <span className="text-xs uppercase tracking-wider text-slate-500">or continue with</span>
            <span className="h-px flex-1 bg-white/10" />
          </div>

          <div className="space-y-2.5">
            {GOOGLE_CLIENT_ID ? (
              <div className="flex justify-center">
                <div ref={buttonRef} />
              </div>
            ) : providers.google ? (
              <p className="text-center text-xs text-slate-500">
                Google sign-in needs VITE_GOOGLE_CLIENT_ID set on the frontend.
              </p>
            ) : null}

            {providers.github && (
              <button
                type="button"
                onClick={() => window.location.assign(authorizeUrl("github"))}
                className="flex w-full items-center justify-center gap-2.5 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-slate-100 transition hover:bg-white/10 hover:border-white/20"
              >
                <GitHubIcon /> Continue with GitHub
              </button>
            )}

            {providers.microsoft && (
              <button
                type="button"
                onClick={() => window.location.assign(authorizeUrl("microsoft"))}
                className="flex w-full items-center justify-center gap-2.5 rounded-lg border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-slate-100 transition hover:bg-white/10 hover:border-white/20"
              >
                <MicrosoftIcon /> Continue with Microsoft
              </button>
            )}

            {!providers.github && !providers.microsoft && !GOOGLE_CLIENT_ID && (
              <p className="text-center text-xs text-slate-500">
                Social sign-in is unavailable — the backend has no provider credentials configured.
              </p>
            )}
          </div>

          {error && <p className="mt-4 text-center text-sm text-red-400">{error}</p>}
        </div>
      </div>
    </div>
  );
}
