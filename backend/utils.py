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
