"""Move the studio between databases without losing a single invoice.

    python scripts/db_snapshot.py export backup.json
    DATABASE_URL=postgresql://... python scripts/db_snapshot.py import backup.json

Plain JSON rather than pg_dump on purpose: it works from the free Render
Postgres, into Supabase, Neon, or the local SQLite fallback, and it does not
care about server versions. Schema migration is handled by create_all on
startup, so the target database only has to be reachable.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import database  # noqa: E402
import models  # noqa: E402

TABLES = [
    models.User,
    models.Client,
    models.Project,
    models.Invoice,
    models.StudioSettings,
]

# Insert order matters for the foreign keys (clients -> projects -> invoices).
DATE_FIELDS = {"due_date", "paid_at"}


def _encode(value):
    if isinstance(value, (datetime, date)):
        return {"__type__": type(value).__name__, "value": value.isoformat()}
    return value


def _decode(value, field: str):
    if isinstance(value, dict) and value.get("__type__"):
        raw = value["value"]
        if value["__type__"] == "datetime":
            return datetime.fromisoformat(raw)
        return date.fromisoformat(raw)
    if field in DATE_FIELDS and isinstance(value, str) and value:
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return value


def export(path: str) -> None:
    session = database.SessionLocal()
    payload: dict[str, list[dict]] = {}
    try:
        for model in TABLES:
            rows = session.query(model).all()
            payload[model.__tablename__] = [
                {col.name: _encode(getattr(row, col.name)) for col in model.__table__.columns}
                for row in rows
            ]
    finally:
        session.close()

    Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    counts = ", ".join(f"{name}={len(rows)}" for name, rows in payload.items())
    print(f"exported {counts} -> {path}")


def import_(path: str) -> None:
    payload = json.loads(Path(path).read_text())
    database.Base.metadata.create_all(bind=database.engine)
    session = database.SessionLocal()
    try:
        for model in TABLES:
            rows = payload.get(model.__tablename__, [])
            columns = {col.name for col in model.__table__.columns}
            for raw in rows:
                clean = {
                    key: _decode(value, key)
                    for key, value in raw.items()
                    if key in columns
                }
                if session.get(model, clean.get("id")) is not None:
                    continue  # already there; the snapshot is not authoritative
                session.add(model(**clean))
            session.commit()
            print(f"{model.__tablename__}: {len(rows)} rows")
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["export", "import"])
    parser.add_argument("path")
    args = parser.parse_args()

    print(f"target: {os.getenv('DATABASE_URL', 'sqlite (local fallback)').split('@')[-1]}")
    if args.action == "export":
        export(args.path)
    else:
        import_(args.path)


if __name__ == "__main__":
    main()
