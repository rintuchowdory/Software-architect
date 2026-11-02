import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { CodeXml } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
  const { loginWithEmail, register, loading, error } = useAuth();
  const navigate = useNavigate();

  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  // --- Email / password form -------------------------------------------------
  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setFormError(null);

    const cleanEmail = email.trim();

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(cleanEmail)) {
      setFormError("Please enter a valid email address.");
      return;
    }

    if (mode === "signup" && password.length < 8) {
      setFormError("Password must be at least 8 characters long.");
      return;
    }

    if (mode === "signup" && name.trim().length < 2) {
      setFormError("Please enter your name.");
      return;
    }

    try {
      if (mode === "signin") {
        await loginWithEmail(cleanEmail, password);
      } else {
        await register(name.trim(), cleanEmail, password);
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
            {mode === "signin" ? "Sign in" : "Create your account"}
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            {mode === "signin"
              ? "Enter your email and password to continue."
              : "Use your work email and a password of at least 8 characters."}
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
              placeholder={mode === "signin" ? "Password" : "Password (min. 8 characters)"}
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

          {error && <p className="mt-4 text-center text-sm text-red-400">{error}</p>}
        </div>

        <p className="mt-6 text-center text-xs text-slate-500">
          By continuing you agree to the terms of service and privacy policy.
        </p>
      </div>
    </div>
  );
}
