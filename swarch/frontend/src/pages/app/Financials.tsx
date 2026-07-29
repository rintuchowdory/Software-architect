import { PageHeader, Card, StatCard } from "@/components/ui/Card";
import { useFetch } from "@/lib/useFetch";
import { AlertCircle } from "lucide-react";

type Invoice = {
  id: string;
  project_name: string;
  client_name: string;
  amount: string;
  status: "draft" | "sent" | "paid" | "overdue";
  due_date: string;
};

type Summary = { outstanding: string; paid_this_month: string; overdue_count: number };

const statusColor: Record<Invoice["status"], string> = {
  draft: "bg-white/5 text-slate-400",
  sent: "bg-warn-400/10 text-warn-400",
  paid: "bg-emerald-400/10 text-emerald-400",
  overdue: "bg-red-400/10 text-red-400",
};

export default function Financials() {
  const { data: summary, loading: summaryLoading, error: summaryError } = useFetch<Summary>("/financials/summary");
  const { data: invoices, loading, error } = useFetch<Invoice[]>("/financials/invoices");

  return (
    <div>
      <PageHeader title="Financials" subtitle="Quotes, invoices, and where the studio's money stands." />

      {summaryError && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          Couldn't reach the backend: {summaryError}.
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Outstanding" value={summaryLoading ? "—" : summary?.outstanding ?? "$0"} />
        <StatCard label="Paid this month" value={summaryLoading ? "—" : summary?.paid_this_month ?? "$0"} />
        <StatCard label="Overdue invoices" value={summaryLoading ? "—" : String(summary?.overdue_count ?? 0)} />
      </div>

      <Card className="mt-6 p-0">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-white/5 text-xs uppercase tracking-wide text-slate-500">
              <th className="px-6 py-3.5 font-medium">Project</th>
              <th className="px-6 py-3.5 font-medium">Client</th>
              <th className="px-6 py-3.5 font-medium">Amount</th>
              <th className="px-6 py-3.5 font-medium">Due</th>
              <th className="px-6 py-3.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {loading && (
              <tr><td colSpan={5} className="px-6 py-6 text-slate-500">Loading invoices…</td></tr>
            )}
            {!loading && !error && invoices?.length === 0 && (
              <tr><td colSpan={5} className="px-6 py-6 text-slate-500">No invoices yet.</td></tr>
            )}
            {error && (
              <tr><td colSpan={5} className="px-6 py-6 text-red-300">Couldn't load invoices: {error}</td></tr>
            )}
            {invoices?.map((inv: Invoice) => (
              <tr key={inv.id}>
                <td className="px-6 py-3.5 font-medium text-slate-200">{inv.project_name}</td>
                <td className="px-6 py-3.5 text-slate-400">{inv.client_name}</td>
                <td className="px-6 py-3.5 text-slate-200">{inv.amount}</td>
                <td className="px-6 py-3.5 text-slate-400">{inv.due_date}</td>
                <td className="px-6 py-3.5">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusColor[inv.status]}`}>
                    {inv.status}
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
