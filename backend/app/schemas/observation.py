from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ObservationCreate(BaseModel):
    patient_id: str  # global patient UUID
    code: str
    display: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    value_string: Optional[str] = None
    effective_date: Optional[str] = None
    status: Optional[str] = "final"
    data: Optional[dict[str, Any]] = None


class ObservationResponse(BaseModel):
    id: str
    patient_id: str
    code: str
    display: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    value_string: Optional[str] = None
    effective_date: Optional[str] = None
    status: str
    data: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
