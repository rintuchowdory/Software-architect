import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export function CTASection() {
  return (
    <section className="border-t border-white/5 py-24">
      <div className="mx-auto max-w-5xl px-6">
        <div className="rounded-3xl bg-gradient-to-br from-signal-500 to-accent-500 px-8 py-14 text-center shadow-2xl shadow-signal-500/20 sm:px-16">
          <h2 className="font-display text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Ready to run projects this way?
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-white/80">
            Set up your first client intake in a few minutes — no credit card, no
            migration, just your next project.
          </p>
          <Link
            to="/login"
            className="mt-8 inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-ink-950 transition hover:bg-white/90"
          >
            Start your project
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>
    </section>
  );
}
