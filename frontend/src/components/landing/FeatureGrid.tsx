import { Layers, MessageSquare, ReceiptText, ShieldCheck, LineChart, Users, Workflow, Sparkles } from "lucide-react";
import type { ComponentType } from "react";

type Feature = {
  icon: ComponentType<{ size?: number; strokeWidth?: number }>;
  title: string;
  body: string;
};

const features: Feature[] = [
  {
    icon: Layers,
    title: "Guided intake",
    body: "A structured questionnaire turns a client's rough idea into a scoped, buildable brief before you ever quote it.",
  },
  {
    icon: MessageSquare,
    title: "One thread per project",
    body: "Every client message, file, and decision lives on the project timeline — no more digging through email.",
  },
  {
    icon: ReceiptText,
    title: "Quotes & invoices",
    body: "Turn a brief into a line-itemed quote in minutes, then bill milestones as the build progresses.",
  },
  {
    icon: ShieldCheck,
    title: "Stripe-backed payments",
    body: "Deposits and milestone payments go through Stripe, with status synced back to the project automatically.",
  },
  {
    icon: LineChart,
    title: "Studio-wide reporting",
    body: "Pipeline value, overdue invoices, and delivery velocity in one view — know the health of the studio at a glance.",
  },
  {
    icon: Users,
    title: "Client portal",
    body: "Clients get a clean, branded view of their project's status, files, and invoices — without a login of their own to manage.",
  },
  {
    icon: Workflow,
    title: "Automations",
    body: "Auto-move projects between stages, chase overdue invoices, and notify clients on milestone changes.",
  },
  {
    icon: Sparkles,
    title: "AI project analysis",
    body: "Generate a technical brief and a ready-to-paste build prompt from the intake answers in one click.",
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
            collapsed into one.
          </p>
        </div>
        <div className="mt-16 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-white/5 bg-ink-800/60 p-6 transition hover:border-signal-400/20"
            >
              <span className="mb-5 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
                <f.icon size={18} strokeWidth={2.25} />
              </span>
              <h3 className="font-display text-base font-semibold text-slate-100">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{f.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
