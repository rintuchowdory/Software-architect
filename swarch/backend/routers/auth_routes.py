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
