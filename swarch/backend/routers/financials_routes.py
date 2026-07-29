from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money

router = APIRouter(prefix="/financials", tags=["financials"])


def to_out(inv: models.Invoice) -> schemas.InvoiceOut:
    return schemas.InvoiceOut(
        id=inv.id,
        project_name=inv.project.name if inv.project else "—",
        client_name=inv.project.client.name if inv.project and inv.project.client else "—",
        amount=money(inv.amount),
        status=inv.status,
        due_date=inv.due_date.isoformat() if inv.due_date else "",
    )


@router.get("/invoices", response_model=List[schemas.InvoiceOut])
def list_invoices(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    invoices = db.query(models.Invoice).order_by(models.Invoice.created_at.desc()).all()
    return [to_out(i) for i in invoices]


@router.post("/invoices", response_model=schemas.InvoiceOut)
def create_invoice(
    payload: schemas.InvoiceCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    project = db.query(models.Project).get(payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    invoice = models.Invoice(**payload.model_dump())
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return to_out(invoice)


@router.get("/summary", response_model=schemas.FinancialSummary)
def summary(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    invoices = db.query(models.Invoice).all()
    outstanding = sum(i.amount for i in invoices if i.status in ("sent", "overdue"))
    paid_this_month = sum(
        i.amount
        for i in invoices
        if i.status == "paid"
        and i.due_date
        and i.due_date.month == date.today().month
        and i.due_date.year == date.today().year
    )
    overdue_count = sum(1 for i in invoices if i.status == "overdue")
    return schemas.FinancialSummary(
        outstanding=money(outstanding),
        paid_this_month=money(paid_this_month),
        overdue_count=overdue_count,
    )
