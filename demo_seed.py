import requests
import time
import uuid

# Configuration
BACKEND_URL = "http://localhost:8000/api"
FHIR_URL = "http://localhost:8001/fhir"

HEADERS_HOSP1 = {
    "X-Role": "hospital",
    "X-Hospital-ID": "HOSP_001",
    "X-API-Key": "key_001",
    "Content-Type": "application/json"
}

HEADERS_HOSP2 = {
    "X-Role": "hospital",
    "X-Hospital-ID": "HOSP_002",
    "X-API-Key": "key_002",
    "Content-Type": "application/json"
}

patients_to_seed = [
    {
        "local_patient_id": "LOC-001",
        "given_name": "Alice",
        "family_name": "Johnson",
        "birth_date": "1985-04-12",
        "gender": "female",
        "phone": "555-0101",
        "address": "123 Elm St",
        "blood_type": "O+"
    },
    {
        "local_patient_id": "LOC-002",
        "given_name": "Bob",
        "family_name": "Martinez",
        "birth_date": "1992-08-25",
        "gender": "male",
        "phone": "555-0202",
        "address": "456 Oak Ave",
        "blood_type": "A-"
    },
    {
        "local_patient_id": "LOC-003",
        "given_name": "Carol",
        "family_name": "Williams",
        "birth_date": "1978-11-03",
        "gender": "female",
        "phone": "555-0303",
        "address": "789 Pine Rd",
        "blood_type": "B+"
    }
]

print("🌱 Seeding Demo Data...")

global_ids = []

# 1. Create Patients via Backend
print("\n=> Creating Patients...")
for i, pt in enumerate(patients_to_seed):
    # Apportion patients between HOSP 1 and 2
    headers = HEADERS_HOSP1 if i % 2 == 0 else HEADERS_HOSP2
    resp = requests.post(f"{BACKEND_URL}/patients", json=pt, headers=headers)
    if resp.status_code == 201:
        gid = resp.json()["global_id"]
        global_ids.append((gid, headers["X-Hospital-ID"]))
        print(f"  [+] Patient {pt['given_name']} {pt['family_name']} created: {gid} at {headers['X-Hospital-ID']}")
    else:
        print(f"  [!] Failed to create patient {pt['given_name']}: {resp.text}")

print("\n=> Granting and Revoking Consents...")
# 2. Grant and Revoke Consents (Generates Audit Events)
if len(global_ids) >= 2:
    p1_id, p1_hosp = global_ids[0]
    p2_id, p2_hosp = global_ids[1]

    # Grant Consent for p1 to the OTHER hospital
    other_hosp = "HOSP_002" if p1_hosp == "HOSP_001" else "HOSP_001"
    headers = HEADERS_HOSP1 if p1_hosp == "HOSP_001" else HEADERS_HOSP2
    
    grant_payload = {
        "patient_id": p1_id,
        "institution_id": other_hosp,
        "expiry": "2026-12-31T23:59:59Z",
        "purpose": "Cardiology Consult"
    }
    r = requests.post(f"{BACKEND_URL}/consent/grant", json=grant_payload, headers=headers)
    if r.status_code == 201:
        print(f"  [+] Consent GRANTED for {p1_id} to {other_hosp}")
    else:
        print(f"  [!] Failed to grant consent: {r.text}")

    # Grant then Revoke for p2
    other_hosp2 = "HOSP_001" if p2_hosp == "HOSP_002" else "HOSP_002"
    headers2 = HEADERS_HOSP1 if p2_hosp == "HOSP_001" else HEADERS_HOSP2
    
    # Wait a sec
    time.sleep(1)
    
    grant_payload2 = {
        "patient_id": p2_id,
        "institution_id": other_hosp2,
        "expiry": "2025-06-01T00:00:00Z",
        "purpose": "Emergency ER Room"
    }
    r2 = requests.post(f"{BACKEND_URL}/consent/grant", json=grant_payload2, headers=headers2)
    if r2.status_code == 201:
        print(f"  [+] Consent GRANTED for {p2_id} to {other_hosp2}")
        time.sleep(1)
        
        # Revoke it
        revoke_payload2 = {
            "patient_id": p2_id,
            "institution_id": other_hosp2
        }
        r3 = requests.post(f"{BACKEND_URL}/consent/revoke", json=revoke_payload2, headers=headers2)
        if r3.status_code == 200:
            print(f"  [+] Consent REVOKED for {p2_id} to {other_hosp2}")
        else:
            print(f"  [!] Failed to revoke: {r3.text}")

print("\n=> Firing FHIR Proxy Hits (Creates Access Logs)...")
# 3. Read data via FHIR proxy (generates FHIR metrics and Audit)
if global_ids:
    p1_id, p1_hosp = global_ids[0]
    
    # Successful query
    headers = HEADERS_HOSP1 if p1_hosp == "HOSP_001" else HEADERS_HOSP2
    r_fhir = requests.get(f"{FHIR_URL}/patient/{p1_id}", headers=headers)
    print(f"  [+] FHIR Request (Authorized): {r_fhir.status_code}")

    # Unauthorized access (Access Denied metrics simulation)
    # the other hospital doesn't have consent if it was revoked or never granted
    if len(global_ids) >= 3:
        p3_id, p3_hosp = global_ids[2]
        unauth_headers = HEADERS_HOSP2 if p3_hosp == "HOSP_001" else HEADERS_HOSP1
        r_unauth = requests.get(f"{FHIR_URL}/patient/{p3_id}", headers=unauth_headers)
        print(f"  [+] FHIR Request (Unauthorized Simulation): {r_unauth.status_code}")


print("\n✅ Seeding Complete. The Dashboard should now reflect live organic data without mocks.")
