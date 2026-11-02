const steps = [
  {
    n: "01",
    title: "Client fills the intake",
    body: "You send one link. Three short steps capture the goal, the features, the timeline and the budget range.",
  },
  {
    n: "02",
    title: "A brief lands in your studio",
    body: "The answers become a lead, a project in Intake, and a scoped brief with hours and a price range.",
  },
  {
    n: "03",
    title: "Quote, then invoice",
    body: "Move the project to Quoted, send the offer, and raise an invoice with a sequential number and VAT breakdown.",
  },
  {
    n: "04",
    title: "Watch the numbers, not the inbox",
    body: "The dashboard shows what was paid, what is outstanding, and which invoice to chase today.",
  },
];

export function Process() {
  return (
    <section id="how-it-works" className="border-t border-white/5 py-24">
      <div className="mx-auto max-w-6xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">How it works</h2>
          <p className="mt-4 text-slate-400">
            Four stages, one project record, and every one of them works today.
          </p>
        </div>
        <ol className="mt-16 grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
          {steps.map((s, i) => (
            <li key={s.n} className="relative">
              <span className="font-mono text-sm text-signal-400/60">{s.n}</span>
              <h3 className="mt-3 font-display text-lg font-semibold text-slate-100">{s.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-slate-400">{s.body}</p>
              {i < steps.length - 1 && (
                <span className="absolute right-[-1.25rem] top-1 hidden h-px w-8 bg-white/10 lg:block" />
              )}
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
