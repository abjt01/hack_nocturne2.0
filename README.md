# 🧬 Vital: Healthcare Interoperability Platform

Vital is a highly secure, microservice-based Healthcare Interoperability Platform built for the Hack Nocturne 2.0 hackathon. It solves the critical challenge of fragmented patient data by enabling multiple isolated hospitals to share and aggregate medical records securely. 

The platform strictly enforces Zero-Trust principles: data is standardly formatted as FHIR bundles, gated by cryptographic patient consent, encrypted at rest via AES-128, and every access event is immutably logged on an Ethereum blockchain.

---

## 🚀 Core Capabilities

- **Universal Identity Resolution (MPI):** Maps siloed, local hospital IDs (e.g., `LOC-001`) into a single, global patient UUID.
- **Zero-Trust Consent Gating:** Hospital B cannot access Hospital A's patient records without explicit cryptographic consent tracked by a dedicated microservice.
- **Defense in Depth (Encryption):** Sensitive Personally Identifiable Information (PII) is encrypted at rest using AES-128 Fernet encryption via SQLAlchemy TypeDecorators.
- **Tamper-Proof Auditing:** Every read, write, and consent grant is hashed (SHA-256) and committed to a local Ethereum blockchain (Hardhat) via Web3.py.
- **Multi-Tenant React Dashboard:** A dynamic Single Page Application (SPA) that allows organic switching between hospital credentials to simulate real-world, cross-tenant data requests.

---

## 🏗️ Architecture & Tech Stack

Vital is designed as a distributed microservice ecosystem.

### **Backend (Python / FastAPI)**
- **Gateway (`vital-backend`):** The central router that enforces `X-Role`, `X-Hospital-ID`, and `X-API-Key` headers before delegating tasks. Handles PII encryption.
- **Microservices:**
  - `hospital-registry`: Issues and validates multi-tenant hospital credentials.
  - `mpi-service` (Master Patient Index): Resolves local IDs to global UUIDs.
  - `consent-service`: The gatekeeper managing active/revoked data access permissions.
  - `fhir-service`: A proxy that standardizes disparate healthcare data into FHIR R4 JSON bundles.
  - `blockchain-audit-service`: Converts platform events into hashes and transacts them onto the Ethereum ledger.

### **Databases & Ledger**
- **PostgreSQL 15:** A single instance utilizing strict multi-schema isolation (`patient_service`, `consent_service`, `registry_service`, etc.) to enforce data boundaries between microservices.
- **Ethereum (Hardhat):** A local blockchain node running the `AuditLogger` smart contract.

### **Frontend**
- **React 18:** A glass-morphic, dark-themed SPA featuring Recharts for live data visualization and Axios interceptors for dynamic header injection.

---

<<<<<<< HEAD
# Problem Statement

Healthcare IT systems face two major challenges:

### 1. Fragmented Medical Records

Hospitals store records in proprietary formats that cannot communicate with other systems.

Consequences include:

- Incomplete patient history
- Duplicate testing
- Delayed treatment decisions
- Increased healthcare costs

### 2. Lack of Transparent Auditability

Patients typically cannot verify:

- Who accessed their records
- Whether access occurred under valid consent
- Whether logs have been tampered with

Vitals solves these issues through **FHIR standardization and blockchain-backed audit verification**.

---


# Microservices

## API Layer (`backend`)
- **Language:** Python / FastAPI  
- **Port:** 8000  

Responsibilities:

- Request routing
- Authentication
- Hospital identity validation
- Gateway for all service calls

---

## FHIR Service (`services/fhir-service`)
- **Language:** Python  
- **Port:** 8001  

Responsibilities:

- Convert hospital data into **HL7 FHIR Bundles**
- Validate resources using `fhir.resources`
- Serve standardized patient records

Endpoints:


GET /fhir/patient/{id}
GET /fhir/observation/{id}
GET /fhir/encounter/{id}
POST /fhir/ingest
GET /fhir/bundle/{patient_id}


---

## Consent Service (`services/consent-service`)
- **Language:** Python  
- **Port:** 8002  

Responsibilities:

- Store consent records
- Validate data access requests
- Handle grant and revoke operations

Endpoints:


POST /consent/validate
POST /consent/grant
POST /consent/revoke
GET /consent/{patient_id}


---

## Patient Data Service (`services/patient-data-service`)
- **Language:** Python  
- **Port:** 8003  

Responsibilities:

- Store FHIR Bundles
- Manage patient records
- Maintain local patient datasets

---

## Blockchain Audit Service (`services/blockchain-audit-service`)
- **Language:** Node.js  
- **Port:** 8004  

Responsibilities:

- Receive audit events from services
- Compute SHA-256 event hashes
- Write hashes to Ethereum smart contracts

Endpoints:


POST /audit/log
GET /audit/verify/{event_id}
GET /audit/events


---

## MPI Service (`services/mpi-service`)
- **Language:** Python  
- **Port:** 9000  

Responsibilities:

- Generate **global patient identifiers**
- Map hospital-specific patient IDs to a universal UUID

---

## Hospital Registry (`services/hospital-registry`)
- **Language:** Python  
- **Port:** 9001  

Responsibilities:

- Maintain hospital identities
- Validate API keys for inter-hospital communication
---

# Features

### Cross-Hospital Identity Resolution
Maps hospital-specific patient IDs to a **single global UUID**.

### FHIR Standardization
All records are served as **HL7 FHIR R4 Bundles**.

### Consent-Based Access
Patient consent is validated before any data retrieval.

### Immutable Audit Trails
Every event is hashed and stored on blockchain.

### Microservice Architecture
Independent services simplify development and scaling.

### Unified Dashboard
React frontend demonstrating patient data access and audit verification.

---

# Tech Stack

### Frontend
- React
- React Router
- Tailwind CSS
- Recharts

### Backend
- Python
- FastAPI
- Pydantic v2
- SQLite

### Blockchain
- Hardhat Ethereum Network
- Solidity
- ethers.js
- web3.py

### Infrastructure
- Docker
- Docker Compose

---

# Prerequisites

Install the following:

- **Docker & Docker Compose** (recommended)
- **Node.js 18+**
- **Python 3.9+**

---

# Running the Platform

## Option 1 — Docker (Recommended)

Start all services with:

=======
## 🛠️ Local Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Node.js (v18+) & npm
- Python 3.10+

### Step 1: Start the Blockchain Node
The blockchain service requires a dedicated terminal to run the local Hardhat network.
```bash
cd services/blockchain-audit-service
npm install
./start.sh
```
*Leave this terminal running in the background.*

### Step 2: Boot the Microservices
Open a new terminal at the project root to spin up PostgreSQL, the FastAPI backend, the React frontend, and all microservices.
>>>>>>> 6c7c1e0 (Update README.md)
```bash
docker-compose up --build
```
*Wait until you see `vital-frontend | Compiled successfully!` and PostgreSQL is ready.*

### Step 3: Seed Organic Demo Data
Vital does not rely on static mock data. Open a third terminal to run the seeding script, which uses actual API calls to populate the database and blockchain with patients, consents, and audit logs.
```bash
python3 integration_test.py
python3 demo_seed.py
```

### Step 4: Access the Platform
Open your browser and navigate to:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🛡️ Demonstrating Security features (MVP Guide)

1. **Dashboard & Metrics:** View live data populated by the `demo_seed.py` script.
2. **Multi-Tenant Config:** Use the `⚙️ Config` button in the top right to switch between `HOSP_001` and `HOSP_002` credentials dynamically.
3. **Consent Revocation:** Navigate to the Consent Manager and revoke an active grant. Watch as the other hospital instantly loses access (403 Forbidden) to that patient's FHIR bundle.
4. **Blockchain Verification:** Go to the Audit Trail and click "Verify" on any log. The system will mathematically prove the log perfectly matches the immutable Ethereum transaction.

---
*Built for Hack Nocturne 2.0*
