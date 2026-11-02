def money(value: float) -> str:
    # German-style formatting: thousands dot, symbol after the number.
    formatted = f"{value:,.0f}".replace(",", ".")
    return f"{formatted} €"

# --- Password hashing (classic email/password auth) -------------------------
# Standard-library PBKDF2-SHA256; no extra dependency needed. Format:
# pbkdf2_sha256$<iterations>$<salt hex>$<digest hex>

def hash_password(password: str) -> str:
    import hashlib
    import os

    salt = os.urandom(16)
    iterations = 390_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    import hashlib
    import hmac

    if not stored:
        return False
    try:
        scheme, iterations, salt_hex, hash_hex = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(digest.hex(), hash_hex)
    except (ValueError, TypeError):
        return False


# --- Invoicing helpers ------------------------------------------------------

def tax_of(net: float, rate: float) -> float:
    return round(net * rate / 100.0, 2)


def gross_of(net: float, rate: float) -> float:
    return round(net + tax_of(net, rate), 2)


def default_tax_rate() -> float:
    """0 % is the correct value for Kleinunternehmer under §19 UStG."""
    import os

    try:
        return float(os.getenv("DEFAULT_TAX_RATE", "19"))
    except ValueError:
        return 19.0


def next_invoice_number(db, year: int | None = None) -> str:
    """Sequential, gap-free-per-year invoice number: RE-2026-0001.

    Reads the highest existing number for the year rather than counting rows,
    so deleting a draft cannot hand out a number twice.
    """
    import re
    from datetime import date

    import models

    # The session is created with autoflush=False, so pending invoices would
    # otherwise be invisible here and two invoices could get the same number.
    db.flush()

    year = year or date.today().year
    prefix = f"RE-{year}-"
    highest = 0
    for (number,) in db.query(models.Invoice.number).filter(
        models.Invoice.number.like(f"{prefix}%")
    ):
        match = re.fullmatch(rf"{prefix}(\d+)", number or "")
        if match:
            highest = max(highest, int(match.group(1)))
    return f"{prefix}{highest + 1:04d}"


def create_numbered_invoice(db, **fields):
    """Insert an invoice and give it the next number in one safe step.

    The row is added and flushed first, so concurrent numbering sees it and
    the unique-per-year sequence cannot hand out the same number twice.
    """
    import models

    invoice = models.Invoice(**fields)
    db.add(invoice)
    db.flush()
    from datetime import date

    year = invoice.created_at.year if invoice.created_at else date.today().year
    invoice.number = next_invoice_number(db, year)
    db.flush()
    return invoice
