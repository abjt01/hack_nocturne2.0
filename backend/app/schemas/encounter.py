from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class EncounterCreate(BaseModel):
    patient_id: str
    encounter_class: Optional[str] = None
    type_code: Optional[str] = None
    type_display: Optional[str] = None
    status: Optional[str] = "finished"
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    provider: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class EncounterResponse(BaseModel):
    id: str
    patient_id: str
    encounter_class: Optional[str] = None
    type_code: Optional[str] = None
    type_display: Optional[str] = None
    status: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    provider: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
