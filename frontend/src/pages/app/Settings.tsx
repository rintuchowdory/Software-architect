import { useEffect, useState } from "react";
import { AlertCircle, Check, Copy, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { Card, PageHeader } from "@/components/ui/Card";
import { cn } from "@/lib/cn";

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
  hourly_rate: number;
  complete: boolean;
  missing: string[];
};

const EMTPY: Profile = {
  name: "",
  owner: "",
  address: "",
  email: "",
  phone: "",
  vat_id: "",
  tax_number: "",
  iban: "",
  bank: "",
  small_business: false,
  hourly_rate: 90,
  complete: false,
  missing: [],
};

const fieldMeta: { key: keyof Profile; label: string; hint?: string; type?: string; wide?: boolean }[] = [
  { key: "name", label: "Studio-Name", hint: "Erscheint oben auf jeder Rechnung" },
  { key: "owner", label: "Inhaber / Inhaberin", hint: "Pflichtangabe nach §14 UStG" },
  { key: "address", label: "Adresse", hint: "Straße, PLZ und Ort", wide: true },
  { key: "email", label: "E-Mail" },
  { key: "phone", label: "Telefon" },
  { key: "vat_id", label: "USt-IdNr", hint: "Alternativ Steuernummer angeben" },
  { key: "tax_number", label: "Steuernummer" },
  { key: "bank", label: "Bank" },
  { key: "iban", label: "IBAN" },
];

export default function Settings() {
  const [form, setForm] = useState<Profile>(EMTPY);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [copied, setCopied] = useState(false);
  const intakeUrl = `${window.location.origin}/intake`;

  useEffect(() => {
    api
      .get<Profile>("/studio/profile")
      .then((data) => setForm(data))
      .catch((e) => setError(e instanceof Error ? e.message : "Couldn't load your studio profile."))
      .finally(() => setLoading(false));
  }, []);

  function set<K extends keyof Profile>(key: K, value: Profile[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      const data = await api.put<Profile>("/studio/profile", form);
      setForm(data);
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save.");
    } finally {
      setSaving(false);
    }
  }

  async function copyIntake() {
    await navigator.clipboard.writeText(intakeUrl).catch(() => {});
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  }

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Studio settings"
        subtitle="What goes on every invoice. Nothing here leaves your own database."
      />

      {error && (
        <div className="mb-4 flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      <Card className="mb-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm font-semibold text-slate-100">
              {form.complete ? "Invoices are legally complete" : "Invoices are not complete yet"}
            </p>
            <p className="mt-1 text-sm text-slate-400">
              {form.complete
                ? "Every invoice you print carries the sender block, tax figure and payment details."
                : `Still missing: ${form.missing
                    .map((m) => fieldMeta.find((f) => f.key === m)?.label ?? m)
                    .join(", ")}.`}
            </p>
          </div>
          <span
            className={cn(
              "rounded-full px-3 py-1 text-xs font-semibold",
              form.complete
                ? "bg-signal-400/10 text-signal-400"
                : "bg-amber-400/10 text-amber-300"
            )}
          >
            {form.complete ? "Complete" : "Draft invoices only"}
          </span>
        </div>
      </Card>

      <form onSubmit={save}>
        <Card>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
            {fieldMeta.map((field) => (
              <label
                key={field.key}
                className={cn("block text-sm", field.wide && "sm:col-span-2")}
              >
                <span className="font-medium text-slate-300">{field.label}</span>
                {field.hint && <span className="mt-0.5 block text-xs text-slate-500">{field.hint}</span>}
                <input
                  type={field.key === "email" ? "email" : "text"}
                  value={String(form[field.key] ?? "")}
                  onChange={(e) => set(field.key, e.target.value as never)}
                  disabled={loading}
                  className="mt-1.5 w-full rounded-lg border border-white/10 bg-ink-900/70 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-signal-400/50 focus:ring-2 focus:ring-signal-400/20 disabled:opacity-50"
                />
              </label>
            ))}

            <label className="block text-sm">
              <span className="font-medium text-slate-300">Stundensatz (€)</span>
              <span className="mt-0.5 block text-xs text-slate-500">
                Grundlage für die Aufwandsschätzung im Intake
              </span>
              <input
                type="number"
                min={10}
                max={1000}
                value={form.hourly_rate}
                onChange={(e) => set("hourly_rate", Number(e.target.value))}
                disabled={loading}
                className="mt-1.5 w-full rounded-lg border border-white/10 bg-ink-900/70 px-3 py-2 text-sm text-slate-100 outline-none transition focus:border-signal-400/50 focus:ring-2 focus:ring-signal-400/20 disabled:opacity-50"
              />
            </label>

            <label className="flex items-start gap-3 rounded-lg border border-white/10 bg-ink-900/40 p-3 text-sm sm:col-span-2">
              <input
                type="checkbox"
                checked={form.small_business}
                onChange={(e) => set("small_business", e.target.checked)}
                disabled={loading}
                className="mt-0.5 h-4 w-4 accent-signal-400"
              />
              <span>
                <span className="font-medium text-slate-200">Kleinunternehmer (§19 UStG)</span>
                <span className="mt-0.5 block text-xs text-slate-500">
                  New invoices get 0 % VAT and the §19 note. Turn off if you charge VAT.
                </span>
              </span>
            </label>
          </div>

          <div className="mt-6 flex items-center gap-3">
            <button
              type="submit"
              disabled={saving || loading}
              className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-signal-500/20 transition hover:shadow-signal-500/35 disabled:opacity-60"
            >
              {saving && <Loader2 size={15} className="animate-spin" />}
              {saving ? "Saving…" : "Save settings"}
            </button>
            {saved && (
              <span className="inline-flex items-center gap-1.5 text-sm text-signal-400">
                <Check size={15} /> Saved
              </span>
            )}
          </div>
        </Card>
      </form>

      <Card className="mt-6">
        <p className="text-sm font-semibold text-slate-100">Your public intake link</p>
        <p className="mt-1 text-sm text-slate-400">
          Send this to a client. No login, three steps, and the brief lands in your projects.
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <code className="flex-1 overflow-x-auto rounded-lg border border-white/10 bg-ink-900/70 px-3 py-2 text-xs text-slate-300">
            {intakeUrl}
          </code>
          <button
            type="button"
            onClick={copyIntake}
            className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-slate-200 transition hover:border-white/20 hover:bg-white/5"
          >
            <Copy size={14} /> {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </Card>
    </div>
  );
}
