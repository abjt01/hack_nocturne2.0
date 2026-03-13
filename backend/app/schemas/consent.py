from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConsentGrant(BaseModel):
    patient_id: str
    institution_id: str  # requesting institution
    expiry: Optional[str] = None  # ISO-8601 datetime or null


class ConsentRevoke(BaseModel):
    patient_id: str
    institution_id: str


class ConsentValidate(BaseModel):
    patient_id: str
    institution_id: str


class ConsentValidateResponse(BaseModel):
    valid: bool
    reason: Optional[str] = None


class ConsentResponse(BaseModel):
    consent_id: str
    patient_id: str
    granting_institution: str
    requesting_institution: str
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    status: str

    class Config:
        from_attributes = True


class ConsentGrantResponse(BaseModel):
    consent_id: str
    patient_id: str
    granting_institution: str
    requesting_institution: str
    status: str
    granted_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    audit_event_id: Optional[str] = None
    blockchain_hash: Optional[str] = None


class ConsentListResponse(BaseModel):
    consents: list[ConsentResponse]
    count: int
