import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CodeXml, ArrowRight } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function Login() {
  const { login, loading, error } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    try {
      await login(email, password);
      navigate("/app");
    } catch {
      // error is surfaced via auth context
    }
  }

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
          <h1 className="font-display text-xl font-semibold text-slate-100">Sign in</h1>
          <p className="mt-1 text-sm text-slate-400">
            Use any email and password — this build runs against the demo backend.
          </p>

          <form onSubmit={onSubmit} className="mt-6 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@studio.com"
                className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-signal-400/50"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium text-slate-300">Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-100 outline-none placeholder:text-slate-500 focus:border-signal-400/50"
              />
            </div>

            {error && <p className="text-sm text-red-400">{error}</p>}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-signal-500/20 transition hover:shadow-signal-500/40 disabled:opacity-60"
            >
              {loading ? "Signing in…" : "Sign in"}
              {!loading && <ArrowRight size={16} />}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
