import { PageHeader, StatCard, Card } from "@/components/ui/Card";
import { useFetch } from "@/lib/useFetch";
import { AlertCircle } from "lucide-react";

type Stats = {
  active_projects: number;
  pipeline_value: string;
  overdue_invoices: number;
  new_leads: number;
};

type ProjectSummary = {
  id: string;
  name: string;
  client_name: string;
  stage: string;
  budget: string;
};

const stageColor: Record<string, string> = {
  intake: "text-slate-400 bg-white/5",
  quoted: "text-warn-400 bg-warn-400/10",
  in_progress: "text-signal-400 bg-signal-400/10",
  delivered: "text-emerald-400 bg-emerald-400/10",
};

export default function DashboardHome() {
  const { data: stats, loading: statsLoading, error: statsError } = useFetch<Stats>("/dashboard/stats");
  const { data: projects, loading: projectsLoading, error: projectsError } =
    useFetch<ProjectSummary[]>("/projects?limit=5");

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Studio-wide snapshot, updated in real time." />

      {statsError && <ApiErrorBanner message={statsError} />}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Active projects" value={statsLoading ? "—" : String(stats?.active_projects ?? 0)} />
        <StatCard label="Pipeline value" value={statsLoading ? "—" : stats?.pipeline_value ?? "$0"} />
        <StatCard
          label="Overdue invoices"
          value={statsLoading ? "—" : String(stats?.overdue_invoices ?? 0)}
          hint={stats && stats.overdue_invoices > 0 ? "Needs a follow-up" : undefined}
        />
        <StatCard label="New leads (7d)" value={statsLoading ? "—" : String(stats?.new_leads ?? 0)} />
      </div>

      <Card className="mt-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-base font-semibold text-slate-100">Recent projects</h2>
        </div>

        {projectsError && <ApiErrorBanner message={projectsError} />}

        {!projectsError && (
          <div className="divide-y divide-white/5">
            {projectsLoading && <p className="py-6 text-sm text-slate-500">Loading projects…</p>}
            {!projectsLoading && projects?.length === 0 && (
              <p className="py-6 text-sm text-slate-500">No projects yet — new intakes will show up here.</p>
            )}
            {projects?.map((p: ProjectSummary) => (
              <div key={p.id} className="flex items-center justify-between py-3.5">
                <div>
                  <p className="text-sm font-medium text-slate-200">{p.name}</p>
                  <p className="text-xs text-slate-500">{p.client_name}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-slate-400">{p.budget}</span>
                  <span
                    className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${stageColor[p.stage] ?? "bg-white/5 text-slate-400"}`}
                  >
                    {p.stage.replace("_", " ")}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}

function ApiErrorBanner({ message }: { message: string }) {
  return (
    <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
      <AlertCircle size={16} />
      Couldn't reach the backend: {message}. Is the API running?
    </div>
  );
}
