from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditEventCreate(BaseModel):
    event_type: str  # DATA_ACCESS | CONSENT_UPDATE | ACCESS_DENIED
    actor_hospital_id: str
    actor_service: str
    subject_patient_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    outcome: str  # SUCCESS | FAILURE
    failure_reason: Optional[str] = None


class AuditEventResponse(BaseModel):
    event_id: str
    event_type: str
    timestamp: Optional[datetime] = None
    actor_hospital_id: str
    actor_service: str
    subject_patient_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    outcome: str
    failure_reason: Optional[str] = None
    blockchain_hash: Optional[str] = None
    tx_hash: Optional[str] = None

    class Config:
        from_attributes = True


class AuditEventListResponse(BaseModel):
    events: list[AuditEventResponse]
    count: int


class AuditVerifyResponse(BaseModel):
    event_id: str
    verified: bool
    local_hash: Optional[str] = None
    stored_hash: Optional[str] = None
    message: str
