"""Public (no-login) intake questionnaire.

A prospective client fills this in, and the studio gets a lead, a project in
the intake stage, and a scoped brief with an effort estimate, without anyone
typing a word. Kept deliberately simple, but rate limited per IP so a public
endpoint cannot be used to flood the project list.
"""

from collections import defaultdict
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
import studio_profile
from brief import PROJECT_TYPES, FEATURES, TIMELINE_LABELS, generate_brief
from utils import money

router = APIRouter(prefix="/public/intake", tags=["intake"])

# ip -> list of submission timestamps (UTC). One instance only; fine at this size.
_recent: dict[str, list[datetime]] = defaultdict(list)
LIMIT_PER_HOUR = 5


def _rate_limit(ip: str) -> None:
    now = datetime.utcnow()
    window = [ts for ts in _recent[ip] if (now - ts).total_seconds() < 3600]
    if len(window) >= LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    window.append(now)
    _recent[ip] = window


@router.get("/options")
def options():
    """Everything the form needs, so labels live in one place (brief.py)."""
    return {
        "project_types": [{"value": k, "label": v[0]} for k, v in PROJECT_TYPES.items()],
        "features": [{"value": k, "label": v[0]} for k, v in FEATURES.items()],
        "timelines": [{"value": k, "label": label} for k, label in TIMELINE_LABELS.items()],
    }


@router.post("", response_model=schemas.IntakeResponse)
def submit(payload: schemas.IntakeRequest, request: Request, db: Session = Depends(get_db)):
    _rate_limit(request.client.host if request.client else "unknown")

    if payload.project_type not in PROJECT_TYPES:
        raise HTTPException(status_code=422, detail="Unknown project type")

    answers = payload.model_dump()
    answers["created_on"] = datetime.utcnow().date().isoformat()
    result = generate_brief(answers, hourly_rate=studio_profile.hourly_rate(db))

    client = db.query(models.Client).filter(models.Client.email == payload.email).first()
    if not client:
        client = models.Client(
            name=payload.client_name or payload.email.split("@")[0],
            company=payload.company,
            email=payload.email,
            status="lead",
        )
        db.add(client)
        db.commit()
        db.refresh(client)

    project = models.Project(
        name=result["title"],
        client_id=client.id,
        stage="intake",
        budget=(result["estimate_low"] + result["estimate_high"]) / 2,
        brief=result["brief"],
        brief_source="intake",
        intake_notes="\n".join(f"{k}: {v}" for k, v in answers.items() if v),
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    return schemas.IntakeResponse(
        project_id=project.id,
        title=result["title"],
        brief=result["brief"],
        hours=result["hours"],
        estimate_low=money(result["estimate_low"]),
        estimate_high=money(result["estimate_high"]),
    )
