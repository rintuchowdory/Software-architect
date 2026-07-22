import { useState, type FormEvent } from "react";
import { PageHeader, Card } from "@/components/ui/Card";
import { useFetch } from "@/lib/useFetch";
import { api } from "@/lib/api";
import { Plus, AlertCircle } from "lucide-react";

type Client = {
  id: string;
  name: string;
  company: string;
  email: string;
  status: "lead" | "active" | "past";
};

const statusColor: Record<Client["status"], string> = {
  lead: "bg-warn-400/10 text-warn-400",
  active: "bg-signal-400/10 text-signal-400",
  past: "bg-white/5 text-slate-400",
};

export default function Clients() {
  const { data: clients, loading, error, refetch } = useFetch<Client[]>("/clients");
  const [showForm, setShowForm] = useState(false);

  return (
    <div>
      <PageHeader
        title="Clients"
        subtitle="Everyone who has come through an intake — leads, active, and past."
        action={
          <button
            onClick={() => setShowForm((v) => !v)}
            className="flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-signal-500/20"
          >
            <Plus size={16} />
            New client
          </button>
        }
      />

      {showForm && <NewClientForm onCreated={() => { setShowForm(false); refetch(); }} />}

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          Couldn't reach the backend: {error}.
        </div>
      )}

      <Card className="p-0">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-white/5 text-xs uppercase tracking-wide text-slate-500">
              <th className="px-6 py-3.5 font-medium">Name</th>
              <th className="px-6 py-3.5 font-medium">Company</th>
              <th className="px-6 py-3.5 font-medium">Email</th>
              <th className="px-6 py-3.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading && (
              <tr>
                <td colSpan={4} className="px-6 py-6 text-slate-500">Loading clients…</td>
              </tr>
            )}
            {!loading && clients?.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-6 text-slate-500">No clients yet — add your first one above.</td>
              </tr>
            )}
            {clients?.map((c: Client) => (
              <tr key={c.id}>
                <td className="px-6 py-3.5 font-medium text-slate-200">{c.name}</td>
                <td className="px-6 py-3.5 text-slate-400">{c.company}</td>
                <td className="px-6 py-3.5 text-slate-400">{c.email}</td>
                <td className="px-6 py-3.5">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusColor[c.status]}`}>
                    {c.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

function NewClientForm({ onCreated }: { onCreated: () => void }) {
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      await api.post("/clients", { name, company, email });
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create client");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card className="mb-6">
      <form onSubmit={onSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <input
          required
          placeholder="Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-signal-400/50"
        />
        <input
          placeholder="Company"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          className="rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-signal-400/50"
        />
        <input
          required
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-100 outline-none focus:border-signal-400/50"
        />
        {error && <p className="col-span-full text-sm text-red-400">{error}</p>}
        <button
          disabled={submitting}
          className="col-span-full justify-self-start rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
        >
          {submitting ? "Saving…" : "Save client"}
        </button>
      </form>
    </Card>
  );
}
