import uuid
from datetime import date, datetime
from sqlalchemy import Column, String, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


def gen_id() -> str:
    return uuid.uuid4().hex[:12]


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    company = Column(String, default="")
    email = Column(String, nullable=False)
    status = Column(String, default="lead")  # lead | active | past
    created_at = Column(DateTime, default=datetime.utcnow)

    projects = relationship("Project", back_populates="client")


class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"))
    stage = Column(String, default="intake")  # intake | quoted | in_progress | delivered
    budget = Column(Float, default=0)
    brief = Column(String, default="")
    # How the brief was produced (manual | intake) and what the intake asked.
    brief_source = Column(String, default="manual")
    intake_notes = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="projects")
    invoices = relationship("Invoice", back_populates="project")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, default=gen_id)
    project_id = Column(String, ForeignKey("projects.id"))
    # Sequential per year, e.g. RE-2026-0007. Required for a valid German
    # invoice (§14 UStG) and must never be reused.
    number = Column(String, default="", index=True)
    amount = Column(Float, default=0)          # net
    tax_rate = Column(Float, default=19.0)     # 0 for Kleinunternehmer (§19 UStG)
    status = Column(String, default="draft")  # draft | sent | paid | overdue
    notes = Column(String, default="")
    due_date = Column(Date, default=date.today)
    paid_at = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="invoices")


class StudioSettings(Base):
    """Single row (id="studio") holding what goes on an invoice.

    Kept in the database rather than the environment so the owner can fix it
    from the UI without a redeploy, and so a fresh clone has no personal data.
    """

    __tablename__ = "studio_settings"
    id = Column(String, primary_key=True, default=lambda: "studio")
    name = Column(String, default="Software Architect")
    owner = Column(String, default="")
    address = Column(String, default="")
    email = Column(String, default="")
    phone = Column(String, default="")
    vat_id = Column(String, default="")
    tax_number = Column(String, default="")
    iban = Column(String, default="")
    bank = Column(String, default="")
    small_business = Column(String, default="false")  # "true" -> §19 UStG, no VAT
    hourly_rate = Column(Float, default=90.0)
