import {
  Layers,
  ReceiptText,
  ShieldCheck,
  LineChart,
  Printer,
  ClipboardCheck,
  CreditCard,
  Users,
} from "lucide-react";
import type { ComponentType } from "react";

type Feature = {
  icon: ComponentType<{ size?: number; strokeWidth?: number }>;
  title: string;
  body: string;
  status: "live" | "soon";
};

const features: Feature[] = [
  {
    icon: Layers,
    title: "Guided client intake",
    body: "A public link asks the right questions in three steps. The client never sees a login, you never type their answers twice.",
    status: "live",
  },
  {
    icon: ClipboardCheck,
    title: "Brief with an estimate",
    body: "Answers become a scoped brief with deliverables, exclusions, hours and a price range. Regenerate it whenever the scope moves.",
    status: "live",
  },
  {
    icon: ReceiptText,
    title: "Invoices that hold up",
    body: "Sequential numbers per year, net/VAT/gross breakdown, §19 UStG support for small businesses. No spreadsheet gymnastics.",
    status: "live",
  },
  {
    icon: Printer,
    title: "Print-ready invoice",
    body: "One click gives you a clean A4 invoice in the browser, ready to save as PDF and send to the client.",
    status: "live",
  },
  {
    icon: LineChart,
    title: "Dashboard that acts",
    body: "Six-month revenue, pipeline by stage, and a prioritised list of what needs you: chase this invoice, scope that project.",
    status: "live",
  },
  {
    icon: ShieldCheck,
    title: "Single source of truth",
    body: "Clients, projects, briefs and invoices on one record, so a question about a project never means digging through email.",
    status: "live",
  },
  {
    icon: CreditCard,
    title: "Deposits via Stripe",
    body: "Take a deposit when the quote is accepted and let the project move to In progress on its own.",
    status: "soon",
  },
  {
    icon: Users,
    title: "Client portal",
    body: "A branded, no-login view of project status, files and invoices, so clients stop asking for updates.",
    status: "soon",
  },
];

export function FeatureGrid() {
  return (
    <section className="border-t border-white/5 bg-ink-900/60 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">
            Everything between "yes" and "shipped"
          </h2>
          <p className="mt-4 text-slate-400">
            The parts of running a studio that usually live in five different tools,
            collapsed into one. What is live today, and what is being built next.
          </p>
        </div>
        <div className="mt-16 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="relative rounded-2xl border border-white/5 bg-ink-800/60 p-6 transition hover:border-signal-400/20"
            >
              <span className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
                <f.icon size={18} strokeWidth={2.25} />
              </span>
              <div className="flex items-center gap-2">
                <h3 className="font-display text-base font-semibold text-slate-100">{f.title}</h3>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{f.body}</p>
              <span
                className={`mt-4 inline-block rounded-full px-2 py-0.5 text-[11px] font-medium ${
                  f.status === "live"
                    ? "bg-emerald-400/10 text-emerald-400"
                    : "bg-warn-400/10 text-warn-400"
                }`}
              >
                {f.status === "live" ? "Live" : "In progress"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
