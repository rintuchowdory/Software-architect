import os
from datetime import date, timedelta

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from database import Base, engine, SessionLocal, DB_INIT_ERROR
import models
from routers import (
    auth_routes,
    clients_routes,
    projects_routes,
    financials_routes,
    dashboard_routes,
    intake_routes,
    studio_routes,
    admin_routes,
)
from utils import next_invoice_number, default_tax_rate, create_numbered_invoice

app = FastAPI(title="Software Architect API")

_init_error: str | None = DB_INIT_ERROR


def ensure_columns() -> None:
    """Add columns introduced after a table already exists.

    create_all() only creates missing tables, so an existing database would
    keep the old schema and every invoice query would fail. This keeps the
    deployed database in step without a migration tool.
    """
    specs = {
        "projects": [
            ("brief_source", "VARCHAR DEFAULT 'manual'"),
            ("intake_notes", "VARCHAR DEFAULT ''"),
        ],
        "invoices": [
            ("number", "VARCHAR DEFAULT ''"),
            ("tax_rate", "FLOAT DEFAULT 19"),
            ("notes", "VARCHAR DEFAULT ''"),
            ("paid_at", "DATE"),
        ],
    }
    insp = inspect(engine)
    with engine.begin() as conn:
        for table, columns in specs.items():
            if not insp.has_table(table):
                continue
            present = {c["name"] for c in insp.get_columns(table)}
            for name, ddl in columns:
                if name not in present:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {ddl}"))


def backfill_invoices() -> None:
    """Give pre-existing invoices the data the new UI needs."""
    db = SessionLocal()
    try:
        if db.query(models.Invoice).count() == 0:
            return
        changed = False

        unnumbered = (
            db.query(models.Invoice)
            .filter((models.Invoice.number == "") | (models.Invoice.number.is_(None)))
            .order_by(models.Invoice.created_at)
            .all()
        )
        for invoice in unnumbered:
            year = invoice.created_at.year if invoice.created_at else date.today().year
            invoice.number = next_invoice_number(db, year)
            changed = True
        if changed:
            db.flush()

        seen: set[str] = set()
        for invoice in db.query(models.Invoice).order_by(models.Invoice.created_at):
            if invoice.number in seen:
                invoice.number = next_invoice_number(db)
                changed = True
            seen.add(invoice.number)

        for invoice in db.query(models.Invoice).filter(models.Invoice.status == "paid"):
            if not invoice.paid_at:
                invoice.paid_at = invoice.due_date or date.today()
                changed = True
            if invoice.tax_rate is None:
                invoice.tax_rate = default_tax_rate()
                changed = True

        if changed:
            db.commit()
    finally:
        db.close()


try:
    if not _init_error:
        Base.metadata.create_all(bind=engine)
        ensure_columns()
        backfill_invoices()
except Exception as e:  # noqa: BLE001
    _init_error = f"create_all failed: {type(e).__name__}: {e}"

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router, prefix="/api")
app.include_router(clients_routes.router, prefix="/api")
app.include_router(projects_routes.router, prefix="/api")
app.include_router(financials_routes.router, prefix="/api")
app.include_router(dashboard_routes.router, prefix="/api")
app.include_router(intake_routes.router, prefix="/api")
app.include_router(studio_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")


@app.exception_handler(SQLAlchemyError)
async def database_unavailable(request: Request, exc: SQLAlchemyError):
    """
    DB connection failures (e.g. a paused/deleted Postgres provider) reach
    the browser as a headerless 500, which surfaces as "Failed to fetch"
    with no CORS response. Return a clean 503 JSON instead so the UI can
    show what actually happened.
    """
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Database unavailable. The database provider may be paused or deleted. "
            "Restore it (or update DATABASE_URL), then retry."
        },
    )


@app.get("/api/health")
def health():
    if _init_error:
        return {"status": "error", "detail": _init_error}
    return {"status": "ok"}


def seed():
    db = SessionLocal()
    try:
        if db.query(models.Client).count() > 0:
            return

        acme = models.Client(name="Priya Nair", company="Acme Retail", email="priya@acme.io", status="active")
        blume = models.Client(name="Tom Ostrowski", company="Blume Labs", email="tom@blumelabs.dev", status="active")
        harborline = models.Client(name="Sara Keld", company="Harborline", email="sara@harborline.co", status="lead")
        db.add_all([acme, blume, harborline])
        db.commit()
        for c in (acme, blume, harborline):
            db.refresh(c)

        p1 = models.Project(name="Storefront rebuild", client_id=acme.id, stage="in_progress", budget=12500, brief="Headless storefront on Next.js + Shopify.")
        p2 = models.Project(name="Internal ops dashboard", client_id=blume.id, stage="quoted", budget=8200, brief="React/FastAPI dashboard for warehouse ops.")
        p3 = models.Project(name="Marketing site refresh", client_id=harborline.id, stage="intake", budget=4800, brief="")
        p4 = models.Project(name="Booking flow v2", client_id=acme.id, stage="delivered", budget=6100, brief="Rebuilt multi-step booking flow.")
        db.add_all([p1, p2, p3, p4])
        db.commit()
        for p in (p1, p2, p3, p4):
            db.refresh(p)

        today = date.today()
        rate = default_tax_rate()

        def add_invoice(project, amount, status, due_offset, paid_offset=None, notes=""):
            return create_numbered_invoice(
                db,
                project_id=project.id,
                amount=amount,
                tax_rate=rate,
                status=status,
                notes=notes,
                due_date=today + timedelta(days=due_offset),
                paid_at=(today + timedelta(days=paid_offset)) if paid_offset is not None else None,
            )

        add_invoice(p1, 6250, "paid", -20, -22)
        add_invoice(p1, 6250, "sent", 10)
        add_invoice(p4, 6100, "paid", -5, -6)
        add_invoice(p2, 2000, "overdue", -4)

        # A little history so the revenue chart has something to show.
        for months_back, amount in ((1, 4800), (2, 7200), (3, 3900), (4, 5100), (5, 6400)):
            add_invoice(p4, amount, "paid", -30 * months_back, -30 * months_back, notes="Archiv")

        db.commit()
    finally:
        db.close()


try:
    if not _init_error:
        seed()
except Exception as e:  # noqa: BLE001
    _init_error = f"seed failed: {type(e).__name__}: {e}"
