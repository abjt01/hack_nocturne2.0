"""
FHIR Service — constructs FHIR-like Bundle JSON from patient + observations + encounters.

Uses plain JSON dicts structured like FHIR R4 Bundles (no fhir.resources library).
"""

from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.observation import Observation
from app.models.encounter import Encounter


def build_patient_resource(patient: Patient) -> dict:
    """Build a FHIR-like Patient resource from a Patient model."""
    return {
        "resourceType": "Patient",
        "id": patient.global_id,
        "identifier": [
            {
                "system": f"urn:hospital:{patient.hospital_id}",
                "value": patient.local_patient_id,
            }
        ],
        "name": [
            {
                "use": "official",
                "family": patient.family_name,
                "given": [patient.given_name] if patient.given_name else [],
            }
        ],
        "gender": patient.gender,
        "birthDate": patient.birth_date,
        "telecom": (
            [{"system": "phone", "value": patient.phone}] if patient.phone else []
        ),
        "address": (
            [{"text": patient.address}] if patient.address else []
        ),
    }


def build_observation_resource(obs: Observation) -> dict:
    """Build a FHIR-like Observation resource."""
    resource = {
        "resourceType": "Observation",
        "id": obs.id,
        "status": obs.status,
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": obs.code,
                    "display": obs.display or obs.code,
                }
            ]
        },
        "subject": {"reference": f"Patient/{obs.patient_id}"},
        "effectiveDateTime": obs.effective_date,
    }

    if obs.value is not None:
        resource["valueQuantity"] = {
            "value": obs.value,
            "unit": obs.unit or "",
            "system": "http://unitsofmeasure.org",
        }
    elif obs.value_string:
        resource["valueString"] = obs.value_string

    return resource


def build_encounter_resource(enc: Encounter) -> dict:
    """Build a FHIR-like Encounter resource."""
    resource = {
        "resourceType": "Encounter",
        "id": enc.id,
        "status": enc.status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
            "code": enc.encounter_class or "AMB",
            "display": enc.encounter_class or "ambulatory",
        },
        "subject": {"reference": f"Patient/{enc.patient_id}"},
    }

    if enc.type_code:
        resource["type"] = [
            {
                "coding": [
                    {
                        "code": enc.type_code,
                        "display": enc.type_display or enc.type_code,
                    }
                ]
            }
        ]

    if enc.period_start or enc.period_end:
        resource["period"] = {}
        if enc.period_start:
            resource["period"]["start"] = enc.period_start
        if enc.period_end:
            resource["period"]["end"] = enc.period_end

    if enc.provider:
        resource["participant"] = [
            {
                "individual": {"display": enc.provider}
            }
        ]

    return resource


def build_bundle(db: Session, patient_id: str) -> dict | None:
    """
    Build a FHIR-like Bundle containing Patient + Observation + Encounter resources.
    Returns None if patient not found.
    """
    patient = db.query(Patient).filter(Patient.global_id == patient_id).first()
    if not patient:
        return None

    observations = (
        db.query(Observation)
        .filter(Observation.patient_id == patient_id)
        .all()
    )
    encounters = (
        db.query(Encounter)
        .filter(Encounter.patient_id == patient_id)
        .all()
    )

    entries = []

    # Patient entry
    entries.append({
        "fullUrl": f"urn:uuid:{patient.global_id}",
        "resource": build_patient_resource(patient),
    })

    # Observation entries
    for obs in observations:
        entries.append({
            "fullUrl": f"urn:uuid:{obs.id}",
            "resource": build_observation_resource(obs),
        })

    # Encounter entries
    for enc in encounters:
        entries.append({
            "fullUrl": f"urn:uuid:{enc.id}",
            "resource": build_encounter_resource(enc),
        })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "total": len(entries),
        "entry": entries,
    }


def get_patient_resource(db: Session, patient_id: str) -> dict | None:
    """Get a single FHIR-like Patient resource."""
    patient = db.query(Patient).filter(Patient.global_id == patient_id).first()
    if not patient:
        return None
    return build_patient_resource(patient)
