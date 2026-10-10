"""
GitHub and Microsoft (Entra ID) sign-in via the OAuth 2.0 authorization-code
flow. Account linking is done by email — no extra columns on the User table —
matching the fallback behaviour the Google flow already uses.

Required environment variables (per provider, both must be set):
  GitHub:    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
  Microsoft: MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET,
             MICROSOFT_TENANT_ID (default "common", or your tenant UUID)

The frontend origin used for post-login redirects:
  FRONTEND_URL (default http://localhost:5173)
"""

import os
import secrets
import urllib.parse
from datetime import datetime, timedelta

import requests
from jose import JWTError, jwt

from auth import SECRET_KEY

STATE_TTL_MINUTES = 10

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT = os.getenv("MICROSOFT_TENANT_ID", "common")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


def enabled_providers() -> dict:
    """Which social providers have credentials configured on the server."""
    return {
        "google": bool(os.getenv("GOOGLE_CLIENT_ID", "")),
        "github": bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET),
        "microsoft": bool(MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET),
    }


# ── State (CSRF protection for the authorization-code flow) ───────────────────

def sign_state(redirect_uri: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=STATE_TTL_MINUTES)
    return jwt.encode(
        {"n": secrets.token_hex(16), "ru": redirect_uri, "exp": expire},
        SECRET_KEY,
        algorithm="HS256",
    )


def verify_state(state: str) -> str:
    """Returns the redirect_uri embedded in the state, or raises ValueError."""
    try:
        payload = jwt.decode(state, SECRET_KEY, algorithms=["HS256"])
    except JWTError as e:
        raise ValueError(f"Invalid state: {e}") from e
    return payload.get("ru", "")


# ── Shared account upsert ───────────────────────────────────────────────────

def upsert_user_by_email(db, models, email: str, name: str):
    """Find a user by email (linking an existing account) or create one."""
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        user = models.User(name=name or email.split("@")[0].title(), email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ── GitHub ───────────────────────────────────────────────────────────────────

def github_authorize_url(redirect_uri: str, state: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "read:user user:email",
            "state": state,
        }
    )
    return f"https://github.com/login/oauth/authorize?{params}"


def github_profile(code: str, redirect_uri: str) -> dict:
    """Exchanges the auth code for a token and fetches {email, name}."""
    res = requests.post(
        "https://github.com/login/oauth/access_token",
        data={
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
        },
        headers={"Accept": "application/json"},
        timeout=10,
    )
    res.raise_for_status()
    token = res.json().get("access_token")
    if not token:
        raise ValueError("GitHub did not return an access token")

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"}
    me = requests.get("https://api.github.com/user", headers=headers, timeout=10).json()

    email = None
    try:
        emails = requests.get(
            "https://api.github.com/user/emails", headers=headers, timeout=10
        ).json()
        primary = [e for e in emails if e.get("primary") and e.get("verified")]
        email = primary[0]["email"] if primary else next(iter(emails), {}).get("email")
    except Exception:  # noqa: BLE001 — email endpoint is best-effort
        email = None

    if not email:
        # GitHub's noreply convention keeps the email unique and stable.
        email = f"{me['id']}+{me['login']}@users.noreply.github.com"

    name = me.get("name") or me.get("login") or "GitHub user"
    return {"email": email, "name": name}


# ── Microsoft (Entra ID) ──────────────────────────────────────────────────────

def _ms_base() -> str:
    return f"https://login.microsoftonline.com/{MICROSOFT_TENANT}"


def microsoft_authorize_url(redirect_uri: str, state: str) -> str:
    params = urllib.parse.urlencode(
        {
            "client_id": MICROSOFT_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile User.Read",
            "state": state,
            "response_mode": "query",
        }
    )
    return f"{_ms_base()}/oauth2/v2.0/authorize?{params}"


def microsoft_profile(code: str, redirect_uri: str) -> dict:
    """Exchanges the auth code for a token and fetches {email, name} via MS Graph."""
    res = requests.post(
        f"{_ms_base()}/oauth2/v2.0/token",
        data={
            "client_id": MICROSOFT_CLIENT_ID,
            "client_secret": MICROSOFT_CLIENT_SECRET,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        },
        timeout=10,
    )
    res.raise_for_status()
    token = res.json().get("access_token")
    if not token:
        raise ValueError("Microsoft did not return an access token")

    me = requests.get(
        "https://graph.microsoft.com/v1.0/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    ).json()

    email = me.get("mail") or me.get("userPrincipalName")
    if not email:
        raise ValueError("Microsoft profile did not include an email address")
    name = me.get("displayName") or me.get("givenName") or "Microsoft user"
    return {"email": email, "name": name}
