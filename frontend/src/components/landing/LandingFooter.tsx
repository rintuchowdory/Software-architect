import { Link } from "react-router-dom";
import { CodeXml } from "lucide-react";

export function LandingFooter() {
  return (
    <footer className="border-t border-white/5 py-10">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 sm:flex-row">
        <div className="flex items-center gap-2">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
            <CodeXml size={14} strokeWidth={2.5} />
          </span>
          <span className="font-display text-sm font-semibold text-slate-200">Software Architect</span>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-5 text-xs text-slate-500">
          <Link to="/impressum" className="transition hover:text-slate-300">Impressum</Link>
          <Link to="/datenschutz" className="transition hover:text-slate-300">Datenschutz</Link>
          <Link to="/agb" className="transition hover:text-slate-300">AGB</Link>
          <Link to="/intake" className="transition hover:text-slate-300">Intake</Link>
        </div>
        <p className="text-xs text-slate-500">© {new Date().getFullYear()} Software Architect</p>
      </div>
    </footer>
  );
}
