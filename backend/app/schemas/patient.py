from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class PatientCreate(BaseModel):
    local_patient_id: str
    given_name: str
    family_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class PatientResponse(BaseModel):
    global_id: str
    hospital_id: str
    local_patient_id: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    data: Optional[dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class PatientListResponse(BaseModel):
    patients: list[PatientResponse]
    count: int


class PatientIngest(BaseModel):
    """Raw hospital data for ingestion — creates patient + observations + encounters."""
    local_patient_id: str
    given_name: str
    family_name: str
    birth_date: Optional[str] = None
    gender: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    observations: Optional[list[dict[str, Any]]] = None
    encounters: Optional[list[dict[str, Any]]] = None


class PatientIngestResponse(BaseModel):
    global_id: str
    hospital_id: str
    patient: dict[str, Any]
    observations_created: int
    encounters_created: int
