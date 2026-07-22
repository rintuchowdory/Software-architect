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
    password_hash = Column(String, nullable=False)
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
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="projects")
    invoices = relationship("Invoice", back_populates="project")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String, primary_key=True, default=gen_id)
    project_id = Column(String, ForeignKey("projects.id"))
    amount = Column(Float, default=0)
    status = Column(String, default="draft")  # draft | sent | paid | overdue
    due_date = Column(Date, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="invoices")
