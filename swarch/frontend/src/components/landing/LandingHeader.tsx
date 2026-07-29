import { Link } from "react-router-dom";
import { CodeXml } from "lucide-react";

export function LandingHeader() {
  return (
    <header className="fixed inset-x-0 top-0 z-50 glass border-b border-white/5">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
            <CodeXml size={18} strokeWidth={2.5} />
          </span>
          <span className="font-display text-[15px] font-semibold tracking-tight text-slate-100">
            Software Architect
          </span>
        </Link>
        <div className="flex items-center gap-3">
          <Link
            to="/login"
            className="hidden text-sm font-medium text-slate-300 transition hover:text-white sm:block"
          >
            Sign in
          </Link>
          <Link
            to="/login"
            className="rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-signal-500/20 transition hover:shadow-signal-500/40"
          >
            Start a project
          </Link>
        </div>
      </div>
    </header>
  );
}
