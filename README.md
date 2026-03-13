# Healthcare Interoperability Platform

A robust, secure, and modern backend for exchanging patient electronic health records (EHR) across different hospital networks. Built with **FastAPI** and **SQLite**, it provides consent-gated data access, global patient identity resolution, and tamper-proof audit trails.

## Features

- 🏥 **Multi-Hospital Network Ecosystem**: Allows diverse clinical institutions to interoperate securely via API keys.
- 🪪 **Master Patient Index (MPI)**: Maps decentralized, local hospital IDs to a centralized global patient UUID for consistent identification.
- 🔐 **Consent-Gated Data Access**: Hospitals can only access records from other hospitals if an active, non-expired Consent grant exists for that specific patient.
- 📜 **FHIR R4 Standardized Payloads**: Constructs patient data, observations, and algorithmic encounters into strictly formatted HL7 FHIR-like JSON bundles (without heavy external library dependencies).
- ⛓️ **Tamper-Proof Audit Logging**: Replaces complex blockchain infrastructure by computing and verifying local SHA-256 cryptographic hashes for every data access, consent update, and access denial.

## Architecture

The system consolidates 5 core microservices from the MVP specification into a streamlined monolithic architecture for rapid MVP deployment:

1. **Hospital Registry**: Manages registered institutions and API credentials.
2. **MPI Service**: Handles global identity resolution.
3. **Patient Data Service**: Manages local data ingestion (demographics, encounters, observations).
4. **Consent Service**: Handles granting, revoking, and validating cross-hospital access.
5. **Audit / Anti-Tamper Service**: Logs events and computes cryptographic hashes to detect manipulation.
6. **FHIR Service**: Compiles the data layer into compliant `Bundle` JSON responses.

---

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` (Python package manager)

### Installation

1. **Clone the repository and navigate to the backend directory:**
    ```bash
    cd backend
    ```

2. **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4. **Environment Variables:**
    Copy the example configuration:
    ```bash
    cp .env.example .env
    ```
    *(The backend works out-of-the-box with the defaults provided in `.env`)*

### Seeding the Database (Demo Data)

To quickly test the platform, run the seed script. It provisions **3 hospitals, 7 patients, 15 clinical records, and multiple cross-network consent rules**:

```bash
python -m app.seed
```

### Running the Server

Start the FastAPI application:

```bash
uvicorn app.main:app --port 8000 --reload
```

## API Documentation & Usage

Once the server is running, the interactive interactive Swagger UI documentation is available at:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

### Authentication

All API endpoints (except the public registry list and health checks) require two custom headers identifying the acting hospital:

- `X-Hospital-ID`: (e.g., `HOSP_001`)
- `X-API-Key`: (e.g., `key_001`)

### Key Workflows

1. **Check System Health:** `GET /`
2. **View Available Hospitals:** `GET /api/hospitals`
3. **View Owned Patients:** `GET /api/patients` (Requires Auth)
4. **Fetch FHIR Bundle Across Network:** `GET /api/bundle/{global_patient_id}`
   *(Will return `200 OK` and a compiled FHIR dict if Consent is active. Will cleanly return `403 Forbidden` if missing/revoked).*
5. **Verify Audit Integrity:** `GET /api/audit/verify/{event_id}`

---

## Tech Stack
* **Language**: Python 3
* **Framework**: FastAPI
* **ORM**: SQLAlchemy
* **Database**: SQLite
* **Data Validation**: Pydantic
