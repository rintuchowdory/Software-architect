from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def stats(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    projects = db.query(models.Project).all()
    active_projects = sum(1 for p in projects if p.stage in ("quoted", "in_progress"))
    pipeline_value = sum(p.budget for p in projects if p.stage in ("intake", "quoted", "in_progress"))

    invoices = db.query(models.Invoice).all()
    overdue_invoices = sum(1 for i in invoices if i.status == "overdue")

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_leads = db.query(models.Client).filter(
        models.Client.status == "lead", models.Client.created_at >= week_ago
    ).count()

    return schemas.DashboardStats(
        active_projects=active_projects,
        pipeline_value=money(pipeline_value),
        overdue_invoices=overdue_invoices,
        new_leads=new_leads,
    )
