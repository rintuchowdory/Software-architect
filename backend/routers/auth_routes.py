from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import verify_google_credential, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


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
