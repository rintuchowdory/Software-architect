from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
import models, schemas
from auth import get_current_user
from brief import HOURLY_RATE
from utils import money, gross_of
from routers.financials_routes import days_overdue, effective_status

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

STAGES = ["intake", "quoted", "in_progress", "delivered"]
MONTH_LABELS = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


def _months_back(count: int) -> list[tuple[int, int]]:
    today = date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(count):
        months.append((year, month))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(months))


@router.get("/stats", response_model=schemas.DashboardStats)
def stats(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    projects = db.query(models.Project).all()
    active_projects = sum(1 for p in projects if p.stage in ("quoted", "in_progress"))
    pipeline_value = sum(p.budget for p in projects if p.stage in ("intake", "quoted", "in_progress"))

    invoices = db.query(models.Invoice).all()
    overdue_invoices = sum(1 for i in invoices if effective_status(i) == "overdue")

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


@router.get("/overview", response_model=schemas.DashboardOverview)
def overview(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    """Everything the dashboard needs in one request: KPIs, a 6-month revenue
    series, the pipeline by stage, the overdue invoices worth chasing, and a
    prioritised list of what to do next."""
    projects = db.query(models.Project).all()
    invoices = db.query(models.Invoice).all()
    clients = db.query(models.Client).all()

    active_projects = sum(1 for p in projects if p.stage in ("quoted", "in_progress"))
    pipeline_value = sum(p.budget for p in projects if p.stage in ("intake", "quoted", "in_progress"))

    open_invoices = [i for i in invoices if effective_status(i) in ("sent", "overdue")]
    outstanding = sum(gross_of(i.amount, i.tax_rate or 0) for i in open_invoices)
    today = date.today()
    paid_this_month = sum(
        gross_of(i.amount, i.tax_rate or 0)
        for i in invoices
        if i.status == "paid" and i.paid_at and i.paid_at.month == today.month and i.paid_at.year == today.year
    )
    overdue_invoices = [i for i in invoices if effective_status(i) == "overdue"]
    overdue_amount = sum(gross_of(i.amount, i.tax_rate or 0) for i in overdue_invoices)

    week_ago = datetime.utcnow() - timedelta(days=7)
    new_leads = sum(1 for c in clients if c.status == "lead" and c.created_at and c.created_at >= week_ago)
    delivered = [p for p in projects if p.stage == "delivered"]
    avg_project = (sum(p.budget for p in delivered) / len(delivered)) if delivered else 0

    # Revenue: gross value of invoices paid per month.
    series = []
    for year, month in _months_back(6):
        total = sum(
            gross_of(i.amount, i.tax_rate or 0)
            for i in invoices
            if i.status == "paid" and i.paid_at and i.paid_at.year == year and i.paid_at.month == month
        )
        series.append(schemas.RevenuePoint(month=f"{year}-{month:02d}", label=MONTH_LABELS[month - 1], value=round(total)))

    pipeline = []
    for stage in STAGES:
        group = [p for p in projects if p.stage == stage]
        value = sum(p.budget for p in group)
        pipeline.append(
            schemas.PipelineStage(stage=stage, count=len(group), value=money(value), value_raw=round(value))
        )

    overdue = sorted(overdue_invoices, key=lambda i: days_overdue(i), reverse=True)[:5]
    overdue_out = [
        schemas.OverdueItem(
            id=i.id,
            number=i.number or "",
            project_name=i.project.name if i.project else "—",
            client_name=(i.project.client.name if i.project and i.project.client else "—"),
            total=money(gross_of(i.amount, i.tax_rate or 0)),
            days_overdue=days_overdue(i),
        )
        for i in overdue
    ]

    # Next actions, most urgent first. These are derived, not stored: the
    # dashboard tells you what the data implies instead of only counting it.
    actions: list[schemas.ActionItem] = []
    for inv in sorted(overdue_invoices, key=lambda i: days_overdue(i), reverse=True)[:3]:
        client = inv.project.client.name if inv.project and inv.project.client else "the client"
        actions.append(
            schemas.ActionItem(
                id=f"chase-{inv.id}",
                title=f"Chase invoice {inv.number or inv.id[:6]}",
                detail=f"{money(gross_of(inv.amount, inv.tax_rate or 0))} from {client}, {days_overdue(inv)} days overdue",
                kind="money",
                href="/app/financials",
                priority=1,
            )
        )

    stale_quotes = [p for p in projects if p.stage == "quoted" and p.created_at and (datetime.utcnow() - p.created_at).days >= 7]
    for project in stale_quotes[:2]:
        actions.append(
            schemas.ActionItem(
                id=f"quote-{project.id}",
                title=f"Follow up on {project.name}",
                detail=f"Quote sent {(datetime.utcnow() - project.created_at).days} days ago and still open",
                kind="sales",
                href="/app/projects",
                priority=2,
            )
        )

    missing_brief = [p for p in projects if p.stage in ("intake", "quoted") and not (p.brief or "").strip()]
    for project in missing_brief[:2]:
        actions.append(
            schemas.ActionItem(
                id=f"brief-{project.id}",
                title=f"Scope {project.name}",
                detail="No brief yet. Send the intake link or write one from the answers.",
                kind="delivery",
                href="/app/projects",
                priority=3,
            )
        )

    if not projects:
        actions.append(
            schemas.ActionItem(
                id="first-project",
                title="Create your first project",
                detail="Add a client, then send them the intake link to get a scoped brief automatically.",
                kind="sales",
                href="/app/clients",
                priority=1,
            )
        )
    if not invoices and projects:
        actions.append(
            schemas.ActionItem(
                id="first-invoice",
                title="Invoice your first project",
                detail="Invoices get a sequential number and a USt breakdown automatically.",
                kind="money",
                href="/app/financials",
                priority=3,
            )
        )

    actions.sort(key=lambda a: a.priority)

    return schemas.DashboardOverview(
        active_projects=active_projects,
        pipeline_value=money(pipeline_value),
        outstanding=money(outstanding),
        paid_this_month=money(paid_this_month),
        overdue_invoices=len(overdue_invoices),
        overdue_amount=money(overdue_amount),
        new_leads=new_leads,
        avg_project_value=money(avg_project),
        billable_hours_estimate=int(sum(p.budget for p in projects if p.stage == "in_progress") / max(HOURLY_RATE, 1)),
        revenue_series=series,
        pipeline=pipeline,
        overdue=overdue_out,
        actions=actions[:6],
    )
