"""Hospital Registry router — CRUD for hospital records."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.hospital import Hospital
from app.schemas.hospital import (
    HospitalCreate,
    HospitalResponse,
    HospitalListResponse,
)

router = APIRouter(prefix="/api/hospitals", tags=["Hospital Registry"])


@router.get("", response_model=HospitalListResponse)
def list_hospitals(db: Session = Depends(get_db)):
    """List all registered hospitals."""
    hospitals = db.query(Hospital).all()
    return HospitalListResponse(
        hospitals=[HospitalResponse.model_validate(h) for h in hospitals],
        count=len(hospitals),
    )


@router.post("", response_model=HospitalResponse, status_code=201)
def register_hospital(body: HospitalCreate, db: Session = Depends(get_db)):
    """Register a new hospital in the registry."""
    existing = db.query(Hospital).filter(Hospital.id == body.id).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail={
                "error": True,
                "code": "HOSPITAL_EXISTS",
                "message": f"Hospital '{body.id}' already exists.",
            },
        )

    hospital = Hospital(id=body.id, name=body.name, api_key=body.api_key)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return HospitalResponse.model_validate(hospital)


@router.get("/{hospital_id}", response_model=HospitalResponse)
def get_hospital(hospital_id: str, db: Session = Depends(get_db)):
    """Get a hospital by ID."""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "UNKNOWN_HOSPITAL",
                "message": f"Hospital '{hospital_id}' not found.",
            },
        )
    return HospitalResponse.model_validate(hospital)
