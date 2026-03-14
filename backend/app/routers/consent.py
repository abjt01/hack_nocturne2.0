"""Consent Service router — grant, revoke, validate, and list consents."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.consent import (
    ConsentGrant,
    ConsentRevoke,
    ConsentValidate,
    ConsentValidateResponse,
    ConsentResponse,
    ConsentGrantResponse,
    ConsentListResponse,
)
from app.services.auth import get_current_hospital, get_current_requester, AuthenticatedHospital, AuthenticatedPatient
from app.services import consent_service
from typing import Annotated

router = APIRouter(prefix="/api/consent", tags=["Consent Service"])


@router.post("/grant", response_model=ConsentGrantResponse, status_code=201)
def grant_consent(
    body: ConsentGrant,
    requester: Annotated[AuthenticatedHospital | AuthenticatedPatient, Depends(get_current_requester)],
    db: Annotated[Session, Depends(get_db)],
):
    """
    Grant consent for an institution to access a patient's records.
    Hospitals grant on behalf of patients; Patients grant directly.
    """
    if isinstance(requester, AuthenticatedPatient):
        if requester.patient_id != body.patient_id:
            raise HTTPException(status_code=403, detail="Patients can only grant consent for themselves")
        grantor = "PATIENT:" + requester.patient_id
    else:
        grantor = requester.hospital_id

    result = consent_service.grant_consent(
        db=db,
        patient_id=body.patient_id,
        granting_institution=grantor,
        requesting_institution=body.institution_id,
        expiry=body.expiry,
    )

    consent = result["consent"]
    audit_event = result.get("audit_event")

    return ConsentGrantResponse(
        consent_id=consent.consent_id,
        patient_id=consent.patient_id,
        granting_institution=consent.granting_institution,
        requesting_institution=consent.requesting_institution,
        status=consent.status,
        granted_at=consent.granted_at,
        expires_at=consent.expires_at,
        audit_event_id=audit_event.event_id if audit_event else None,
        blockchain_hash=audit_event.blockchain_hash if audit_event else None,
    )


@router.post("/revoke")
def revoke_consent(
    body: ConsentRevoke,
    requester: Annotated[AuthenticatedHospital | AuthenticatedPatient, Depends(get_current_requester)],
    db: Annotated[Session, Depends(get_db)],
):
    """Revoke consent for an institution to access a patient's records."""
    if isinstance(requester, AuthenticatedPatient):
        if requester.patient_id != body.patient_id:
            raise HTTPException(status_code=403, detail="Patients can only revoke their own consent")
        grantor = "PATIENT:" + requester.patient_id
    else:
        grantor = requester.hospital_id

    result = consent_service.revoke_consent(
        db=db,
        patient_id=body.patient_id,
        granting_institution=grantor,
        requesting_institution=body.institution_id,
    )

    if not result["revoked"]:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "CONSENT_NOT_FOUND",
                "message": "No active consent found to revoke.",
            },
        )

    consent = result["consent"]
    audit_event = result.get("audit_event")

    return {
        "revoked": True,
        "consent_id": consent.consent_id,
        "patient_id": consent.patient_id,
        "status": consent.status,
        "audit_event_id": audit_event.event_id if audit_event else None,
        "blockchain_hash": audit_event.blockchain_hash if audit_event else None,
    }


@router.post("/validate", response_model=ConsentValidateResponse)
def validate_consent(
    body: ConsentValidate,
    hospital: Annotated[AuthenticatedHospital, Depends(get_current_hospital)],
    db: Annotated[Session, Depends(get_db)],
):
    """Validate whether an institution has active consent for a patient. Restricted to Hospitals."""
    result = consent_service.validate_consent(
        db=db,
        patient_id=body.patient_id,
        institution_id=body.institution_id,
    )
    return ConsentValidateResponse(valid=result["valid"], reason=result["reason"])


@router.get("/{patient_id}", response_model=ConsentListResponse)
def list_consents(
    patient_id: str,
    requester: Annotated[AuthenticatedHospital | AuthenticatedPatient, Depends(get_current_requester)],
    db: Annotated[Session, Depends(get_db)],
):
    """List all active consents for a patient. Patients can only see their own list."""
    if isinstance(requester, AuthenticatedPatient) and requester.patient_id != patient_id:
        raise HTTPException(status_code=403, detail="Patients can only view their own consents")

    consents = consent_service.list_consents(db=db, patient_id=patient_id)
    return ConsentListResponse(
        consents=[ConsentResponse.model_validate(c) for c in consents],
        count=len(consents),
    )

