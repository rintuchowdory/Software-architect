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
        <p className="text-xs text-slate-500">© {new Date().getFullYear()} Software Architect. All rights reserved.</p>
      </div>
    </footer>
  );
}
