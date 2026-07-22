import os
from datetime import date, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine, SessionLocal, DB_INIT_ERROR
import models
from routers import auth_routes, clients_routes, projects_routes, financials_routes, dashboard_routes

app = FastAPI(title="Software Architect API")

_init_error: str | None = DB_INIT_ERROR
try:
    if not _init_error:
        Base.metadata.create_all(bind=engine)
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
        db.add_all([
            models.Invoice(project_id=p1.id, amount=6250, status="paid", due_date=today - timedelta(days=20)),
            models.Invoice(project_id=p1.id, amount=6250, status="sent", due_date=today + timedelta(days=10)),
            models.Invoice(project_id=p4.id, amount=6100, status="paid", due_date=today - timedelta(days=5)),
            models.Invoice(project_id=p2.id, amount=2000, status="overdue", due_date=today - timedelta(days=4)),
        ])
        db.commit()
    finally:
        db.close()


try:
    if not _init_error:
        seed()
except Exception as e:  # noqa: BLE001
    _init_error = f"seed failed: {type(e).__name__}: {e}"
