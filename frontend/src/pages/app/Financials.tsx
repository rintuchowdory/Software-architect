import { useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader, Card, StatCard } from "@/components/ui/Card";
import { useFetch } from "@/lib/useFetch";
import { api } from "@/lib/api";
import { AlertCircle, Check, Printer, Send } from "lucide-react";

type Invoice = {
  id: string;
  number: string;
  project_name: string;
  client_name: string;
  amount: string;
  tax_rate: number;
  tax_amount: string;
  total: string;
  status: "draft" | "sent" | "paid" | "overdue";
  due_date: string;
  days_overdue: number;
};

type Summary = {
  outstanding: string;
  paid_this_month: string;
  overdue_count: number;
  overdue_amount: string;
};

const statusColor: Record<Invoice["status"], string> = {
  draft: "bg-white/5 text-slate-400",
  sent: "bg-warn-400/10 text-warn-400",
  paid: "bg-emerald-400/10 text-emerald-400",
  overdue: "bg-red-400/10 text-red-400",
};

export default function Financials() {
  const summary = useFetch<Summary>("/financials/summary");
  const invoices = useFetch<Invoice[]>("/financials/invoices");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function setStatus(invoice: Invoice, status: Invoice["status"]) {
    setBusyId(invoice.id);
    setError(null);
    try {
      await api.patch(`/financials/invoices/${invoice.id}`, { status });
      invoices.refetch();
      summary.refetch();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not update the invoice.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <div>
      <PageHeader
        title="Financials"
        subtitle="Invoices with sequential numbers, VAT breakdown, and a print view for the client."
      />

      {(summary.error || error) && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          {error ?? `Couldn't reach the backend: ${summary.error}.`}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard
          label="Outstanding"
          value={summary.loading ? "—" : summary.data?.outstanding ?? "0 €"}
          hint="Sent and overdue, incl. VAT"
        />
        <StatCard label="Paid this month" value={summary.loading ? "—" : summary.data?.paid_this_month ?? "0 €"} />
        <StatCard
          label="Overdue"
          value={summary.loading ? "—" : String(summary.data?.overdue_count ?? 0)}
          hint={summary.data?.overdue_amount}
        />
      </div>

      <Card className="mt-6 overflow-x-auto p-0">
        <table className="w-full min-w-[900px] text-left text-sm">
          <thead>
            <tr className="border-b border-white/5 text-xs uppercase tracking-wide text-slate-500">
              <th className="px-6 py-3.5 font-medium">Nr.</th>
              <th className="px-4 py-3.5 font-medium">Project</th>
              <th className="px-4 py-3.5 font-medium">Client</th>
              <th className="px-4 py-3.5 text-right font-medium">Net</th>
              <th className="px-4 py-3.5 text-right font-medium">VAT</th>
              <th className="px-4 py-3.5 text-right font-medium">Total</th>
              <th className="px-4 py-3.5 font-medium">Due</th>
              <th className="px-4 py-3.5 font-medium">Status</th>
              <th className="px-6 py-3.5 font-medium"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {invoices.loading && (
              <tr>
                <td colSpan={9} className="px-6 py-6 text-slate-500">Loading invoices…</td>
              </tr>
            )}
            {!invoices.loading && !invoices.error && invoices.data?.length === 0 && (
              <tr>
                <td colSpan={9} className="px-6 py-6 text-slate-500">No invoices yet.</td>
              </tr>
            )}
            {invoices.data?.map((inv) => (
              <tr key={inv.id} className="transition hover:bg-white/[0.02]">
                <td className="px-6 py-3.5 font-mono text-xs text-slate-400">{inv.number || "—"}</td>
                <td className="px-4 py-3.5 font-medium text-slate-200">{inv.project_name}</td>
                <td className="px-4 py-3.5 text-slate-400">{inv.client_name}</td>
                <td className="px-4 py-3.5 text-right text-slate-400">{inv.amount}</td>
                <td className="px-4 py-3.5 text-right text-slate-500">
                  {inv.tax_amount} <span className="text-[11px]">({inv.tax_rate}%)</span>
                </td>
                <td className="px-4 py-3.5 text-right font-medium text-slate-200">{inv.total}</td>
                <td className="px-4 py-3.5 text-slate-400">
                  {inv.due_date}
                  {inv.days_overdue > 0 && (
                    <span className="ml-2 text-[11px] text-red-400">+{inv.days_overdue}d</span>
                  )}
                </td>
                <td className="px-4 py-3.5">
                  <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusColor[inv.status]}`}>
                    {inv.status}
                  </span>
                </td>
                <td className="px-6 py-3.5">
                  <div className="flex items-center justify-end gap-1.5">
                    {inv.status === "draft" && (
                      <button
                        onClick={() => setStatus(inv, "sent")}
                        disabled={busyId === inv.id}
                        title="Mark as sent"
                        className="rounded-md border border-white/10 p-1.5 text-slate-400 transition hover:text-signal-400 disabled:opacity-40"
                      >
                        <Send size={14} />
                      </button>
                    )}
                    {inv.status !== "paid" && (
                      <button
                        onClick={() => setStatus(inv, "paid")}
                        disabled={busyId === inv.id}
                        title="Mark as paid"
                        className="rounded-md border border-white/10 p-1.5 text-slate-400 transition hover:text-emerald-400 disabled:opacity-40"
                      >
                        <Check size={14} />
                      </button>
                    )}
                    <Link
                      to={`/app/financials/${inv.id}`}
                      title="Open printable invoice"
                      className="rounded-md border border-white/10 p-1.5 text-slate-400 transition hover:text-signal-400"
                    >
                      <Printer size={14} />
                    </Link>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}
