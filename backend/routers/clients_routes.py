from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from utils import money, gross_of

router = APIRouter(prefix="/clients", tags=["clients"])


def to_out(client: models.Client, open_value: float = 0) -> schemas.ClientOut:
    return schemas.ClientOut(
        id=client.id,
        name=client.name,
        company=client.company or "",
        email=client.email,
        status=client.status,
        open_value=money(open_value),
    )


def _open_value(client: models.Client) -> float:
    total = 0.0
    for project in client.projects or []:
        for invoice in project.invoices or []:
            if invoice.status in ("sent", "overdue"):
                total += gross_of(invoice.amount, invoice.tax_rate or 0)
    return total


@router.get("", response_model=List[schemas.ClientOut])
def list_clients(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    clients = db.query(models.Client).order_by(models.Client.created_at.desc()).all()
    return [to_out(c, _open_value(c)) for c in clients]


@router.post("", response_model=schemas.ClientOut)
def create_client(
    payload: schemas.ClientCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    client = models.Client(**payload.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return to_out(client)


@router.get("/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: str, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    client = db.query(models.Client).get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return to_out(client, _open_value(client))
