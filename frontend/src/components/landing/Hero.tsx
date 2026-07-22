import { Link } from "react-router-dom";
import { ArrowRight, Sparkles } from "lucide-react";

export function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute inset-0 grid-fade" />
      <div className="relative mx-auto max-w-5xl px-6 pb-28 pt-40 text-center sm:pt-48">
        <div className="mx-auto mb-8 inline-flex items-center gap-2 rounded-full border border-signal-400/20 bg-signal-400/10 px-4 py-1.5 text-sm font-medium text-signal-400">
          <Sparkles size={14} />
          One inbox from lead to invoice
        </div>
        <h1 className="font-display text-5xl font-bold leading-[1.05] tracking-tight sm:text-6xl lg:text-7xl">
          Run your dev studio
          <br />
          <span className="text-gradient-signal">without the spreadsheets</span>
        </h1>
        <p className="mx-auto mt-7 max-w-2xl text-lg leading-relaxed text-slate-400 sm:text-xl">
          A guided intake turns a client's idea into a scoped brief. You send a quote,
          collect the deposit, and track the build — all from one dashboard built for
          solo studios and small agencies.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            to="/login"
            className="group inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-signal-500/25 transition hover:shadow-signal-500/40"
          >
            Start your project
            <ArrowRight size={16} className="transition group-hover:translate-x-0.5" />
          </Link>
          <a
            href="#how-it-works"
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-6 py-3 text-sm font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/5"
          >
            See how it works
          </a>
        </div>
      </div>
    </section>
  );
}
