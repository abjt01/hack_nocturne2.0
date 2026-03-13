"""
Consent Service — manages consent records between institutions for patient data access.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.consent import Consent
from app.services import audit_service


def validate_consent(db: Session, patient_id: str, institution_id: str) -> dict:
    """
    Check if an institution has active consent to access a patient's records.
    Returns { valid: bool, reason: str }.
    """
    consent = (
        db.query(Consent)
        .filter(
            Consent.patient_id == patient_id,
            Consent.requesting_institution == institution_id,
            Consent.status == "active",
        )
        .first()
    )

    if not consent:
        return {"valid": False, "reason": "CONSENT_NOT_FOUND"}

    # Check expiry (use naive UTC for SQLite compatibility)
    if consent.expires_at:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        expires = consent.expires_at.replace(tzinfo=None) if consent.expires_at.tzinfo else consent.expires_at
        if expires < now:
            return {"valid": False, "reason": "CONSENT_EXPIRED"}

    return {"valid": True, "reason": None}


def grant_consent(
    db: Session,
    patient_id: str,
    granting_institution: str,
    requesting_institution: str,
    expiry: str = None,
) -> dict:
    """
    Grant consent for an institution to access a patient's records.
    Logs a CONSENT_UPDATE audit event.
    """
    # Check if active consent already exists
    existing = (
        db.query(Consent)
        .filter(
            Consent.patient_id == patient_id,
            Consent.granting_institution == granting_institution,
            Consent.requesting_institution == requesting_institution,
            Consent.status == "active",
        )
        .first()
    )

    if existing:
        return {
            "consent_id": existing.consent_id,
            "already_exists": True,
            "consent": existing,
        }

    expires_at = None
    if expiry:
        try:
            expires_at = datetime.fromisoformat(expiry.replace("Z", "+00:00"))
        except ValueError:
            expires_at = None

    consent = Consent(
        consent_id=str(uuid.uuid4()),
        patient_id=patient_id,
        granting_institution=granting_institution,
        requesting_institution=requesting_institution,
        expires_at=expires_at,
        status="active",
    )

    db.add(consent)
    db.commit()
    db.refresh(consent)

    # Log audit event
    audit_event = audit_service.log_event(
        db=db,
        event_type="CONSENT_UPDATE",
        actor_hospital_id=granting_institution,
        actor_service="consent-service",
        outcome="SUCCESS",
        subject_patient_id=patient_id,
        resource_type="Consent",
        resource_id=consent.consent_id,
    )

    return {
        "consent_id": consent.consent_id,
        "already_exists": False,
        "consent": consent,
        "audit_event": audit_event,
    }


def revoke_consent(
    db: Session,
    patient_id: str,
    granting_institution: str,
    requesting_institution: str,
) -> dict:
    """
    Revoke consent for an institution.
    Logs a CONSENT_UPDATE audit event.
    """
    consent = (
        db.query(Consent)
        .filter(
            Consent.patient_id == patient_id,
            Consent.granting_institution == granting_institution,
            Consent.requesting_institution == requesting_institution,
            Consent.status == "active",
        )
        .first()
    )

    if not consent:
        # Log failed revocation attempt
        audit_service.log_event(
            db=db,
            event_type="CONSENT_UPDATE",
            actor_hospital_id=granting_institution,
            actor_service="consent-service",
            outcome="FAILURE",
            subject_patient_id=patient_id,
            resource_type="Consent",
            failure_reason="CONSENT_NOT_FOUND",
        )
        return {"revoked": False, "reason": "CONSENT_NOT_FOUND"}

    consent.status = "revoked"
    db.commit()
    db.refresh(consent)

    # Log audit event
    audit_event = audit_service.log_event(
        db=db,
        event_type="CONSENT_UPDATE",
        actor_hospital_id=granting_institution,
        actor_service="consent-service",
        outcome="SUCCESS",
        subject_patient_id=patient_id,
        resource_type="Consent",
        resource_id=consent.consent_id,
    )

    return {
        "revoked": True,
        "consent": consent,
        "audit_event": audit_event,
    }


def list_consents(db: Session, patient_id: str) -> list[Consent]:
    """List all active consents for a patient."""
    return (
        db.query(Consent)
        .filter(Consent.patient_id == patient_id, Consent.status == "active")
        .all()
    )
