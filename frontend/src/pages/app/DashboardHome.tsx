import { Link } from "react-router-dom";
import { PageHeader, StatCard, Card } from "@/components/ui/Card";
import { BarChart } from "@/components/ui/BarChart";
import { useFetch } from "@/lib/useFetch";
import { AlertCircle, ArrowRight, CheckCircle2, Clock3, Euro, Send } from "lucide-react";

type Overview = {
  active_projects: number;
  pipeline_value: string;
  outstanding: string;
  paid_this_month: string;
  overdue_invoices: number;
  overdue_amount: string;
  new_leads: number;
  avg_project_value: string;
  billable_hours_estimate: number;
  revenue_series: { month: string; label: string; value: number }[];
  pipeline: { stage: string; count: number; value: string; value_raw: number }[];
  overdue: { id: string; number: string; project_name: string; client_name: string; total: string; days_overdue: number }[];
  actions: { id: string; title: string; detail: string; kind: string; href: string; priority: number }[];
};

const stageLabel: Record<string, string> = {
  intake: "Intake",
  quoted: "Quoted",
  in_progress: "In progress",
  delivered: "Delivered",
};

const actionIcon: Record<string, typeof Euro> = {
  money: Euro,
  sales: Send,
  delivery: Clock3,
};

export default function DashboardHome() {
  const { data, loading, error, refetch } = useFetch<Overview>("/dashboard/overview");

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="What the studio earned, what is owed, and what needs you today."
        action={
          <Link
            to="/intake"
            target="_blank"
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-signal-500/20 transition hover:shadow-signal-500/40"
          >
            Send intake link
            <ArrowRight size={15} />
          </Link>
        }
      />

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          Couldn't reach the backend: {error}.
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Paid this month"
          value={loading ? "—" : data?.paid_this_month ?? "0 €"}
          hint={data ? `Ø project ${data.avg_project_value}` : undefined}
        />
        <StatCard
          label="Outstanding"
          value={loading ? "—" : data?.outstanding ?? "0 €"}
          hint={data && data.overdue_invoices > 0 ? `${data.overdue_amount} of it overdue` : "All within terms"}
        />
        <StatCard
          label="Pipeline"
          value={loading ? "—" : data?.pipeline_value ?? "0 €"}
          hint={data ? `${data.active_projects} active, ${data.new_leads} new leads` : undefined}
        />
        <StatCard
          label="Billable in flight"
          value={loading ? "—" : `${data?.billable_hours_estimate ?? 0} h`}
          hint="Estimated from running projects"
        />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="mb-6 flex items-baseline justify-between">
            <div>
              <h2 className="font-display text-base font-semibold text-slate-100">Revenue</h2>
              <p className="mt-1 text-xs text-slate-500">Paid invoices, last six months, incl. VAT</p>
            </div>
            <span className="text-xs text-slate-500">{data ? data.revenue_series.length : 0} months</span>
          </div>
          <BarChart
            data={(data?.revenue_series ?? []).map((p) => ({ label: p.label, value: p.value }))}
            format={(v) => `${v.toLocaleString("de-DE")} €`}
          />
        </Card>

        <Card>
          <h2 className="font-display text-base font-semibold text-slate-100">Pipeline</h2>
          <p className="mt-1 text-xs text-slate-500">Value by stage</p>
          <div className="mt-5 space-y-4">
            {loading && <p className="text-sm text-slate-500">Loading…</p>}
            {data?.pipeline.map((stage) => {
              const max = Math.max(...data.pipeline.map((s) => s.value_raw), 1);
              return (
                <div key={stage.stage}>
                  <div className="mb-1.5 flex items-center justify-between text-xs">
                    <span className="text-slate-300">{stageLabel[stage.stage] ?? stage.stage}</span>
                    <span className="text-slate-500">
                      {stage.count} · {stage.value}
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-white/5">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-signal-500 to-accent-500"
                      style={{ width: `${Math.max((stage.value_raw / max) * 100, stage.value_raw > 0 ? 6 : 0)}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-base font-semibold text-slate-100">What needs you</h2>
            <button onClick={refetch} className="text-xs text-slate-500 transition hover:text-slate-300">
              Refresh
            </button>
          </div>

          {!loading && data?.actions.length === 0 && (
            <div className="flex items-center gap-2 py-6 text-sm text-slate-400">
              <CheckCircle2 size={16} className="text-emerald-400" />
              Nothing urgent. Everything is paid, quoted, or scoped.
            </div>
          )}

          <div className="divide-y divide-white/5">
            {data?.actions.map((action) => {
              const Icon = actionIcon[action.kind] ?? Clock3;
              return (
                <Link
                  key={action.id}
                  to={action.href}
                  className="flex items-start gap-3 py-3.5 transition hover:bg-white/[0.02]"
                >
                  <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/5 text-signal-400">
                    <Icon size={15} />
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-medium text-slate-200">{action.title}</span>
                    <span className="mt-0.5 block text-xs text-slate-500">{action.detail}</span>
                  </span>
                  <ArrowRight size={15} className="mt-2 shrink-0 text-slate-600" />
                </Link>
              );
            })}
          </div>
        </Card>

        <Card>
          <h2 className="font-display text-base font-semibold text-slate-100">Overdue</h2>
          <p className="mt-1 text-xs text-slate-500">
            {data ? `${data.overdue_invoices} invoice(s) · ${data.overdue_amount}` : " "}
          </p>
          <div className="mt-4 divide-y divide-white/5">
            {!loading && data?.overdue.length === 0 && (
              <p className="py-4 text-sm text-slate-500">Nothing overdue.</p>
            )}
            {data?.overdue.map((inv) => (
              <div key={inv.id} className="py-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-200">{inv.number || "—"}</span>
                  <span className="text-sm text-slate-300">{inv.total}</span>
                </div>
                <p className="mt-0.5 text-xs text-slate-500">
                  {inv.client_name} · {inv.days_overdue} days
                </p>
              </div>
            ))}
          </div>
          <Link
            to="/app/financials"
            className="mt-4 inline-flex items-center gap-1.5 text-xs font-medium text-signal-400 transition hover:text-signal-300"
          >
            Go to financials
            <ArrowRight size={13} />
          </Link>
        </Card>
      </div>
    </div>
  );
}
