# 🧬 Vital: Healthcare Interoperability Platform

**Vital** is a secure, microservice-based Healthcare Interoperability Platform built for Hack Nocturne 2.0.  
It solves the challenge of fragmented patient data by enabling multiple isolated hospitals to securely share and aggregate medical records.

The platform follows Zero-Trust principles: data is standardized as FHIR bundles, gated by patient consent, encrypted at rest, and every access event is immutably logged on a local Ethereum blockchain.

---

## 📸 Screenshots

![Screenshot 1](https://github.com/user-attachments/assets/82c3602a-476a-44ab-878c-0b913d1362de)
![Screenshot 2](https://github.com/user-attachments/assets/7eab3c0c-5041-4b14-b13f-76fa5b240893)

---

## 🚀 Core Capabilities

- **Universal Identity Resolution (MPI):** Maps siloed local hospital IDs (for example, `LOC-001`) into a single global patient UUID.
- **Consent-Gated Access:** A hospital cannot access another hospital’s patient records without explicit consent.
- **Encryption at Rest:** Sensitive PII is encrypted at rest using Fernet-based encryption.
- **Tamper-Proof Auditing:** Every read, write, and consent update is hashed with SHA-256 and committed to a local Ethereum blockchain using Hardhat.
- **FHIR Standardization:** Medical records are normalized and served as HL7 FHIR R4 Bundles.
- **Multi-Tenant Dashboard:** A React-based SPA allows switching between hospital credentials to simulate cross-hospital workflows.

---

## ⚠️ The Problem We Solve

Healthcare systems still face two major issues:

1. **Fragmented Medical Records**  
   Hospitals often store patient data in proprietary formats that do not interoperate. This leads to incomplete medical history, duplicate testing, delayed treatment, and higher operational cost.

2. **Lack of Transparent Auditability**  
   Patients and institutions usually cannot reliably verify who accessed a record, whether access was consented, or whether logs were altered.

**Vital solves both problems** by combining FHIR-based interoperability with blockchain-backed audit verification.

---

## 🏗️ System Architecture

The system follows a microservice-based architecture where each service has a clear responsibility and communicates through REST APIs.

### Network Topology

```text
       [ React Frontend SPA (:3000) ]
                   |
                   v
    +-----------------------------+
    | API Gateway Layer (:8000)   |
    | (Auth, Routing, Encryption) |
    +-----------------------------+
                   |
      +------------+-------------+---------------------------+
      |            |             |                           |
      v            v             v                           v
  [ FHIR ]    [ Consent ]  [ Patient Data ]  (Shared) [ MPI ] & [ Registry ]
  (:8001)      (:8002)       (:8003/DB)               (:9000)     (:9001)
      |            |             |
      +------------+-------------+
                   |
         (Logs all access events)
                   v
    +-----------------------------+
    |  Blockchain Audit (:8005)   |
    |  (Computes SHA-256 Hashes)  |
    +-----------------------------+
                   |
                   v
    [ Hardhat Ethereum Node (:8545) ]
````

### Component Stack & Responsibilities

* **Frontend:** React 18 SPA with dynamic hospital switching and dashboard views.
* **API Gateway (`vital-backend` / Port 8000):** Central FastAPI layer that validates headers like `X-Hospital-ID` and `X-API-Key`, routes requests, and handles secure request flow.
* **FHIR Service (Port 8001):** Converts hospital data into HL7 FHIR R4 Bundles and validates resources.
* **Consent Service (Port 8002):** Stores and validates consent records before any patient data is shared.
* **Patient Data Service (Port 8003):** Stores patient data and FHIR bundles.
* **Blockchain Audit Service (Port 8005):** Receives audit events, computes SHA-256 hashes, and writes them to the blockchain.
* **MPI Service (Port 9000):** Resolves local patient IDs into a single global UUID.
* **Hospital Registry (Port 9001):** Stores and validates hospital identities and API keys.
* **Database & Ledger:** PostgreSQL for structured data storage and Hardhat Ethereum node for immutable audit hashing.

---

## 🛠️ Local Setup & Installation

### Prerequisites

* Docker & Docker Compose
* Node.js (v18+)
* Python 3.10+

### Step 1: Start the Blockchain Node

```bash
cd services/blockchain-audit-service
npm install
./start.sh
```

Keep this terminal running.

### Step 2: Start the Main Services

From the project root:

```bash
docker-compose up --build
```

Wait until the frontend and backend services are fully up.

### Step 3: Seed Demo Data

In a new terminal:

```bash
python3 integration_test.py
python3 demo_seed.py
```

This populates demo patients, consents, and audit logs through real API calls.

### Step 4: Open the App

```text
http://localhost:3000
```
---

## 🔐 Security Features

* Every inter-service request is authenticated using hospital-level headers.
* Consent is checked before any patient record is shared.
* Sensitive data is encrypted at rest.
* Only audit hashes are stored on-chain, not raw patient data.
* Both successful and denied access attempts are logged for auditability.

---

## 🔭 Future Enhancements

* Production-grade deployment and infra hardening
* Public blockchain or testnet integration
* Patient-facing consent portal
* Role-based access control at clinician or department level
* Real EHR/FHIR server integration

---

## ❤️ Built At

Built with ❤️ at **Hack Nocturne 2.0**

