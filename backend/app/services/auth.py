"""
Authentication dependency for the API Layer.

Validates X-Hospital-ID and X-API-Key headers against the Hospital Registry.
Returns the authenticated hospital record to downstream handlers.
"""

from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from app.database import get_db
from app.models.hospital import Hospital
from app.security import Role, get_current_role


class AuthenticatedHospital:
    """Holds the authenticated hospital info for downstream use."""
    def __init__(self, hospital_id: str, hospital_name: str):
        self.hospital_id = hospital_id
        self.hospital_name = hospital_name

class AuthenticatedPatient:
    """Holds the authenticated patient info for downstream use."""
    def __init__(self, patient_id: str):
        self.patient_id = patient_id

async def get_current_hospital(
    requester: Annotated[dict, Depends(get_current_role)],
    db: Session = Depends(get_db),
) -> AuthenticatedHospital:
    """
    Dependency that ensures the requester is a valid Hospital.
    """
    if requester["role"] != Role.HOSPITAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires a Hospital role"
        )
    
    hospital_id = requester["id"]
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()

    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Hospital '{hospital_id}' not found in registry.",
        )

    # In a real app, we would validate the API Key here again if not done in security.py
    return AuthenticatedHospital(
        hospital_id=hospital.id,
        hospital_name=hospital.name,
    )

async def get_current_requester(
    requester: Annotated[dict, Depends(get_current_role)],
) -> AuthenticatedHospital | AuthenticatedPatient:
    """
    Dependency that returns either a Hospital or Patient requester.
    """
    if requester["role"] == Role.HOSPITAL:
        # Note: This is a simplified version, ideally it should also validate hospital in DB
        return AuthenticatedHospital(hospital_id=requester["id"], hospital_name="Unknown Hospital")
    
    return AuthenticatedPatient(patient_id=requester["id"])

