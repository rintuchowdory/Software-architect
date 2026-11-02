from datetime import date
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class PasswordLoginRequest(BaseModel):
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
    open_value: Optional[str] = None

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
    has_brief: bool = False

    class Config:
        from_attributes = True


class InvoiceCreate(BaseModel):
    project_id: str
    amount: float
    tax_rate: Optional[float] = None
    status: Optional[str] = "draft"
    due_date: Optional[date] = None
    notes: Optional[str] = ""


class InvoiceUpdate(BaseModel):
    status: Optional[str] = None
    amount: Optional[float] = None
    tax_rate: Optional[float] = None
    due_date: Optional[date] = None
    notes: Optional[str] = None


class InvoiceOut(BaseModel):
    id: str
    number: str
    project_id: str
    project_name: str
    client_name: str
    client_company: str
    client_email: str
    amount: str          # net, formatted
    tax_rate: float
    tax_amount: str
    total: str           # gross, formatted
    status: str
    due_date: str
    paid_at: str
    days_overdue: int
    notes: str


class DashboardStats(BaseModel):
    active_projects: int
    pipeline_value: str
    overdue_invoices: int
    new_leads: int


class FinancialSummary(BaseModel):
    outstanding: str
    paid_this_month: str
    overdue_count: int
    overdue_amount: str = "0 €"


class PipelineStage(BaseModel):
    stage: str
    count: int
    value: str
    value_raw: float


class RevenuePoint(BaseModel):
    month: str
    label: str
    value: float


class OverdueItem(BaseModel):
    id: str
    number: str
    project_name: str
    client_name: str
    total: str
    days_overdue: int


class ActionItem(BaseModel):
    id: str
    title: str
    detail: str
    kind: str      # money | sales | delivery
    href: str
    priority: int


class DashboardOverview(BaseModel):
    active_projects: int
    pipeline_value: str
    outstanding: str
    paid_this_month: str
    overdue_invoices: int
    overdue_amount: str
    new_leads: int
    avg_project_value: str
    billable_hours_estimate: int
    revenue_series: List[RevenuePoint]
    pipeline: List[PipelineStage]
    overdue: List[OverdueItem]
    actions: List[ActionItem]


class IntakeRequest(BaseModel):
    project_type: str = "website"
    goal: str = ""
    features: List[str] = Field(default_factory=list)
    timeline: str = ""
    budget: str = ""
    existing: str = ""
    notes: str = ""
    client_name: str = ""
    company: str = ""
    email: EmailStr
    project_name: str = ""


class IntakeResponse(BaseModel):
    project_id: str
    title: str
    brief: str
    hours: int
    estimate_low: str
    estimate_high: str
