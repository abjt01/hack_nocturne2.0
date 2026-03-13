"""MPI (Master Patient Index) router — patient identity resolution."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.mpi import MPIRegister, MPIRegisterResponse, MPIRecordResponse, MPIIdentity
from app.services.auth import get_current_hospital, AuthenticatedHospital
from app.services import mpi_service

router = APIRouter(prefix="/api/mpi", tags=["Master Patient Index"])


@router.post("/register", response_model=MPIRegisterResponse, status_code=201)
def register_identity(
    body: MPIRegister,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Register a patient identity mapping in the MPI."""
    result = mpi_service.register_patient(
        db=db,
        hospital_id=body.hospital_id,
        local_patient_id=body.local_patient_id,
        global_patient_id=body.global_patient_id,
    )
    return MPIRegisterResponse(
        global_patient_id=result["global_patient_id"],
        hospital_id=result["hospital_id"],
        local_patient_id=result["local_patient_id"],
    )


@router.get("/resolve")
def resolve_identity(
    hospital_id: str = Query(...),
    local_patient_id: str = Query(...),
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Resolve a global patient UUID from hospital ID + local patient ID."""
    global_id = mpi_service.resolve_patient(
        db=db,
        hospital_id=hospital_id,
        local_patient_id=local_patient_id,
    )
    if not global_id:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No MPI record for hospital '{hospital_id}' patient '{local_patient_id}'.",
            },
        )
    return {"global_patient_id": global_id}


@router.get("/{global_patient_id}", response_model=MPIRecordResponse)
def get_identities(
    global_patient_id: str,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Get all hospital identity mappings for a global patient UUID."""
    identities = mpi_service.get_identities(db=db, global_patient_id=global_patient_id)
    if not identities:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No MPI records for global patient ID '{global_patient_id}'.",
            },
        )
    return MPIRecordResponse(
        global_patient_id=global_patient_id,
        identities=[MPIIdentity(**i) for i in identities],
    )
