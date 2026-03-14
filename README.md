# Vital: FHIR Healthcare Interoperability Platform

Vital is a comprehensive healthcare data exchange layer built on HL7 FHIR standards. It enables disparate hospital systems to securely share patient records using a zero-trust architecture, consent-gated access control, and immutable blockchain-based audit trails.

The system implements a **microservices architecture** that standardizes hospital data into **HL7 FHIR bundles**, validates **cross-institution access through patient consent**, and logs every access event using **blockchain-backed cryptographic verification**.

The goal is to demonstrate how healthcare institutions can safely share patient records while preserving **privacy, traceability, and interoperability**.

---

## Badges

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Enabled-green.svg)
![Node.js](https://img.shields.io/badge/Node.js-18+-lightgrey.svg)
![React](https://img.shields.io/badge/React-18+-informational.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES2022-yellow.svg)

---

# Overview

Healthcare institutions typically maintain **isolated Electronic Health Record (EHR) systems** using incompatible formats.

When patients move between institutions:

- Their medical history is fragmented
- Physicians lack access to complete records
- Duplicate diagnostic tests are ordered
- Emergency care decisions are delayed

Vitals introduces a **FHIR-based interoperability layer** that standardizes patient data exchange while ensuring:

- Patient-controlled access through consent management
- Cross-hospital identity resolution
- Tamper-proof audit trails using blockchain verification

---

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

# Project Structure


vitals/
│
├── backend/
│ └── FastAPI gateway
│
├── frontend/
│ └── React dashboard
│
├── services/
│ ├── blockchain-audit-service/
│ ├── consent-service/
│ ├── fhir-service/
│ ├── hospital-registry/
│ ├── mpi-service/
│ └── patient-data-service/
│
├── docker-compose.yml
└── README.md


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

```bash
docker-compose up --build
