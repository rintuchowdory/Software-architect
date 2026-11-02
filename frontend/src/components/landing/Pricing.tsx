import { Link } from "react-router-dom";
import { Check } from "lucide-react";

const tiers = [
  {
    name: "Solo",
    price: "19 €",
    tagline: "One person, all the basics",
    features: [
      "Unlimited clients and projects",
      "Public intake link with automatic brief",
      "Invoices with sequential numbers and VAT",
      "Print-ready A4 invoice / PDF",
      "Six-month revenue dashboard",
    ],
    cta: "Start free",
    highlight: false,
  },
  {
    name: "Studio",
    price: "39 €",
    tagline: "When someone else quotes too",
    features: [
      "Everything in Solo",
      "3 seats",
      "Invoice status automation and reminders",
      "Client portal (in progress)",
      "Priority support",
    ],
    cta: "Start free",
    highlight: true,
  },
  {
    name: "Agency",
    price: "79 €",
    tagline: "Small team, bigger pipeline",
    features: [
      "Everything in Studio",
      "10 seats and role permissions",
      "Custom domain for the intake form",
      "API access",
      "Onboarding call",
    ],
    cta: "Talk to us",
    highlight: false,
  },
];

export function Pricing() {
  return (
    <section id="pricing" className="border-t border-white/5 bg-ink-900/60 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Pricing</h2>
          <p className="mt-4 text-slate-400">
            Flat monthly price, no per-invoice fees, cancel any time. Prices exclude VAT.
          </p>
          <span className="mt-4 inline-block rounded-full border border-signal-400/20 bg-signal-400/10 px-3 py-1 text-xs font-medium text-signal-400">
            Beta: everything is free while billing is being finished
          </span>
        </div>

        <div className="mt-14 grid grid-cols-1 gap-6 lg:grid-cols-3">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`flex flex-col rounded-2xl border p-7 ${
                tier.highlight
                  ? "border-signal-400/40 bg-ink-800 shadow-xl shadow-signal-500/10"
                  : "border-white/5 bg-ink-800/60"
              }`}
            >
              {tier.highlight && (
                <span className="mb-3 w-fit rounded-full bg-signal-400/15 px-2.5 py-0.5 text-[11px] font-semibold text-signal-400">
                  Most popular
                </span>
              )}
              <h3 className="font-display text-lg font-semibold text-slate-100">{tier.name}</h3>
              <p className="mt-1 text-sm text-slate-500">{tier.tagline}</p>
              <p className="mt-5 font-display text-4xl font-bold text-slate-100">
                {tier.price}
                <span className="ml-1 text-sm font-normal text-slate-500">/ month</span>
              </p>
              <ul className="mt-6 flex-1 space-y-3 text-sm">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex gap-2 text-slate-300">
                    <Check size={15} className="mt-0.5 shrink-0 text-signal-400" />
                    {feature}
                  </li>
                ))}
              </ul>
              <Link
                to="/login"
                className={`mt-7 rounded-lg px-4 py-2.5 text-center text-sm font-semibold transition ${
                  tier.highlight
                    ? "bg-gradient-to-r from-signal-500 to-accent-500 text-white hover:opacity-90"
                    : "border border-white/10 text-slate-200 hover:bg-white/5"
                }`}
              >
                {tier.cta}
              </Link>
            </div>
          ))}
        </div>

        <p className="mt-8 text-center text-xs text-slate-500">
          Self-hosted? The whole thing is open source under rintuchowdory/Software-architect.
        </p>
      </div>
    </section>
  );
}
