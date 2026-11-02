from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money
from brief import generate_brief

router = APIRouter(prefix="/projects", tags=["projects"])


def to_out(p: models.Project) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id=p.id,
        name=p.name,
        client_name=p.client.name if p.client else "—",
        stage=p.stage,
        budget=money(p.budget),
        has_brief=bool((p.brief or "").strip()),
    )


@router.get("", response_model=List[schemas.ProjectOut])
def list_projects(
    limit: Optional[int] = None,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    q = db.query(models.Project).order_by(models.Project.created_at.desc())
    if limit:
        q = q.limit(limit)
    return [to_out(p) for p in q.all()]


@router.post("", response_model=schemas.ProjectOut)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    client = db.query(models.Client).get(payload.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    project = models.Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return to_out(project)


@router.patch("/{project_id}", response_model=schemas.ProjectOut)
def update_project_stage(
    project_id: str,
    stage: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.stage = stage
    db.commit()
    db.refresh(project)
    return to_out(project)


@router.post("/{project_id}/brief", response_model=schemas.ProjectOut)
def regenerate_brief(
    project_id: str,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    """Rebuild the brief from the stored intake answers.

    Re-running is safe: the generator is deterministic, so the text only
    changes if the answers (or the estimate table) changed.
    """
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    answers: dict = {"created_on": project.created_at.date().isoformat() if project.created_at else ""}
    for line in (project.intake_notes or "").splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            answers[key.strip()] = value.strip()

    if not answers.get("project_type"):
        raise HTTPException(
            status_code=422,
            detail="This project has no intake answers. Send the intake link instead.",
        )

    result = generate_brief(answers)
    project.brief = result["brief"]
    project.brief_source = "intake"
    project.budget = (result["estimate_low"] + result["estimate_high"]) / 2
    db.commit()
    db.refresh(project)
    return to_out(project)
