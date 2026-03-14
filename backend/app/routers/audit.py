"""Audit router — list events, verify hash integrity."""

from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.audit import AuditEventResponse, AuditEventListResponse, AuditVerifyResponse
from app.services.auth import get_current_hospital, get_current_requester, AuthenticatedHospital, AuthenticatedPatient
from app.services import audit_service
from typing import Annotated

router = APIRouter(prefix="/api/audit", tags=["Audit Service"])


@router.get("/events", response_model=AuditEventListResponse)
def list_audit_events(
    requester: Annotated[AuthenticatedHospital | AuthenticatedPatient, Depends(get_current_requester)],
    db: Annotated[Session, Depends(get_db)],
    patient_id: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """List audit events. Patients can only see their own history."""
    if isinstance(requester, AuthenticatedPatient):
        if patient_id and patient_id != requester.patient_id:
            raise HTTPException(status_code=403, detail="Patients can only view their own history")
        patient_id = requester.patient_id

    events = audit_service.list_events(
        db=db,
        patient_id=patient_id,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )
    return AuditEventListResponse(
        events=[AuditEventResponse.model_validate(e) for e in events],
        count=len(events),
    )


@router.get("/verify/{event_id}", response_model=AuditVerifyResponse)
def verify_audit_event(
    event_id: str,
    hospital: Annotated[AuthenticatedHospital, Depends(get_current_hospital)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Verify an audit event's hash integrity. Restricted to Hospitals.
    """
    result = audit_service.verify_event(db=db, event_id=event_id)
    return AuditVerifyResponse(**result)


class AuditLogRequest(BaseModel):
    """Payload accepted from trusted microservices to log an audit event."""
    event_type: str
    actor_hospital_id: str
    actor_service: str
    outcome: str
    subject_patient_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    failure_reason: Optional[str] = None
    dedup_key: Optional[str] = None


@router.post("/log", response_model=AuditEventResponse, status_code=201)
def log_audit_event(
    body: AuditLogRequest,
    hospital: Annotated[AuthenticatedHospital, Depends(get_current_hospital)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Accept an audit event from a trusted microservice. Restricted to Hospitals.
    """
    failure_reason = body.failure_reason
    if not failure_reason and body.dedup_key:
        failure_reason = f"dedup:{body.dedup_key}"

    event = audit_service.log_event(
        db=db,
        event_type=body.event_type,
        actor_hospital_id=body.actor_hospital_id,
        actor_service=body.actor_service,
        outcome=body.outcome,
        subject_patient_id=body.subject_patient_id,
        resource_type=body.resource_type,
        resource_id=body.resource_id,
        failure_reason=failure_reason,
    )
    return AuditEventResponse.model_validate(event)

