"""
MPI (Master Patient Index) Service — manages global UUID <-> hospital local ID mappings.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.mpi import MPIRecord


def register_patient(
    db: Session,
    hospital_id: str,
    local_patient_id: str,
    global_patient_id: str = None,
) -> dict:
    """
    Register a patient identity in the MPI.
    If global_patient_id is provided, use it. Otherwise generate a new UUID.
    Returns { global_patient_id, hospital_id, local_patient_id }.
    """
    if not global_patient_id:
        global_patient_id = str(uuid.uuid4())

    # Check if this mapping already exists
    existing = (
        db.query(MPIRecord)
        .filter(
            MPIRecord.hospital_id == hospital_id,
            MPIRecord.local_patient_id == local_patient_id,
        )
        .first()
    )

    if existing:
        return {
            "global_patient_id": existing.global_patient_id,
            "hospital_id": hospital_id,
            "local_patient_id": local_patient_id,
            "already_exists": True,
        }

    record = MPIRecord(
        global_patient_id=global_patient_id,
        hospital_id=hospital_id,
        local_patient_id=local_patient_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "global_patient_id": global_patient_id,
        "hospital_id": hospital_id,
        "local_patient_id": local_patient_id,
        "already_exists": False,
    }


def resolve_patient(
    db: Session,
    hospital_id: str,
    local_patient_id: str,
) -> str | None:
    """
    Resolve a global patient UUID from hospital ID + local patient ID.
    Returns the global_patient_id or None if not found.
    """
    record = (
        db.query(MPIRecord)
        .filter(
            MPIRecord.hospital_id == hospital_id,
            MPIRecord.local_patient_id == local_patient_id,
        )
        .first()
    )
    return record.global_patient_id if record else None


def get_identities(db: Session, global_patient_id: str) -> list[dict]:
    """
    Get all hospital identity mappings for a global patient UUID.
    """
    records = (
        db.query(MPIRecord)
        .filter(MPIRecord.global_patient_id == global_patient_id)
        .all()
    )
    return [
        {
            "hospital_id": r.hospital_id,
            "local_patient_id": r.local_patient_id,
            "created_at": r.created_at,
        }
        for r in records
    ]
