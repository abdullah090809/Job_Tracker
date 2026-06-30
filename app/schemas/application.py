from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    company: str
    role: str
    status: ApplicationStatus = ApplicationStatus.applied
    applied_date: date
    jd_text: Optional[str] = None
    notes: Optional[str] = None


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    role: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    applied_date: Optional[date] = None
    jd_text: Optional[str] = None
    notes: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    user_id: int
    company: str
    role: str
    status: ApplicationStatus
    applied_date: date
    jd_text: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}