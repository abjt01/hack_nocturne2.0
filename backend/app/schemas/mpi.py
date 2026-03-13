from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MPIRegister(BaseModel):
    hospital_id: str
    local_patient_id: str
    global_patient_id: Optional[str] = None  # auto-generated if not provided


class MPIResolveQuery(BaseModel):
    hospital_id: str
    local_patient_id: str


class MPIIdentity(BaseModel):
    hospital_id: str
    local_patient_id: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MPIRecordResponse(BaseModel):
    global_patient_id: str
    identities: list[MPIIdentity]


class MPIRegisterResponse(BaseModel):
    global_patient_id: str
    hospital_id: str
    local_patient_id: str
