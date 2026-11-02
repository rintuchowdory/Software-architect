from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import create_access_token, get_current_user
from utils import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.LoginResponse)
def register(payload: schemas.RegisterRequest, db: Session = Depends(get_db)):
    """
    Creates a new account with email + password. Returns the same
    {access_token, user} payload as the login endpoint.
    """
    if len(payload.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters long",
        )

    existing = db.query(models.User).filter(models.User.email == payload.email).first()

    if existing is not None:
        if existing.password_hash:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This email is already registered. Sign in instead.",
            )
        # Legacy account created before email/password was the only sign-in
        # method: it has no password yet, so let the owner set one here.
        existing.password_hash = hash_password(payload.password)
        if not existing.name:
            existing.name = payload.name.strip() or payload.email.split("@")[0].title()
        db.commit()
        db.refresh(existing)
        token = create_access_token(existing.id)
        return schemas.LoginResponse(
            access_token=token, user=schemas.UserOut.model_validate(existing)
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
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(user.id)
    return schemas.LoginResponse(access_token=token, user=schemas.UserOut.model_validate(user))


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    """Returns the signed-in user, so the app can verify a stored token on load."""
    return schemas.UserOut.model_validate(current_user)
