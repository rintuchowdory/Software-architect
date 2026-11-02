import { Link, useParams } from "react-router-dom";
import { useFetch } from "@/lib/useFetch";
import { AlertCircle, ArrowLeft, Printer } from "lucide-react";

type Invoice = {
  id: string;
  number: string;
  project_name: string;
  client_name: string;
  client_company: string;
  client_email: string;
  amount: string;
  tax_rate: number;
  tax_amount: string;
  total: string;
  status: string;
  due_date: string;
  created_date: string;
  paid_at: string;
  notes: string;
};

type Profile = {
  name: string;
  owner: string;
  address: string;
  email: string;
  phone: string;
  vat_id: string;
  tax_number: string;
  iban: string;
  bank: string;
  small_business: boolean;
  complete: boolean;
};

function deDate(value: string) {
  if (!value) return "";
  // Accepts ISO (2026-11-02) and returns the German convention (02.11.2026).
  const [y, m, d] = value.split("-");
  return y && m && d ? `${d}.${m}.${y}` : value;
}

export default function InvoiceDetail() {
  const { id } = useParams();
  const invoice = useFetch<Invoice>(`/financials/invoices/${id}`);
  const profile = useFetch<Profile>("/studio/profile");

  if (invoice.error) {
    return (
      <div className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
        <AlertCircle size={16} />
        Couldn't load the invoice: {invoice.error}
      </div>
    );
  }

  const inv = invoice.data;
  const p = profile.data;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3 print:hidden">
        <Link
          to="/app/financials"
          className="inline-flex items-center gap-2 text-sm font-medium text-slate-400 transition hover:text-slate-200"
        >
          <ArrowLeft size={15} />
          Back to financials
        </Link>
        <div className="flex items-center gap-2">
          {p && !p.complete && (
            <span className="rounded-lg border border-warn-400/20 bg-warn-400/10 px-3 py-1.5 text-xs text-warn-400">
              Add your studio address to make this a valid invoice
            </span>
          )}
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-4 py-2 text-sm font-semibold text-white"
          >
            <Printer size={15} />
            Print / PDF
          </button>
        </div>
      </div>

      {!inv && <p className="text-sm text-slate-500">Loading invoice…</p>}

      {inv && (
        <article className="mx-auto max-w-3xl rounded-2xl bg-white p-10 text-slate-900 shadow-2xl print:rounded-none print:p-0 print:shadow-none">
          <header className="flex items-start justify-between border-b border-slate-200 pb-6">
            <div>
              <p className="text-lg font-bold">{p?.name ?? "Software Architect"}</p>
              <p className="mt-1 whitespace-pre-line text-xs leading-relaxed text-slate-600">
                {p?.owner && <>{p.owner}<br /></>}
                {p?.address ? p.address : "[Straße, PLZ Ort]"}
                {p?.email && <><br />{p.email}</>}
                {p?.phone && <><br />{p.phone}</>}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs uppercase tracking-wide text-slate-500">Rechnung</p>
              <p className="mt-1 font-mono text-sm font-semibold">{inv.number || "—"}</p>
              <p className="mt-1 text-xs text-slate-500">Datum: {deDate(inv.created_date)}</p>
              {inv.due_date && <p className="text-xs text-slate-500">Fällig: {deDate(inv.due_date)}</p>}
            </div>
          </header>

          <section className="mt-8">
            <p className="text-xs uppercase tracking-wide text-slate-500">Rechnung an</p>
            <p className="mt-1 text-sm font-semibold">
              {inv.client_company || inv.client_name}
            </p>
            <p className="whitespace-pre-line text-xs text-slate-600">
              {inv.client_company && <>{inv.client_name}<br /></>}
              {inv.client_email}
            </p>
          </section>

          <table className="mt-8 w-full text-left text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-xs uppercase tracking-wide text-slate-500">
                <th className="py-2 font-medium">Position</th>
                <th className="py-2 text-right font-medium">Betrag</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-100">
                <td className="py-3">
                  {inv.project_name}
                  {inv.notes && <span className="block text-xs text-slate-500">{inv.notes}</span>}
                </td>
                <td className="py-3 text-right">{inv.amount}</td>
              </tr>
            </tbody>
          </table>

          <div className="mt-4 ml-auto w-full max-w-xs space-y-1 text-sm">
            <div className="flex justify-between text-slate-600">
              <span>Netto</span>
              <span>{inv.amount}</span>
            </div>
            <div className="flex justify-between text-slate-600">
              <span>zzgl. {inv.tax_rate} % USt.</span>
              <span>{inv.tax_amount}</span>
            </div>
            <div className="flex justify-between border-t border-slate-200 pt-1 font-semibold">
              <span>Gesamt</span>
              <span>{inv.total}</span>
            </div>
          </div>

          <footer className="mt-10 space-y-2 border-t border-slate-200 pt-4 text-xs text-slate-600">
            <p>
              Zahlbar innerhalb von 14 Tagen ohne Abzug
              {p?.iban ? ` auf das Konto ${p.iban}${p.bank ? ` (${p.bank})` : ""}.` : "."}
            </p>
            <p>Bitte die Rechnungsnummer {inv.number} als Verwendungszweck angeben.</p>
            {p?.small_business && (
              <p>Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.</p>
            )}
            <p className="pt-2 text-[11px] text-slate-500">
              {p?.tax_number && <>Steuernummer: {p.tax_number} · </>}
              {p?.vat_id && <>USt-IdNr.: {p.vat_id}</>}
            </p>
          </footer>
        </article>
      )}

      {inv?.status === "paid" && inv.paid_at && (
        <p className="mt-4 text-center text-xs text-emerald-400 print:hidden">
          Marked paid on {deDate(inv.paid_at)}
        </p>
      )}
    </div>
  );
}
