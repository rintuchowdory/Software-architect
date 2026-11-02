import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { CodeXml, ArrowRight, ArrowLeft, Check, Loader2, Copy, CheckCheck } from "lucide-react";
import { api } from "@/lib/api";

type Option = { value: string; label: string };
type Options = { project_types: Option[]; features: Option[]; timelines: Option[] };
type Result = {
  project_id: string;
  title: string;
  brief: string;
  hours: number;
  estimate_low: string;
  estimate_high: string;
};

const emptyForm = {
  project_type: "website",
  goal: "",
  features: [] as string[],
  timeline: "",
  budget: "",
  existing: "",
  notes: "",
  client_name: "",
  company: "",
  email: "",
  project_name: "",
};

export default function Intake() {
  const [options, setOptions] = useState<Options | null>(null);
  const [step, setStep] = useState(1);
  const [form, setForm] = useState(emptyForm);
  const [result, setResult] = useState<Result | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    api
      .get<Options>("/public/intake/options")
      .then(setOptions)
      .catch(() => setError("Could not load the form. Please reload the page."));
  }, []);

  const set = <K extends keyof typeof form>(key: K, value: (typeof form)[K]) =>
    setForm((prev) => ({ ...prev, [key]: value }));

  const toggleFeature = (value: string) =>
    setForm((prev) => ({
      ...prev,
      features: prev.features.includes(value)
        ? prev.features.filter((f) => f !== value)
        : [...prev.features, value],
    }));

  const step1Valid = form.goal.trim().length > 3;
  const step2Valid = form.timeline !== "";
  const step3Valid = /\S+@\S+\.\S+/.test(form.email);

  async function submit() {
    setBusy(true);
    setError(null);
    try {
      const res = await api.post<Result>("/public/intake", form);
      setResult(res);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-ink-950">
      <header className="border-b border-white/5">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-5">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-signal-400 to-accent-500 text-ink-950">
              <CodeXml size={18} strokeWidth={2.5} />
            </span>
            <span className="font-display text-[15px] font-semibold text-slate-100">Software Architect</span>
          </Link>
          <span className="text-xs text-slate-500">Projekt-Intake</span>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-12">
        {result ? (
          <BriefResult result={result} copied={copied} setCopied={setCopied} />
        ) : (
          <>
            <h1 className="font-display text-3xl font-bold tracking-tight text-slate-100">
              Erzähl mir von deinem Projekt
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-slate-400">
              Drei kurze Schritte, keine Anmeldung. Am Ende bekommst du eine erste Einschätzung
              zu Umfang, Aufwand und Kostenrahmen.
            </p>

            <ol className="mt-8 flex items-center gap-3 text-xs">
              {["Projekt", "Umfang", "Kontakt"].map((label, i) => {
                const index = i + 1;
                const active = step === index;
                const done = step > index;
                return (
                  <li key={label} className="flex items-center gap-2">
                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-semibold ${
                        done
                          ? "bg-signal-500 text-ink-950"
                          : active
                            ? "bg-signal-400/20 text-signal-300"
                            : "bg-white/5 text-slate-500"
                      }`}
                    >
                      {done ? <Check size={12} /> : index}
                    </span>
                    <span className={active ? "text-slate-200" : "text-slate-500"}>{label}</span>
                    {index < 3 && <span className="mx-1 h-px w-6 bg-white/10" />}
                  </li>
                );
              })}
            </ol>

            <div className="mt-8 rounded-2xl border border-white/5 bg-ink-800/60 p-6 sm:p-8">
              {error && (
                <div className="mb-5 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {error}
                </div>
              )}

              {step === 1 && (
                <div className="space-y-6">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">Was brauchst du?</label>
                    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                      {options?.project_types.map((type) => (
                        <button
                          key={type.value}
                          type="button"
                          onClick={() => set("project_type", type.value)}
                          className={`rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                            form.project_type === type.value
                              ? "border-signal-400/60 bg-signal-400/10 text-slate-100"
                              : "border-white/10 text-slate-400 hover:border-white/20 hover:text-slate-200"
                          }`}
                        >
                          {type.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label htmlFor="goal" className="mb-2 block text-sm font-medium text-slate-300">
                      Worum geht es? Zwei, drei Sätze reichen.
                    </label>
                    <textarea
                      id="goal"
                      value={form.goal}
                      onChange={(e) => set("goal", e.target.value)}
                      rows={4}
                      placeholder="Zum Beispiel: Ich verkaufe handgemachte Kerzen und brauche einen Shop, in dem Kunden direkt bestellen und bezahlen können."
                      className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none transition focus:border-signal-400/60"
                    />
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-6">
                  <div>
                    <label className="mb-2 block text-sm font-medium text-slate-300">
                      Was soll auf jeden Fall dabei sein?
                    </label>
                    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                      {options?.features.map((feature) => {
                        const active = form.features.includes(feature.value);
                        return (
                          <button
                            key={feature.value}
                            type="button"
                            onClick={() => toggleFeature(feature.value)}
                            className={`flex items-center justify-between rounded-lg border px-3 py-2.5 text-left text-sm transition ${
                              active
                                ? "border-signal-400/60 bg-signal-400/10 text-slate-100"
                                : "border-white/10 text-slate-400 hover:border-white/20 hover:text-slate-200"
                            }`}
                          >
                            {feature.label}
                            {active && <Check size={14} className="text-signal-400" />}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="timeline" className="mb-2 block text-sm font-medium text-slate-300">
                        Zeitrahmen
                      </label>
                      <select
                        id="timeline"
                        value={form.timeline}
                        onChange={(e) => set("timeline", e.target.value)}
                        className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                      >
                        <option value="">Bitte wählen</option>
                        {options?.timelines.map((t) => (
                          <option key={t.value} value={t.value}>
                            {t.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="budget" className="mb-2 block text-sm font-medium text-slate-300">
                        Budget-Vorstellung (optional)
                      </label>
                      <input
                        id="budget"
                        value={form.budget}
                        onChange={(e) => set("budget", e.target.value)}
                        placeholder="z. B. 3.000 – 5.000 €"
                        className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="existing" className="mb-2 block text-sm font-medium text-slate-300">
                      Was gibt es schon? (Texte, Logo, Fotos, Systeme)
                    </label>
                    <textarea
                      id="existing"
                      value={form.existing}
                      onChange={(e) => set("existing", e.target.value)}
                      rows={3}
                      className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                    />
                  </div>
                </div>
              )}

              {step === 3 && (
                <div className="space-y-5">
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                    <div>
                      <label htmlFor="client_name" className="mb-2 block text-sm font-medium text-slate-300">
                        Dein Name
                      </label>
                      <input
                        id="client_name"
                        value={form.client_name}
                        onChange={(e) => set("client_name", e.target.value)}
                        className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                      />
                    </div>
                    <div>
                      <label htmlFor="company" className="mb-2 block text-sm font-medium text-slate-300">
                        Firma (optional)
                      </label>
                      <input
                        id="company"
                        value={form.company}
                        onChange={(e) => set("company", e.target.value)}
                        className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                      />
                    </div>
                  </div>
                  <div>
                    <label htmlFor="email" className="mb-2 block text-sm font-medium text-slate-300">
                      E-Mail
                    </label>
                    <input
                      id="email"
                      type="email"
                      value={form.email}
                      onChange={(e) => set("email", e.target.value)}
                      className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                    />
                  </div>
                  <div>
                    <label htmlFor="notes" className="mb-2 block text-sm font-medium text-slate-300">
                      Noch etwas, das ich wissen sollte? (optional)
                    </label>
                    <textarea
                      id="notes"
                      value={form.notes}
                      onChange={(e) => set("notes", e.target.value)}
                      rows={3}
                      className="w-full rounded-lg border border-white/10 bg-ink-900 px-3 py-2.5 text-sm text-slate-200 outline-none focus:border-signal-400/60"
                    />
                  </div>
                </div>
              )}

              <div className="mt-8 flex items-center justify-between">
                <button
                  type="button"
                  onClick={() => setStep((s) => Math.max(1, s - 1))}
                  disabled={step === 1}
                  className="inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 transition enabled:hover:text-slate-200 disabled:opacity-40"
                >
                  <ArrowLeft size={15} />
                  Zurück
                </button>

                {step < 3 ? (
                  <button
                    type="button"
                    onClick={() => setStep((s) => Math.min(3, s + 1))}
                    disabled={(step === 1 && !step1Valid) || (step === 2 && !step2Valid)}
                    className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-5 py-2.5 text-sm font-semibold text-white transition enabled:hover:opacity-90 disabled:opacity-40"
                  >
                    Weiter
                    <ArrowRight size={15} />
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={submit}
                    disabled={!step3Valid || busy}
                    className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-5 py-2.5 text-sm font-semibold text-white transition enabled:hover:opacity-90 disabled:opacity-40"
                  >
                    {busy ? <Loader2 size={15} className="animate-spin" /> : <ArrowRight size={15} />}
                    Einschätzung erhalten
                  </button>
                )}
              </div>
            </div>

            <p className="mt-6 text-center text-xs text-slate-600">
              Deine Angaben werden nur für die Projektanfrage verwendet.
            </p>
          </>
        )}
      </main>
    </div>
  );
}

function BriefResult({
  result,
  copied,
  setCopied,
}: {
  result: Result;
  copied: boolean;
  setCopied: (v: boolean) => void;
}) {
  const blocks = useMemo(() => renderBrief(result.brief), [result.brief]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(result.brief);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div>
      <span className="inline-flex items-center gap-2 rounded-full border border-signal-400/20 bg-signal-400/10 px-3 py-1 text-xs font-medium text-signal-400">
        <Check size={12} />
        Anfrage angekommen
      </span>
      <h1 className="mt-5 font-display text-3xl font-bold tracking-tight text-slate-100">{result.title}</h1>
      <p className="mt-3 text-sm text-slate-400">
        Erste Einschätzung: rund <strong className="text-slate-200">{result.hours} Stunden</strong> Aufwand,
        Kostenrahmen <strong className="text-slate-200">{result.estimate_low}</strong> bis{" "}
        <strong className="text-slate-200">{result.estimate_high}</strong> netto. Verbindlich wird es nach
        einem kurzen Gespräch.
      </p>

      <div className="mt-8 rounded-2xl border border-white/5 bg-ink-800/60 p-6 sm:p-8">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-slate-400">
            Projekt-Brief
          </h2>
          <button
            onClick={copy}
            className="inline-flex items-center gap-1.5 rounded-lg border border-white/10 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:bg-white/5"
          >
            {copied ? <CheckCheck size={13} /> : <Copy size={13} />}
            {copied ? "Kopiert" : "Kopieren"}
          </button>
        </div>
        <div className="space-y-3 text-sm leading-relaxed">{blocks}</div>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <a
          href={`mailto:?subject=${encodeURIComponent(result.title)}&body=${encodeURIComponent(result.brief)}`}
          className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-signal-500 to-accent-500 px-5 py-2.5 text-sm font-semibold text-white"
        >
          Per E-Mail senden
          <ArrowRight size={15} />
        </a>
        <Link
          to="/"
          className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-5 py-2.5 text-sm font-semibold text-slate-200 transition hover:bg-white/5"
        >
          Zurück zur Startseite
        </Link>
      </div>
    </div>
  );
}

/** Tiny markdown renderer: headings, bullets, bold. No dependency needed. */
function renderBrief(markdown: string) {
  return markdown.split("\n").map((line, i) => {
    const key = `${i}-${line.slice(0, 12)}`;
    if (line.startsWith("# "))
      return (
        <h2 key={key} className="font-display text-lg font-bold text-slate-100">
          {line.slice(2)}
        </h2>
      );
    if (line.startsWith("## "))
      return (
        <h3 key={key} className="pt-3 text-xs font-semibold uppercase tracking-wide text-slate-400">
          {line.slice(3)}
        </h3>
      );
    if (line.startsWith("- ") || /^\d\. /.test(line))
      return (
        <p key={key} className="flex gap-2 text-slate-300">
          <span className="text-signal-400">•</span>
          <span>{stripBold(line.replace(/^-\s|^\d\.\s/, ""))}</span>
        </p>
      );
    if (line.trim() === "") return null;
    return (
      <p key={key} className="text-slate-300">
        {stripBold(line)}
      </p>
    );
  });
}

function stripBold(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith("**") && part.endsWith("**") ? (
      <strong key={i} className="font-semibold text-slate-100">
        {part.slice(2, -2)}
      </strong>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}
