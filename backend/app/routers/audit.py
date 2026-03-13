"""Audit router — list events, verify hash integrity."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.audit import AuditEventResponse, AuditEventListResponse, AuditVerifyResponse
from app.services.auth import get_current_hospital, AuthenticatedHospital
from app.services import audit_service

router = APIRouter(prefix="/api/audit", tags=["Audit Service"])


@router.get("/events", response_model=AuditEventListResponse)
def list_audit_events(
    patient_id: str = Query(None),
    event_type: str = Query(None),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """List audit events with optional filters."""
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
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """
    Verify an audit event's hash integrity.
    Recomputes hash from stored fields and compares to stored hash.
    """
    result = audit_service.verify_event(db=db, event_id=event_id)
    return AuditVerifyResponse(**result)
