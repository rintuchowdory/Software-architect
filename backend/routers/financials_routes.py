from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money, gross_of, tax_of, default_tax_rate, create_numbered_invoice

router = APIRouter(prefix="/financials", tags=["financials"])

VALID_STATUS = {"draft", "sent", "paid", "overdue"}


def days_overdue(inv: models.Invoice) -> int:
    if inv.status not in ("sent", "overdue") or not inv.due_date:
        return 0
    delta = (date.today() - inv.due_date).days
    return delta if delta > 0 else 0


def effective_status(inv: models.Invoice) -> str:
    """A sent invoice past its due date is overdue, whether or not anyone
    remembered to update the status."""
    if inv.status == "sent" and days_overdue(inv) > 0:
        return "overdue"
    return inv.status


def to_out(inv: models.Invoice) -> schemas.InvoiceOut:
    project = inv.project
    client = project.client if project and project.client else None
    rate = inv.tax_rate if inv.tax_rate is not None else 19.0
    return schemas.InvoiceOut(
        id=inv.id,
        number=inv.number or "",
        project_id=inv.project_id or "",
        project_name=project.name if project else "—",
        client_name=client.name if client else "—",
        client_company=client.company if client else "",
        client_email=client.email if client else "",
        amount=money(inv.amount),
        tax_rate=rate,
        tax_amount=money(tax_of(inv.amount, rate)),
        total=money(gross_of(inv.amount, rate)),
        status=effective_status(inv),
        due_date=inv.due_date.isoformat() if inv.due_date else "",
        paid_at=inv.paid_at.isoformat() if inv.paid_at else "",
        days_overdue=days_overdue(inv),
        notes=inv.notes or "",
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
    if payload.status and payload.status not in VALID_STATUS:
        raise HTTPException(status_code=422, detail="Unknown invoice status")
    data = payload.model_dump()
    rate = data.pop("tax_rate")
    data.pop("due_date", None)
    invoice = create_numbered_invoice(
        db,
        **data,
        tax_rate=rate if rate is not None else default_tax_rate(),
        due_date=payload.due_date or date.today(),
    )
    db.commit()
    db.refresh(invoice)
    return to_out(invoice)


@router.get("/invoices/{invoice_id}", response_model=schemas.InvoiceOut)
def get_invoice(invoice_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    invoice = db.query(models.Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return to_out(invoice)


@router.patch("/invoices/{invoice_id}", response_model=schemas.InvoiceOut)
def update_invoice(
    invoice_id: str,
    payload: schemas.InvoiceUpdate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    invoice = db.query(models.Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    changes = payload.model_dump(exclude_unset=True)
    if "status" in changes and changes["status"] not in VALID_STATUS:
        raise HTTPException(status_code=422, detail="Unknown invoice status")

    for field, value in changes.items():
        setattr(invoice, field, value)

    # Keep paid_at in sync with the status so "paid this month" is real.
    if changes.get("status") == "paid" and not invoice.paid_at:
        invoice.paid_at = date.today()
    if changes.get("status") in ("draft", "sent", "overdue"):
        invoice.paid_at = None

    db.commit()
    db.refresh(invoice)
    return to_out(invoice)


@router.get("/summary", response_model=schemas.FinancialSummary)
def summary(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    invoices = db.query(models.Invoice).all()
    open_invoices = [i for i in invoices if effective_status(i) in ("sent", "overdue")]
    outstanding = sum(gross_of(i.amount, i.tax_rate or 0) for i in open_invoices)
    paid_this_month = sum(
        gross_of(i.amount, i.tax_rate or 0)
        for i in invoices
        if i.status == "paid"
        and i.paid_at
        and i.paid_at.month == date.today().month
        and i.paid_at.year == date.today().year
    )
    overdue = [i for i in invoices if effective_status(i) == "overdue"]
    return schemas.FinancialSummary(
        outstanding=money(outstanding),
        paid_this_month=money(paid_this_month),
        overdue_count=len(overdue),
        overdue_amount=money(sum(gross_of(i.amount, i.tax_rate or 0) for i in overdue)),
    )
