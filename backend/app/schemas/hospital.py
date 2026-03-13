from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class HospitalCreate(BaseModel):
    id: str  # e.g. HOSP_001
    name: str
    api_key: str


class HospitalResponse(BaseModel):
    id: str
    name: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class HospitalListResponse(BaseModel):
    hospitals: list[HospitalResponse]
    count: int
