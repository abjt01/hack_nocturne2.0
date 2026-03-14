"""
FHIR router — consent-gated patient data access and FHIR Bundle retrieval.

Implements the core data access workflow:
1. Auth check (via dependency)
2. Consent check
3. Data retrieval
4. Audit logging (success or failure)
"""

import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient
from app.models.observation import Observation
from app.models.encounter import Encounter
from app.schemas.patient import PatientIngest, PatientIngestResponse
from app.schemas.observation import ObservationCreate, ObservationResponse
from app.services.auth import get_current_hospital, get_current_requester, AuthenticatedHospital, AuthenticatedPatient
from app.services import consent_service, audit_service, fhir_service, mpi_service
from typing import Annotated

logger = logging.getLogger("backend.fhir")
logger.setLevel(logging.INFO)

router = APIRouter(prefix="/api", tags=["FHIR Service"])


def _consent_gate(db: Session, patient_id: str, requester: AuthenticatedHospital | AuthenticatedPatient):
    """
    Shared consent check logic. If Patient role, checks ownership. If Hospital, checks consent.
    """
    if isinstance(requester, AuthenticatedPatient):
        if requester.patient_id != patient_id:
             raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Patients can only access their own records"
            )
        return

    hospital = requester
    # Check if the requesting hospital owns the patient (same hospital = no consent needed)
    patient = db.query(Patient).filter(Patient.global_id == patient_id).first()
    if patient and patient.hospital_id == hospital.hospital_id:
        return  # Same hospital, no consent needed

    validation = consent_service.validate_consent(
        db=db,
        patient_id=patient_id,
        institution_id=hospital.hospital_id,
    )

    if not validation.get("valid", False):
        # Log ACCESS_DENIED event
        event = audit_service.log_event(
            db=db,
            event_type="ACCESS_DENIED",
            actor_hospital_id=hospital.hospital_id,
            actor_service="fhir-service",
            outcome="FAILURE",
            subject_patient_id=patient_id,
            resource_type="Patient",
            resource_id=patient_id,
            failure_reason=validation.get("reason"),
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": True,
                "code": validation.get("reason", "CONSENT_DENIED"),
                "message": f"Access denied: {validation.get('reason', 'consent check failed')}",
                "event_id": getattr(event, "event_id", None),
            },
        )


@router.get("/patient/{patient_id}")
def get_patient_resource(
    patient_id: str,
    requester: AuthenticatedHospital | AuthenticatedPatient = Depends(get_current_requester),
    db: Session = Depends(get_db),
):
    """
    Get a FHIR Patient resource by global patient ID.
    Consent-gated for cross-hospital access; implicit for Patients.
    """
    # Consent check
    _consent_gate(db, patient_id, requester)

    resource = fhir_service.get_patient_resource(db, patient_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No record for global patient ID '{patient_id}'.",
            },
        )

    # Log DATA_ACCESS event
    actor_id = requester.hospital_id if isinstance(requester, AuthenticatedHospital) else "PATIENT:" + requester.patient_id
    audit_service.log_event(
        db=db,
        event_type="DATA_ACCESS",
        actor_hospital_id=actor_id,
        actor_service="fhir-service",
        outcome="SUCCESS",
        subject_patient_id=patient_id,
        resource_type="Patient",
        resource_id=patient_id,
    )

    return resource


@router.get("/bundle/{patient_id}")
def get_bundle(
    patient_id: str,
    requester: AuthenticatedHospital | AuthenticatedPatient = Depends(get_current_requester),
    db: Session = Depends(get_db),
):
    """
    Get a full FHIR Bundle for a patient.
    Consent-gated for cross-hospital access; implicit for Patients.
    """
    # Consent check
    _consent_gate(db, patient_id, requester)

    bundle = fhir_service.build_bundle(db, patient_id)
    if not bundle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": True,
                "code": "PATIENT_NOT_FOUND",
                "message": f"No record for global patient ID '{patient_id}'.",
            },
        )

    # Log DATA_ACCESS event
    actor_id = requester.hospital_id if isinstance(requester, AuthenticatedHospital) else "PATIENT:" + requester.patient_id
    audit_service.log_event(
        db=db,
        event_type="DATA_ACCESS",
        actor_hospital_id=actor_id,
        actor_service="fhir-service",
        outcome="SUCCESS",
        subject_patient_id=patient_id,
        resource_type="Bundle",
        resource_id=patient_id,
    )

    return bundle


@router.get("/observation/{observation_id}")
def get_observation(
    observation_id: str,
    requester: AuthenticatedHospital | AuthenticatedPatient = Depends(get_current_requester),
    db: Session = Depends(get_db),
):
    """Get a FHIR Observation resource by ID."""
    obs = db.query(Observation).filter(Observation.id == observation_id).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": True,
                "code": "OBSERVATION_NOT_FOUND",
                "message": f"Observation '{observation_id}' not found.",
            },
        )

    # Consent check on the patient
    _consent_gate(db, obs.patient_id, requester)

    resource = fhir_service.build_observation_resource(obs)

    actor_id = requester.hospital_id if isinstance(requester, AuthenticatedHospital) else "PATIENT:" + requester.patient_id
    audit_service.log_event(
        db=db,
        event_type="DATA_ACCESS",
        actor_hospital_id=actor_id,
        actor_service="fhir-service",
        outcome="SUCCESS",
        subject_patient_id=obs.patient_id,
        resource_type="Observation",
        resource_id=observation_id,
    )

    return resource


@router.get("/encounter/{encounter_id}")
def get_encounter_resource(
    encounter_id: str,
    requester: AuthenticatedHospital | AuthenticatedPatient = Depends(get_current_requester),
    db: Session = Depends(get_db),
):
    """Get a FHIR Encounter resource by ID."""
    enc = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not enc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": True,
                "code": "ENCOUNTER_NOT_FOUND",
                "message": f"Encounter '{encounter_id}' not found.",
            },
        )

    # Consent check on the owning patient
    _consent_gate(db, enc.patient_id, requester)

    resource = fhir_service.build_encounter_resource(enc)

    actor_id = requester.hospital_id if isinstance(requester, AuthenticatedHospital) else "PATIENT:" + requester.patient_id
    audit_service.log_event(
        db=db,
        event_type="DATA_ACCESS",
        actor_hospital_id=actor_id,
        actor_service="fhir-service",
        outcome="SUCCESS",
        subject_patient_id=enc.patient_id,
        resource_type="Encounter",
        resource_id=encounter_id,
    )

    return resource


@router.post("/observation", status_code=status.HTTP_201_CREATED)
def create_observation(
    body: ObservationCreate,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """Create a new Observation resource. Restricted to Hospitals."""
    obs = Observation(
        id=str(uuid.uuid4()),
        patient_id=body.patient_id,
        code=body.code,
        display=body.display,
        value=body.value,
        unit=body.unit,
        value_string=body.value_string,
        effective_date=body.effective_date,
        status=body.status or "final",
        data=body.data,
    )
    db.add(obs)
    db.commit()
    db.refresh(obs)

    return ObservationResponse.model_validate(obs)


@router.post("/patient/ingest", status_code=status.HTTP_201_CREATED)
def ingest_patient(
    body: PatientIngest,
    hospital: AuthenticatedHospital = Depends(get_current_hospital),
    db: Session = Depends(get_db),
):
    """
    Ingest raw hospital patient data. Restricted to Hospitals.
    """
    global_id = str(uuid.uuid4())

    # Create patient record
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
    )
    db.add(patient)

    # Register in MPI
    mpi_service.register_patient(
        db=db,
        hospital_id=hospital.hospital_id,
        local_patient_id=body.local_patient_id,
        global_patient_id=global_id,
    )

    # Create observations
    obs_count = 0
    if body.observations:
        for obs_data in body.observations:
            obs = Observation(
                id=str(uuid.uuid4()),
                patient_id=global_id,
                code=obs_data.get("code", "unknown"),
                display=obs_data.get("display"),
                value=obs_data.get("value"),
                unit=obs_data.get("unit"),
                value_string=obs_data.get("value_string"),
                effective_date=obs_data.get("effective_date"),
                status=obs_data.get("status", "final"),
                data=obs_data,
            )
            db.add(obs)
            obs_count += 1

    # Create encounters
    enc_count = 0
    if body.encounters:
        for enc_data in body.encounters:
            enc = Encounter(
                id=str(uuid.uuid4()),
                patient_id=global_id,
                encounter_class=enc_data.get("class"),
                type_code=enc_data.get("type_code"),
                type_display=enc_data.get("type_display"),
                status=enc_data.get("status", "finished"),
                period_start=enc_data.get("period_start"),
                period_end=enc_data.get("period_end"),
                provider=enc_data.get("provider"),
                data=enc_data,
            )
            db.add(enc)
            enc_count += 1

    try:
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("DB commit failed during patient ingest")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": True, "code": "DB_COMMIT_FAILED", "message": "Failed to persist patient data."},
        )

    fhir_patient = fhir_service.build_patient_resource(patient)

    audit_service.log_event(
        db=db,
        event_type="DATA_ACCESS",
        actor_hospital_id=hospital.hospital_id,
        actor_service="fhir-service",
        outcome="SUCCESS",
        subject_patient_id=global_id,
        resource_type="Patient",
        resource_id=global_id,
    )

    return PatientIngestResponse(
        global_id=global_id,
        hospital_id=hospital.hospital_id,
        patient=fhir_patient,
        observations_created=obs_count,
        encounters_created=enc_count,
    )