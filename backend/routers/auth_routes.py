import urllib.parse

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import verify_google_credential, create_access_token
import oauth

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/providers")
def providers():
    """Which social sign-in providers have credentials configured."""
    return oauth.enabled_providers()


@router.post("/google", response_model=schemas.LoginResponse)
def login_with_google(payload: schemas.GoogleLoginRequest, db: Session = Depends(get_db)):
    """
    Verifies a Google Identity Services credential (ID token) and either
    finds the matching user by google_sub, links an existing email/password
    account to Google, or creates a brand-new user.
    """
    try:
        claims = verify_google_credential(payload.credential)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {e}")

    google_sub = claims["sub"]
    email = claims.get("email")
    name = claims.get("name") or (email.split("@")[0].title() if email else "User")

    user = db.query(models.User).filter(models.User.google_sub == google_sub).first()

    if user is None and email:
        # Link to an existing account created before Google sign-in existed.
        user = db.query(models.User).filter(models.User.email == email).first()
        if user is not None:
            user.google_sub = google_sub
            db.commit()
            db.refresh(user)

    if user is None:
        user = models.User(name=name, email=email, google_sub=google_sub)
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return schemas.LoginResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/register", response_model=schemas.LoginResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """
    Creates a new account with email + password. Returns the same
    {access_token, user} payload as the other login endpoints.
    """
    from utils import hash_password

    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long",
        )

    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This email is already registered — sign in instead, or use Google.",
        )

    user = models.User(
        name=payload.name.strip() or payload.email.split("@")[0].title(),
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)
    return schemas.LoginResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@router.post("/login", response_model=schemas.LoginResponse)
def login_with_password(payload: schemas.PasswordLoginRequest, db: Session = Depends(get_db)):
    """
    Classic email + password login. Same generic error for unknown email and
    wrong password so the endpoint cannot be used to probe for accounts.
    """
    from utils import verify_password

    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)
    return schemas.LoginResponse(access_token=token, user=schemas.UserOut.model_validate(user))


# ── GitHub & Microsoft OAuth (authorization-code flow) ───────────────────────

_OAUTH = {
    "github": {"authorize": oauth.github_authorize_url, "profile": oauth.github_profile},
    "microsoft": {"authorize": oauth.microsoft_authorize_url, "profile": oauth.microsoft_profile},
}


@router.get("/{provider}/authorize")
def oauth_authorize(provider: str, redirect_uri: str | None = None):
    """
    Starts the OAuth flow: returns a 302 to the provider's consent screen.
    `redirect_uri` is where the frontend wants to land after the callback
    (defaults to {FRONTEND_URL}/login).
    """
    spec = _OAUTH.get(provider)
    if spec is None or not oauth.enabled_providers().get(provider):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{provider} sign-in is not configured on the server",
        )

    target = redirect_uri or f"{oauth.FRONTEND_URL}/login"
    # Only allow redirects back to our own frontend (or localhost in dev).
    parsed = urllib.parse.urlparse(target)
    allowed = [urllib.parse.urlparse(oauth.FRONTEND_URL).netloc, "localhost:5173", "127.0.0.1:5173"]
    if parsed.netloc not in allowed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="redirect_uri not allowed")

    state = oauth.sign_state(target)
    authorize_url = spec["authorize"](f"{oauth.FRONTEND_URL}/api/auth/{provider}/callback", state)
    return RedirectResponse(authorize_url, status_code=302)


@router.get("/{provider}/callback")
def oauth_callback(provider: str, code: str, state: str, db: Session = Depends(get_db)):
    """
    Provider redirects here after consent. Verifies the signed state,
    exchanges the code, upserts the user by email, then sends the browser
    back to the frontend with a session token in the query string.
    """
    spec = _OAUTH.get(provider)
    if spec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown provider")

    try:
        redirect_target = oauth.verify_state(state)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    try:
        profile = spec["profile"](code, f"{oauth.FRONTEND_URL}/api/auth/{provider}/callback")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Could not sign in with {provider}: {e}")
    except Exception as e:  # noqa: BLE001 — provider outages / bad codes
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Provider error: {e}")

    user = oauth.upsert_user_by_email(db, models, profile["email"], profile["name"])
    token = create_access_token(user.id)

    params = urllib.parse.urlencode(
        {"token": token, "name": user.name, "email": user.email}
    )
    separator = "&" if urllib.parse.urlparse(redirect_target).query else "?"
    return RedirectResponse(f"{redirect_target}{separator}{params}", status_code=302)
