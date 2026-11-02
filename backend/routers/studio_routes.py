"""Studio profile: the sender block on invoices.

Stored in the database so it can be edited from the UI (Settings) without a
redeploy; environment variables remain as the initial value for a fresh
instance. Nothing here is committed to the repository.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models, schemas, studio_profile
from auth import get_current_user
from database import get_db

router = APIRouter(prefix="/studio", tags=["studio"])


@router.get("/profile", response_model=schemas.StudioProfileOut)
def profile(user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return studio_profile.load(db)


@router.put("/profile", response_model=schemas.StudioProfileOut)
def update_profile(
    payload: schemas.StudioProfileIn,
    user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not (payload.name or "").strip():
        raise HTTPException(status_code=422, detail="Der Studio-Name darf nicht leer sein.")
    return studio_profile.save(db, payload.model_dump())
