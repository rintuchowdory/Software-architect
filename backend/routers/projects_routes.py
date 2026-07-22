from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money

router = APIRouter(prefix="/projects", tags=["projects"])


def to_out(p: models.Project) -> schemas.ProjectOut:
    return schemas.ProjectOut(
        id=p.id,
        name=p.name,
        client_name=p.client.name if p.client else "—",
        stage=p.stage,
        budget=money(p.budget),
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
