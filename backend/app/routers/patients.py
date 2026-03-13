"""Patient Data Service router — CRUD for patient records."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientUpdate,
    PatientListResponse,
)
from app.services.auth import get_current_hospital, AuthenticatedHospital
from app.services import mpi_service

router = APIRouter(prefix="/api/patients", tags=["Patient Data Service"])


@router.get("", response_model=PatientListResponse)
def list_patients(
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """List all patients for the authenticated hospital."""
    patients = (
        db.query(Patient).filter(Patient.hospital_id == hospital.hospital_id).all()
    )
    return PatientListResponse(
        patients=[PatientResponse.model_validate(p) for p in patients],
        count=len(patients),
    )


@router.post("", response_model=PatientResponse, status_code=201)
def create_patient(
    body: PatientCreate,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Create a new patient record and register in MPI."""
    global_id = str(uuid.uuid4())

    patient = Patient(
        global_id=global_id,
        hospital_id=hospital.hospital_id,
        local_patient_id=body.local_patient_id,
        given_name=body.given_name,
        family_name=body.family_name,
        birth_date=body.birth_date,
        gender=body.gender,
        phone=body.phone,
        address=body.address,
        data=body.data,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)

    # Register in MPI
    mpi_service.register_patient(
        db=db,
        hospital_id=hospital.hospital_id,
        local_patient_id=body.local_patient_id,
        global_patient_id=global_id,
    )

    return PatientResponse.model_validate(patient)


@router.get("/{global_id}", response_model=PatientResponse)
def get_patient(
    global_id: str,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Get a patient by global UUID."""
    patient = db.query(Patient).filter(Patient.global_id == global_id).first()
    if not patient:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No record for global patient ID '{global_id}'.",
            },
        )
    return PatientResponse.model_validate(patient)


@router.put("/{global_id}", response_model=PatientResponse)
def update_patient(
    global_id: str,
    body: PatientUpdate,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Update a patient record."""
    patient = db.query(Patient).filter(Patient.global_id == global_id).first()
    if not patient:
        raise HTTPException(
            status_code=404,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No record for global patient ID '{global_id}'.",
            },
        )

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return PatientResponse.model_validate(patient)
