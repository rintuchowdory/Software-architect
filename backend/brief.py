"""Guided intake → scoped project brief.

Deterministic and dependency-free on purpose: no LLM call, no API key, no
per-request cost, and the output is stable enough to unit test. The text is
German because it is the document the studio's German clients read.
"""

from __future__ import annotations

import os

HOURLY_RATE = float(os.getenv("HOURLY_RATE", "90"))  # fallback when no settings row exists

PROJECT_TYPES = {
    "website": ("Website / Marketingseite", 45),
    "shop": ("Onlineshop", 80),
    "webapp": ("Web-App", 110),
    "dashboard": ("Dashboard / internes Tool", 70),
    "api": ("API / Backend", 40),
    "automation": ("Automatisierung", 30),
    "mobile": ("Mobile App", 130),
    "other": ("Sonstiges", 55),
}

FEATURES = {
    "auth": ("Login / Benutzerkonten", 12),
    "payments": ("Zahlungen", 16),
    "cms": ("Inhalte selbst pflegen", 14),
    "search": ("Suche / Filter", 8),
    "notifications": ("E-Mail-Benachrichtigungen", 6),
    "reporting": ("Auswertungen / Berichte", 14),
    "integrations": ("Anbindung an Fremdsysteme", 12),
    "design": ("Individuelles Design", 18),
    "seo": ("SEO-Grundlagen", 6),
    "multilingual": ("Mehrsprachigkeit", 10),
    "admin": ("Admin-Bereich", 12),
    "uploads": ("Datei-Uploads", 6),
}

TIMELINES = {
    "asap": "so schnell wie möglich",
    "4w": "in etwa 4 Wochen",
    "8w": "in 2 Monaten",
    "flexible": "zeitlich flexibel",
}

# Labels for the form; the sentences above are used inside the brief text.
TIMELINE_LABELS = {
    "asap": "So schnell wie möglich",
    "4w": "In etwa 4 Wochen",
    "8w": "In 2 Monaten",
    "flexible": "Zeitlich flexibel",
}


def _round_to(value: float, step: int) -> int:
    return int(round(value / step) * step)


def estimate(project_type: str, features: list[str], rate: float | None = None) -> tuple[int, int, int]:
    """Return (hours, low_eur, high_eur) for a project type and feature list."""
    rate = float(rate or HOURLY_RATE)
    _, base = PROJECT_TYPES.get(project_type, PROJECT_TYPES["other"])
    hours = base
    for key in features:
        hours += FEATURES.get(key, ("", 8))[1]
    hours = _round_to(hours, 5)
    low = _round_to(hours * rate * 0.85, 50)
    high = _round_to(hours * rate * 1.25, 50)
    return hours, low, high


def _feature_lines(features: list[str]) -> list[str]:
    if not features:
        return ["- Keine Zusatzfunktionen bestätigt. Der Umfang wird im Gespräch festgelegt."]
    return [f"- {FEATURES.get(f, (f, 8))[0]}" for f in features]


def generate_brief(answers: dict, hourly_rate: float | None = None) -> dict:
    """Build the brief from intake answers.

    Expected keys (all optional except project_type): project_type, goal,
    features, timeline, budget, existing, notes, client_name, company,
    project_name.
    """
    rate = float(hourly_rate or HOURLY_RATE)
    project_type = (answers.get("project_type") or "other").lower()
    type_label, _ = PROJECT_TYPES.get(project_type, PROJECT_TYPES["other"])
    features = [f for f in (answers.get("features") or []) if f]
    goal = (answers.get("goal") or "").strip()
    existing = (answers.get("existing") or "").strip()
    notes = (answers.get("notes") or "").strip()
    budget = (answers.get("budget") or "").strip()
    timeline = TIMELINES.get((answers.get("timeline") or "").lower(), "noch offen")
    client_name = (answers.get("client_name") or "").strip()
    company = (answers.get("company") or "").strip()
    title = (answers.get("project_name") or "").strip() or f"{type_label} für {company or client_name or 'neuen Kunden'}"

    hours, low, high = estimate(project_type, features, rate)

    lines = [f"# {title}", ""]
    if client_name or company:
        lines += [f"**Kunde:** {client_name}{f' ({company})' if company else ''}", ""]
    lines += [
        "## Ausgangslage",
        goal or "Der Kunde hat noch kein Ziel schriftlich formuliert. Im Erstgespräch klären.",
        "",
        "## Umfang (Vorschlag)",
        f"- Projektart: {type_label}",
        *_feature_lines(features),
        "",
        "## Nicht enthalten",
        "- Texte und Bildmaterial (sofern nicht anders vereinbart)",
        "- Laufende Betreuung nach Abnahme",
        "- Kostenpflichtige Fremdleistungen (Hosting, Lizenzen, Zahlungsanbieter)",
        "",
        "## Aufwandsschätzung",
        f"- Geschätzter Aufwand: {hours} Stunden",
        f"- Rahmen: {low:,.0f} € bis {high:,.0f} € netto (Stundensatz {rate:.0f} €)".replace(",", "."),
        f"- Gewünschter Zeitrahmen: {timeline}",
    ]
    if budget:
        lines.append(f"- Budgetvorstellung des Kunden: {budget}")
    lines += ["", "## Voraussetzungen"]
    lines.append(f"- Bestehendes Material: {existing}" if existing else "- Bestehendes Material: noch unklar, im Gespräch klären")
    lines += ["- Eine Ansprechperson mit Entscheidungsbefugnis", ""]

    if notes:
        lines += ["## Notizen des Kunden", notes, ""]

    lines += [
        "## Nächste Schritte",
        "1. Erstgespräch (30 Minuten) zur Schärfung des Umfangs",
        "2. Verbindliches Angebot mit Festpreis oder Aufwandsschätzung",
        "3. Anzahlung, dann Kick-off",
        "",
        f"_Erstellt am {answers.get('created_on', '')} aus dem Intake-Fragebogen. Schätzung, kein Angebot._",
    ]

    return {
        "title": title,
        "brief": "\n".join(lines),
        "hours": hours,
        "estimate_low": low,
        "estimate_high": high,
    }
