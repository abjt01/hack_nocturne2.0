"""
Audit Service — logs events, computes SHA-256 hashes, and verifies integrity.

Replaces the blockchain audit service from the original design with
local SHA-256 hashing stored in SQLite.
"""

import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.audit import AuditEvent


def compute_hash(event_id: str, patient_id: str, hospital_id: str, timestamp: str) -> str:
    """
    Compute SHA-256 hash from event fields.
    Hash input = event_id + patient_id + hospital_id + timestamp
    """
    hash_input = f"{event_id}{patient_id}{hospital_id}{timestamp}"
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


def log_event(
    db: Session,
    event_type: str,
    actor_hospital_id: str,
    actor_service: str,
    outcome: str,
    subject_patient_id: str = None,
    resource_type: str = None,
    resource_id: str = None,
    failure_reason: str = None,
) -> AuditEvent:
    """
    Create and store an audit event with SHA-256 hash.
    Returns the created AuditEvent.
    """
    event_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).replace(tzinfo=None)
    timestamp_str = timestamp.isoformat()

    # Compute blockchain hash
    blockchain_hash = compute_hash(
        event_id=event_id,
        patient_id=subject_patient_id or "",
        hospital_id=actor_hospital_id,
        timestamp=timestamp_str,
    )

    event = AuditEvent(
        event_id=event_id,
        event_type=event_type,
        timestamp=timestamp,
        actor_hospital_id=actor_hospital_id,
        actor_service=actor_service,
        subject_patient_id=subject_patient_id,
        resource_type=resource_type,
        resource_id=resource_id,
        outcome=outcome,
        failure_reason=failure_reason,
        blockchain_hash=blockchain_hash,
        tx_hash=None,  # No blockchain in this version
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def verify_event(db: Session, event_id: str) -> dict:
    """
    Verify an audit event's hash integrity.
    Recomputes the hash from stored fields and compares to stored hash.
    """
    event = db.query(AuditEvent).filter(AuditEvent.event_id == event_id).first()
    if not event:
        return {
            "event_id": event_id,
            "verified": False,
            "local_hash": None,
            "stored_hash": None,
            "message": "Event not found.",
        }

    # Recompute hash from stored fields
    recomputed_hash = compute_hash(
        event_id=event.event_id,
        patient_id=event.subject_patient_id or "",
        hospital_id=event.actor_hospital_id,
        timestamp=event.timestamp.isoformat() if event.timestamp else "",
    )

    verified = recomputed_hash == event.blockchain_hash

    return {
        "event_id": event_id,
        "verified": verified,
        "local_hash": recomputed_hash,
        "stored_hash": event.blockchain_hash,
        "message": "Hash verified — integrity intact." if verified else "Hash mismatch — possible tampering detected.",
    }


def list_events(
    db: Session,
    patient_id: str = None,
    event_type: str = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditEvent]:
    """List audit events with optional filters."""
    query = db.query(AuditEvent)
    if patient_id:
        query = query.filter(AuditEvent.subject_patient_id == patient_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    return query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
