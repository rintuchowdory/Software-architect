"""The studio's own details: the sender block of every invoice.

Resolution order is database row, then environment variable, then a sane
default, so an unconfigured instance still boots and the UI can show exactly
what is missing instead of printing a plausible-looking fake address.
"""

from __future__ import annotations

import os

import models

SINGLETON = "studio"

FIELDS = (
    "name",
    "owner",
    "address",
    "email",
    "phone",
    "vat_id",
    "tax_number",
    "iban",
    "bank",
)

ENV_KEYS = {
    "name": "STUDIO_NAME",
    "owner": "STUDIO_OWNER",
    "address": "STUDIO_ADDRESS",
    "email": "STUDIO_EMAIL",
    "phone": "STUDIO_PHONE",
    "vat_id": "STUDIO_VAT_ID",
    "tax_number": "STUDIO_TAX_NUMBER",
    "iban": "STUDIO_IBAN",
    "bank": "STUDIO_BANK",
}

DEFAULTS = {"name": "Software Architect"}


def _row(session) -> models.StudioSettings | None:
    return session.query(models.StudioSettings).filter_by(id=SINGLETON).first()


def load(session) -> dict:
    """Current profile plus what still has to be filled in."""
    row = _row(session)
    data: dict = {}
    for field in FIELDS:
        from_row = getattr(row, field, None) if row is not None else None
        data[field] = (from_row or "").strip() or os.getenv(ENV_KEYS[field], "").strip() or DEFAULTS.get(field, "")

    small_business = os.getenv("STUDIO_SMALL_BUSINESS", "false").lower() in ("1", "true", "yes")
    if row is not None:
        small_business = (row.small_business or "false") == "true"
    data["small_business"] = small_business

    rate = None if row is None else row.hourly_rate
    data["hourly_rate"] = float(rate or os.getenv("HOURLY_RATE", "90"))

    missing = [f for f in ("owner", "address", "email") if not data[f]]
    # A German invoice needs the tax figure or the exemption reason (§14 UStG).
    if not small_business and not (data["vat_id"] or data["tax_number"]):
        missing.append("vat_id")
    data["missing"] = missing
    data["complete"] = not missing
    return data


def hourly_rate(session) -> float:
    return load(session)["hourly_rate"]


def save(session, payload: dict) -> dict:
    row = _row(session)
    if row is None:
        row = models.StudioSettings(id=SINGLETON)
        session.add(row)
    for field in FIELDS:
        if field in payload:
            setattr(row, field, (payload[field] or "").strip())
    if "small_business" in payload:
        row.small_business = "true" if payload["small_business"] else "false"
    if "hourly_rate" in payload:
        row.hourly_rate = float(payload["hourly_rate"])
    session.commit()
    return load(session)
