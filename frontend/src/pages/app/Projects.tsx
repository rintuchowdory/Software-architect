import { PageHeader, Card } from "@/components/ui/Card";
import { useFetch } from "@/lib/useFetch";
import { AlertCircle } from "lucide-react";

type Project = {
  id: string;
  name: string;
  client_name: string;
  stage: "intake" | "quoted" | "in_progress" | "delivered";
  budget: string;
};

const columns: { key: Project["stage"]; label: string }[] = [
  { key: "intake", label: "Intake" },
  { key: "quoted", label: "Quoted" },
  { key: "in_progress", label: "In progress" },
  { key: "delivered", label: "Delivered" },
];

export default function Projects() {
  const { data: projects, loading, error } = useFetch<Project[]>("/projects");

  return (
    <div>
      <PageHeader title="Projects" subtitle="Every brief, from intake through delivery." />

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          Couldn't reach the backend: {error}.
        </div>
      )}

      {loading && <p className="text-sm text-slate-500">Loading projects…</p>}

      {!loading && !error && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {columns.map((col) => {
            const items = projects?.filter((p: Project) => p.stage === col.key) ?? [];
            return (
              <div key={col.key}>
                <div className="mb-3 flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-slate-300">{col.label}</h3>
                  <span className="text-xs text-slate-500">{items.length}</span>
                </div>
                <div className="space-y-3">
                  {items.length === 0 && (
                    <p className="rounded-xl border border-dashed border-white/10 px-4 py-6 text-center text-xs text-slate-600">
                      Nothing here
                    </p>
                  )}
                  {items.map((p: Project) => (
                    <Card key={p.id} className="p-4">
                      <p className="text-sm font-medium text-slate-200">{p.name}</p>
                      <p className="mt-1 text-xs text-slate-500">{p.client_name}</p>
                      <p className="mt-3 text-sm font-semibold text-signal-400">{p.budget}</p>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
