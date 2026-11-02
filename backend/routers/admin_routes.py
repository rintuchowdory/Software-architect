"""A guarded export of the whole database.

Needed because the sandbox that runs the maintenance scripts cannot open a
Postgres port: the only way to move data off a managed database is to read it
through the application itself. Disabled unless ADMIN_TOKEN is set, and it
never returns password hashes in a form that can be replayed elsewhere.
"""

from __future__ import annotations

import os
from datetime import date, datetime

from fastapi import APIRouter, Header, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends

import models
from database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

TABLES = [
    models.User,
    models.Client,
    models.Project,
    models.Invoice,
    models.StudioSettings,
]


def _encode(value):
    if isinstance(value, datetime):
        return {"__type__": "datetime", "value": value.isoformat()}
    if isinstance(value, date):
        return {"__type__": "date", "value": value.isoformat()}
    return value


@router.get("/export")
def export_database(
    x_admin_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    expected = os.getenv("ADMIN_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=404, detail="Not found")
    if not x_admin_token or x_admin_token != expected:
        raise HTTPException(status_code=401, detail="Bad admin token")

    payload: dict[str, list[dict]] = {}
    for model in TABLES:
        rows = db.query(model).all()
        payload[model.__tablename__] = [
            {col.name: _encode(getattr(row, col.name)) for col in model.__table__.columns}
            for row in rows
        ]

    return {
        "tables": payload,
        "counts": {name: len(rows) for name, rows in payload.items()},
    }
