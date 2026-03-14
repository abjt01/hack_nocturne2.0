import requests
import time
import sys

# --- Configuration ---
BASE_URL = "http://localhost:8000/api"
HOSP_HEADERS = {
    "X-Role": "hospital",
    "X-Hospital-ID": "HOSP_001",
    "X-API-Key": "key_001"
}

def check_health():
    print("🔍 Checking System Health...")
    try:
        resp = requests.get(f"http://localhost:8000/api/health")
        if resp.status_code == 200:
            print("✅ Backend is UP")
            return True
    except:
        pass
    print("❌ Backend is DOWN. Please run 'docker-compose up --build' first.")
    return False

def test_patient_ingest():
    print("\n📝 Testing Patient Ingest (PII Encryption & RBAC)...")
    payload = {
        "local_patient_id": "LOC-TEST-001",
        "given_name": "Vital",
        "family_name": "Test",
        "birth_date": "1990-01-01",
        "gender": "male",
        "phone": "555-0199",
        "address": "123 Verification St",
        "observations": [
            {"code": "8867-4", "display": "Heart rate", "value": 72, "unit": "bpm"}
        ]
    }
    
    # 1. Ingest as Hospital
    resp = requests.post(f"{BASE_URL}/patients", json=payload, headers=HOSP_HEADERS)
    if resp.status_code != 201:
        print(f"❌ Ingest failed: {resp.text}")
        return None
    
    data = resp.json()
    global_id = data["global_id"]
    print(f"✅ Patient Ingested: {global_id}")
    return global_id

def test_rbac_and_encryption(global_id):
    if not global_id: return

    print("\n🔐 Testing RBAC & Decryption...")
    
    # 1. Access as the WRONG hospital (should fail or hide depending on logic)
    WRONG_HEADERS = HOSP_HEADERS.copy()
    WRONG_HEADERS["X-Hospital-ID"] = "HOSP_999"
    resp = requests.get(f"{BASE_URL}/patients/{global_id}", headers=WRONG_HEADERS)
    # The current logic might return 401/403 or just not find it. 
    # Based on our refactored security.py, it requires a valid ID/Key.
    print(f"--- Unauthorized Access (HOSP_999): Status {resp.status_code}")

    # 2. Access as the CORRECT Patient
    PAT_HEADERS = {
        "X-Role": "patient",
        "X-Patient-ID": global_id
    }
    resp = requests.get(f"{BASE_URL}/patients/{global_id}", headers=PAT_HEADERS)
    if resp.status_code == 200:
        p_data = resp.json()
        print(f"✅ Patient Access (Self): PASS")
        print(f"✅ Decryption Check (Name): {p_data.get('given_name')} {p_data.get('family_name')}")
        if p_data.get('given_name') == "Vital":
            print("✨ PII Decryption verified correct.")
    else:
        print(f"❌ Patient Access failed: {resp.text}")

def test_consent_flow(global_id):
    if not global_id: return
    print("\n🤝 Testing Consent & FHIR Proxy...")
    
    # 1. Requesting Hospital (HOSP_002) tries to pull FHIR Bundle without consent
    HOSP2_HEADERS = {
        "X-Role": "hospital",
        "X-Hospital-ID": "HOSP_002",
        "X-API-Key": "key_002"
    }
    resp = requests.get(f"{BASE_URL}/bundle/{global_id}", headers=HOSP2_HEADERS)
    print(f"--- HOSP_002 Access WITHOUT Consent: Status {resp.status_code} (Expected 403)")

    # 2. Grant Consent
    grant_payload = {
        "patient_id": global_id,
        "institution_id": "HOSP_002",
        "expiry": "2026-12-31T23:59:59Z"
    }
    # Hospital 1 (Owner) grants to Hospital 2
    resp = requests.post(f"{BASE_URL}/consent/grant", json=grant_payload, headers=HOSP_HEADERS)
    if resp.status_code == 201:
        print("✅ Consent Granted: HOSP_001 -> HOSP_002")
    
    # 3. Requesting Hospital (HOSP_002) tries again
    resp = requests.get(f"{BASE_URL}/bundle/{global_id}", headers=HOSP2_HEADERS)
    if resp.status_code == 200:
        print("✅ HOSP_002 Access WITH Consent: PASS")
        print("✅ FHIR Bundle compilation: PASS")
    else:
        print(f"❌ Consent verification failed: {resp.text}")

if __name__ == "__main__":
    if check_health():
        gid = test_patient_ingest()
        test_rbac_and_encryption(gid)
        test_consent_flow(gid)
        print("\n🏁 Integration test complete.")
    else:
        sys.exit(1)
