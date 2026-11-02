import { Link } from "react-router-dom";
import { CodeXml, ArrowLeft } from "lucide-react";

type PageKey = "impressum" | "datenschutz" | "agb";

const titles: Record<PageKey, string> = {
  impressum: "Impressum",
  datenschutz: "Datenschutz",
  agb: "AGB",
};

export default function Legal({ page }: { page: PageKey }) {
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
          <Link
            to="/"
            className="inline-flex items-center gap-1.5 text-sm text-slate-400 transition hover:text-slate-200"
          >
            <ArrowLeft size={14} />
            Zurück
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-3xl px-6 py-14">
        <h1 className="font-display text-3xl font-bold tracking-tight text-slate-100">{titles[page]}</h1>

        {page !== "datenschutz" && (
          <div className="mt-6 rounded-xl border border-warn-400/20 bg-warn-400/10 px-4 py-3 text-sm text-warn-400">
            Entwurf. Diese Seite ist ein Gerüst und muss vor dem Livegang anwaltlich geprüft und mit
            deinen echten Daten gefüllt werden.
          </div>
        )}

        <div className="mt-8 space-y-6 text-sm leading-relaxed text-slate-300">
          {page === "impressum" && <Impressum />}
          {page === "datenschutz" && <Datenschutz />}
          {page === "agb" && <Agb />}
        </div>
      </main>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section>
      <h2 className="font-display text-base font-semibold text-slate-100">{title}</h2>
      <div className="mt-2 space-y-2">{children}</div>
    </section>
  );
}

function Impressum() {
  return (
    <>
      <Section title="Angaben gemäß § 5 DDG">
        <p className="text-slate-400">
          [Vor- und Nachname]
          <br />
          [Straße und Hausnummer]
          <br />
          [PLZ und Ort]
          <br />
          Deutschland
        </p>
      </Section>
      <Section title="Kontakt">
        <p className="text-slate-400">
          Telefon: [Telefonnummer]
          <br />
          E-Mail: [E-Mail-Adresse]
        </p>
      </Section>
      <Section title="Umsatzsteuer">
        <p className="text-slate-400">
          USt-IdNr. gemäß § 27 a UStG: [USt-IdNr.] oder Steuernummer: [Steuernummer]
        </p>
      </Section>
      <Section title="Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV">
        <p className="text-slate-400">[Vor- und Nachname, Anschrift wie oben]</p>
      </Section>
      <Section title="Hinweis">
        <p className="text-slate-400">
          Ein Impressum ist in Deutschland für geschäftliche Websites Pflicht. Sobald du über diese
          Seite zahlende Kunden gewinnst, müssen Name, ladungsfähige Anschrift und eine schnelle
          Kontaktmöglichkeit vollständig und korrekt angegeben sein. Ein Postfach genügt nicht.
        </p>
      </Section>
    </>
  );
}

function Datenschutz() {
  return (
    <>
      <Section title="Verantwortlich">
        <p className="text-slate-400">
          [Vor- und Nachname, Anschrift, E-Mail]. Die vollständigen Angaben findest du im Impressum.
        </p>
      </Section>
      <Section title="Welche Daten verarbeitet werden">
        <p className="text-slate-400">
          Bei der Registrierung: Name, E-Mail-Adresse und ein Passwort, das ausschließlich als
          gesalzener Hash (PBKDF2-SHA256) gespeichert wird und nicht im Klartext vorliegt. Bei der
          Nutzung: Kunden-, Projekt- und Rechnungsdaten, die du selbst eingibst. Beim Absenden des
          Intake-Formulars: die dort gemachten Angaben inklusive E-Mail-Adresse der anfragenden
          Person.
        </p>
      </Section>
      <Section title="Zweck und Rechtsgrundlage">
        <p className="text-slate-400">
          Die Verarbeitung dient der Vertragsanbahnung und Vertragsdurchführung (Art. 6 Abs. 1 lit. b
          DSGVO) sowie dem sicheren Betrieb der Anwendung (lit. f). Daten werden nicht verkauft und
          nicht zu Werbezwecken weitergegeben.
        </p>
      </Section>
      <Section title="Cookies und Tracking">
        <p className="text-slate-400">
          Es werden keine Analyse- oder Marketing-Cookies eingesetzt. Für die Anmeldung wird ein
          Sitzungstoken im localStorage des Browsers gespeichert; das ist technisch notwendig und
          enthält kein Profiling.
        </p>
      </Section>
      <Section title="Auftragsverarbeiter">
        <p className="text-slate-400">
          Hosting der Weboberfläche: Vercel Inc. (USA). Hosting der API und der Datenbank: Render
          Services, Inc., Region Frankfurt am Main. Mit beiden Anbietern ist ein
          Auftragsverarbeitungsvertrag (AVV) über die jeweiligen Standardvertragsklauseln abzuschließen.
        </p>
      </Section>
      <Section title="Speicherdauer">
        <p className="text-slate-400">
          Kontodaten werden gelöscht, sobald das Konto gelöscht wird. Rechnungsdaten unterliegen den
          handels- und steuerrechtlichen Aufbewahrungsfristen (in der Regel bis zu 10 Jahre) und
          werden bis dahin aufbewahrt.
        </p>
      </Section>
      <Section title="Deine Rechte">
        <p className="text-slate-400">
          Auskunft, Berichtigung, Löschung, Einschränkung der Verarbeitung, Datenübertragbarkeit und
          Widerspruch. Eine Nachricht an die oben genannte Adresse genügt. Außerdem steht dir die
          Beschwerde bei einer Datenschutz-Aufsichtsbehörde zu.
        </p>
      </Section>
      <div className="rounded-xl border border-warn-400/20 bg-warn-400/10 px-4 py-3 text-sm text-warn-400">
        Diese Erklärung beschreibt den tatsächlichen Stand der Anwendung, ersetzt aber keine
        rechtliche Prüfung. Vor dem ersten zahlenden Kunden prüfen lassen.
      </div>
    </>
  );
}

function Agb() {
  return (
    <>
      <Section title="1. Geltungsbereich">
        <p className="text-slate-400">
          Diese Bedingungen gelten für die Nutzung der Software "Software Architect" durch
          Unternehmer im Sinne des § 14 BGB. Verbraucher nutzen die Software nicht.
        </p>
      </Section>
      <Section title="2. Vertragsschluss">
        <p className="text-slate-400">
          Die Registrierung stellt eine Bestellung dar. Der Vertrag kommt mit der Freischaltung des
          Zugangs zustande. Kostenlose Testphasen enden ohne Kündigung automatisch.
        </p>
      </Section>
      <Section title="3. Preise und Zahlung">
        <p className="text-slate-400">
          Es gelten die zum Bestellzeitpunkt angezeigten Preise zzgl. gesetzlicher Umsatzsteuer. Die
          Abrechnung erfolgt monatlich im Voraus. Rechnungen sind innerhalb von 14 Tagen ohne Abzug
          fällig.
        </p>
      </Section>
      <Section title="4. Laufzeit und Kündigung">
        <p className="text-slate-400">
          Der Vertrag verlängert sich monatlich und ist zum Ende des jeweiligen Abrechnungszeitraums
          kündbar. Das Recht zur außerordentlichen Kündigung aus wichtigem Grund bleibt bestehen.
        </p>
      </Section>
      <Section title="5. Verfügbarkeit und Gewährleistung">
        <p className="text-slate-400">
          Die Software wird als Cloud-Dienst bereitgestellt. Eine bestimmte Verfügbarkeit wird nicht
          garantiert; geplante Wartungsarbeiten werden angekündigt, soweit möglich. Für die
          Rechtmäßigkeit der eingegebenen Inhalte ist der Nutzer verantwortlich.
        </p>
      </Section>
      <Section title="6. Haftung">
        <p className="text-slate-400">
          Die Haftung ist auf Vorsatz und grobe Fahrlässigkeit beschränkt, soweit gesetzlich
          zulässig. Die Haftung nach dem Produkthaftungsgesetz und für Schäden aus der Verletzung von
          Leben, Körper oder Gesundheit bleibt unberührt.
        </p>
      </Section>
      <Section title="7. Schlussbestimmungen">
        <p className="text-slate-400">
          Es gilt deutsches Recht. Gerichtsstand ist der Sitz des Anbieters. Sollten einzelne
          Bestimmungen unwirksam sein, bleibt der übrige Vertrag wirksam.
        </p>
      </Section>
      <div className="rounded-xl border border-warn-400/20 bg-warn-400/10 px-4 py-3 text-sm text-warn-400">
        AGB für Software-Abos enthalten regelmäßig Punkte, die vor Gericht Bestand haben müssen
        (Haftung, Verfügbarkeit, Kündigung). Vor Veröffentlichung prüfen lassen.
      </div>
    </>
  );
}
