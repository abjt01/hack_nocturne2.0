"""
Authentication dependency for the API Layer.

Validates X-Hospital-ID and X-API-Key headers against the Hospital Registry.
Returns the authenticated hospital record to downstream handlers.
"""

from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hospital import Hospital


class AuthenticatedHospital:
    """Holds the authenticated hospital info for downstream use."""

    def __init__(self, hospital_id: str, hospital_name: str):
        self.hospital_id = hospital_id
        self.hospital_name = hospital_name


async def get_current_hospital(
    x_hospital_id: str = Header(None, alias="X-Hospital-ID"),
    x_api_key: str = Header(None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> AuthenticatedHospital:
    """
    FastAPI dependency that validates X-Hospital-ID and X-API-Key headers.
    Returns AuthenticatedHospital on success, raises 401 on failure.
    """
    if not x_hospital_id or not x_api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": True,
                "code": "INVALID_TOKEN",
                "message": "Missing X-Hospital-ID or X-API-Key header.",
            },
        )

    hospital = db.query(Hospital).filter(Hospital.id == x_hospital_id).first()

    if not hospital:
        raise HTTPException(
            status_code=401,
            detail={
                "error": True,
                "code": "UNKNOWN_HOSPITAL",
                "message": f"Hospital '{x_hospital_id}' not found in registry.",
            },
        )

    if hospital.api_key != x_api_key:
        raise HTTPException(
            status_code=401,
            detail={
                "error": True,
                "code": "INVALID_TOKEN",
                "message": "Invalid API key for this hospital.",
            },
        )

    return AuthenticatedHospital(
        hospital_id=hospital.id,
        hospital_name=hospital.name,
    )
