from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str

    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    access_token: str
    user: UserOut


class ClientCreate(BaseModel):
    name: str
    company: Optional[str] = ""
    email: EmailStr
    status: Optional[str] = "lead"


class ClientOut(BaseModel):
    id: str
    name: str
    company: str
    email: str
    status: str

    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    client_id: str
    stage: Optional[str] = "intake"
    budget: Optional[float] = 0
    brief: Optional[str] = ""


class ProjectOut(BaseModel):
    id: str
    name: str
    client_name: str
    stage: str
    budget: str

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    project_id: str
    amount: float
    status: Optional[str] = "draft"
    due_date: Optional[date] = None


class InvoiceOut(BaseModel):
    id: str
    project_name: str
    client_name: str
    amount: str
    status: str
    due_date: str

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    active_projects: int
    pipeline_value: str
    overdue_invoices: int
    new_leads: int


class FinancialSummary(BaseModel):
    outstanding: str
    paid_this_month: str
    overdue_count: int
