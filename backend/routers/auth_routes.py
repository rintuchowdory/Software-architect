from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models
import schemas
from auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    First sign-in for an email creates the account. Later sign-ins for the
    same email must match the password used the first time.
    """
    user = db.query(models.User).filter(models.User.email == payload.email).first()

    if user is None:
        name = payload.email.split("@")[0].replace(".", " ").title()
        user = models.User(name=name, email=payload.email, password_hash=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = create_access_token(user.id)
    return schemas.LoginResponse(access_token=token, user=schemas.UserOut.model_validate(user))
