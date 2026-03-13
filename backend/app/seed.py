"""
Seed script — populates the database with demo data for testing.

Run: python -m app.seed
"""

import uuid
from datetime import datetime, timezone, timedelta

from app.database import SessionLocal, create_tables

# Import models
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.mpi import MPIRecord
from app.models.consent import Consent
from app.models.observation import Observation
from app.models.encounter import Encounter

# Import services
from app.services import audit_service


def seed():
    create_tables()
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Hospital).first()
        if existing:
            print("Database already seeded. Drop healthcare.db and re-run to re-seed.")
            return

        print("Seeding database...")

        # ── 1. Hospitals ──────────────────────────────────────────
        hospitals = [
            Hospital(id="HOSP_001", name="Apollo Delhi", api_key="key_001"),
            Hospital(id="HOSP_002", name="Max Mumbai", api_key="key_002"),
            Hospital(id="HOSP_003", name="Fortis Bangalore", api_key="key_003"),
        ]
        db.add_all(hospitals)
        db.flush()
        print(f"  ✓ {len(hospitals)} hospitals created")

        # ── 2. Patients ───────────────────────────────────────────
        patients_data = [
            # Hospital 1 — Apollo Delhi
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_001",
                "local_patient_id": "APL-001",
                "given_name": "Rahul",
                "family_name": "Sharma",
                "birth_date": "1985-03-15",
                "gender": "male",
                "phone": "+91-9876543210",
                "address": "42 Connaught Place, New Delhi",
            },
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_001",
                "local_patient_id": "APL-002",
                "given_name": "Priya",
                "family_name": "Patel",
                "birth_date": "1992-07-22",
                "gender": "female",
                "phone": "+91-9876543211",
                "address": "15 Hauz Khas, New Delhi",
            },
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_001",
                "local_patient_id": "APL-003",
                "given_name": "Amit",
                "family_name": "Kumar",
                "birth_date": "1978-11-05",
                "gender": "male",
                "phone": "+91-9876543212",
                "address": "88 Dwarka Sector 7, New Delhi",
            },
            # Hospital 2 — Max Mumbai
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_002",
                "local_patient_id": "MAX-001",
                "given_name": "Sneha",
                "family_name": "Desai",
                "birth_date": "1990-01-10",
                "gender": "female",
                "phone": "+91-9876543213",
                "address": "7 Bandra West, Mumbai",
            },
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_002",
                "local_patient_id": "MAX-002",
                "given_name": "Vikram",
                "family_name": "Singh",
                "birth_date": "1982-06-30",
                "gender": "male",
                "phone": "+91-9876543214",
                "address": "23 Andheri East, Mumbai",
            },
            # Hospital 3 — Fortis Bangalore
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_003",
                "local_patient_id": "FRT-001",
                "given_name": "Ananya",
                "family_name": "Reddy",
                "birth_date": "1995-09-18",
                "gender": "female",
                "phone": "+91-9876543215",
                "address": "12 Koramangala, Bangalore",
            },
            {
                "global_id": str(uuid.uuid4()),
                "hospital_id": "HOSP_003",
                "local_patient_id": "FRT-002",
                "given_name": "Karthik",
                "family_name": "Nair",
                "birth_date": "1988-12-25",
                "gender": "male",
                "phone": "+91-9876543216",
                "address": "56 Indiranagar, Bangalore",
            },
        ]

        patients = []
        for pdata in patients_data:
            p = Patient(**pdata)
            patients.append(p)
            db.add(p)
        db.flush()
        print(f"  ✓ {len(patients)} patients created")

        # ── 3. MPI Records ────────────────────────────────────────
        mpi_records = []
        for p in patients:
            mpi = MPIRecord(
                global_patient_id=p.global_id,
                hospital_id=p.hospital_id,
                local_patient_id=p.local_patient_id,
            )
            mpi_records.append(mpi)
            db.add(mpi)

        # Cross-hospital mapping: Rahul Sharma also visited Max Mumbai
        cross_mpi = MPIRecord(
            global_patient_id=patients[0].global_id,  # Rahul Sharma
            hospital_id="HOSP_002",
            local_patient_id="MAX-XREF-001",
        )
        mpi_records.append(cross_mpi)
        db.add(cross_mpi)
        db.flush()
        print(f"  ✓ {len(mpi_records)} MPI records created (incl. 1 cross-hospital)")

        # ── 4. Observations ───────────────────────────────────────
        observations_data = [
            # Rahul Sharma (HOSP_001)
            {"patient_id": patients[0].global_id, "code": "8867-4", "display": "Heart Rate", "value": 72.0, "unit": "bpm", "effective_date": "2025-12-01", "status": "final"},
            {"patient_id": patients[0].global_id, "code": "8480-6", "display": "Systolic BP", "value": 128.0, "unit": "mmHg", "effective_date": "2025-12-01", "status": "final"},
            {"patient_id": patients[0].global_id, "code": "8462-4", "display": "Diastolic BP", "value": 82.0, "unit": "mmHg", "effective_date": "2025-12-01", "status": "final"},
            {"patient_id": patients[0].global_id, "code": "2345-7", "display": "Blood Glucose", "value": 95.0, "unit": "mg/dL", "effective_date": "2025-12-01", "status": "final"},
            # Priya Patel (HOSP_001)
            {"patient_id": patients[1].global_id, "code": "8867-4", "display": "Heart Rate", "value": 68.0, "unit": "bpm", "effective_date": "2025-11-15", "status": "final"},
            {"patient_id": patients[1].global_id, "code": "2093-3", "display": "Total Cholesterol", "value": 210.0, "unit": "mg/dL", "effective_date": "2025-11-15", "status": "final"},
            # Sneha Desai (HOSP_002)
            {"patient_id": patients[3].global_id, "code": "8867-4", "display": "Heart Rate", "value": 75.0, "unit": "bpm", "effective_date": "2025-12-10", "status": "final"},
            {"patient_id": patients[3].global_id, "code": "718-7", "display": "Hemoglobin", "value": 13.2, "unit": "g/dL", "effective_date": "2025-12-10", "status": "final"},
            # Ananya Reddy (HOSP_003)
            {"patient_id": patients[5].global_id, "code": "8310-5", "display": "Body Temperature", "value": 37.1, "unit": "°C", "effective_date": "2025-12-05", "status": "final"},
            {"patient_id": patients[5].global_id, "code": "29463-7", "display": "Body Weight", "value": 58.0, "unit": "kg", "effective_date": "2025-12-05", "status": "final"},
        ]

        observations = []
        for obs_data in observations_data:
            obs = Observation(id=str(uuid.uuid4()), **obs_data)
            observations.append(obs)
            db.add(obs)
        db.flush()
        print(f"  ✓ {len(observations)} observations created")

        # ── 5. Encounters ─────────────────────────────────────────
        encounters_data = [
            # Rahul Sharma
            {"patient_id": patients[0].global_id, "encounter_class": "AMB", "type_code": "checkup", "type_display": "Annual Physical", "status": "finished", "period_start": "2025-12-01T09:00:00", "period_end": "2025-12-01T10:30:00", "provider": "Dr. Meena Gupta"},
            {"patient_id": patients[0].global_id, "encounter_class": "AMB", "type_code": "followup", "type_display": "Follow-up Visit", "status": "finished", "period_start": "2026-01-15T11:00:00", "period_end": "2026-01-15T11:45:00", "provider": "Dr. Meena Gupta"},
            # Priya Patel
            {"patient_id": patients[1].global_id, "encounter_class": "AMB", "type_code": "consultation", "type_display": "Cardiology Consultation", "status": "finished", "period_start": "2025-11-15T14:00:00", "period_end": "2025-11-15T15:00:00", "provider": "Dr. Rajesh Khanna"},
            # Sneha Desai
            {"patient_id": patients[3].global_id, "encounter_class": "EMER", "type_code": "emergency", "type_display": "Emergency Visit", "status": "finished", "period_start": "2025-12-10T02:30:00", "period_end": "2025-12-10T08:00:00", "provider": "Dr. Farhan Sheikh"},
            # Ananya Reddy
            {"patient_id": patients[5].global_id, "encounter_class": "AMB", "type_code": "checkup", "type_display": "Routine Checkup", "status": "finished", "period_start": "2025-12-05T10:00:00", "period_end": "2025-12-05T10:45:00", "provider": "Dr. Lakshmi Rao"},
        ]

        encounters = []
        for enc_data in encounters_data:
            enc = Encounter(id=str(uuid.uuid4()), **enc_data)
            encounters.append(enc)
            db.add(enc)
        db.flush()
        print(f"  ✓ {len(encounters)} encounters created")

        # ── 6. Consents ───────────────────────────────────────────
        now = datetime.now(timezone.utc)
        consents_data = [
            # HOSP_001 grants HOSP_002 access to Rahul Sharma (active)
            {
                "consent_id": str(uuid.uuid4()),
                "patient_id": patients[0].global_id,
                "granting_institution": "HOSP_001",
                "requesting_institution": "HOSP_002",
                "granted_at": now - timedelta(days=7),
                "expires_at": now + timedelta(days=90),
                "status": "active",
            },
            # HOSP_001 grants HOSP_003 access to Priya Patel (active)
            {
                "consent_id": str(uuid.uuid4()),
                "patient_id": patients[1].global_id,
                "granting_institution": "HOSP_001",
                "requesting_institution": "HOSP_003",
                "granted_at": now - timedelta(days=3),
                "status": "active",
            },
            # HOSP_002 grants HOSP_001 access to Sneha Desai (revoked)
            {
                "consent_id": str(uuid.uuid4()),
                "patient_id": patients[3].global_id,
                "granting_institution": "HOSP_002",
                "requesting_institution": "HOSP_001",
                "granted_at": now - timedelta(days=30),
                "status": "revoked",
            },
            # HOSP_003 grants HOSP_002 access to Ananya Reddy (active)
            {
                "consent_id": str(uuid.uuid4()),
                "patient_id": patients[5].global_id,
                "granting_institution": "HOSP_003",
                "requesting_institution": "HOSP_002",
                "granted_at": now - timedelta(days=1),
                "expires_at": now + timedelta(days=30),
                "status": "active",
            },
        ]

        for consent_data in consents_data:
            c = Consent(**consent_data)
            db.add(c)
        db.flush()
        print(f"  ✓ {len(consents_data)} consent records created (3 active, 1 revoked)")

        # ── 7. Audit Events ───────────────────────────────────────
        # Create some initial audit events
        audit_service.log_event(
            db=db,
            event_type="DATA_ACCESS",
            actor_hospital_id="HOSP_002",
            actor_service="fhir-service",
            outcome="SUCCESS",
            subject_patient_id=patients[0].global_id,
            resource_type="Patient",
            resource_id=patients[0].global_id,
        )
        audit_service.log_event(
            db=db,
            event_type="CONSENT_UPDATE",
            actor_hospital_id="HOSP_001",
            actor_service="consent-service",
            outcome="SUCCESS",
            subject_patient_id=patients[0].global_id,
            resource_type="Consent",
        )
        audit_service.log_event(
            db=db,
            event_type="ACCESS_DENIED",
            actor_hospital_id="HOSP_003",
            actor_service="fhir-service",
            outcome="FAILURE",
            subject_patient_id=patients[3].global_id,
            resource_type="Patient",
            resource_id=patients[3].global_id,
            failure_reason="CONSENT_NOT_FOUND",
        )
        print("  ✓ 3 audit events created")

        db.commit()
        print("\n✅ Database seeded successfully!")
        print(f"\nHospitals:")
        for h in hospitals:
            print(f"  {h.id} — {h.name} (API Key: {h.api_key})")
        print(f"\nPatients:")
        for p in patients:
            print(f"  {p.global_id[:8]}... — {p.given_name} {p.family_name} ({p.hospital_id})")

    except Exception as e:
        db.rollback()
        print(f"❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
