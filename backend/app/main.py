"""
Healthcare Interoperability Platform — Core Backend

FastAPI application with modular routers implementing:
- Hospital Registry
- Patient Data Service
- Master Patient Index (MPI)
- Consent Service
- FHIR Bundle Service (consent-gated)
- Audit Service (SHA-256 hash verification)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import create_tables

# Import all models so they get registered with SQLAlchemy
from app.models import hospital, patient, mpi, consent, observation, encounter, audit  # noqa: F401

# Import routers
from app.routers import hospitals, patients, mpi as mpi_router, consent as consent_router, fhir, audit as audit_router

app = FastAPI(
    title="Vital",
    description=(
        "FHIR-based healthcare interoperability layer with consent enforcement "
        "and tamper-proof audit trails. Enables hospitals to securely exchange "
        "standardized medical records."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow all origins for React frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(hospitals.router)
app.include_router(patients.router)
app.include_router(mpi_router.router)
app.include_router(consent_router.router)
app.include_router(fhir.router)
app.include_router(audit_router.router)


@app.on_event("startup")
def on_startup():
    """Create database tables on startup."""
    create_tables()


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Vital",
        "version": "1.0.0",
    }


@app.get("/api/health", tags=["Health"])
def api_health():
    """API health check."""
    return {
        "status": "healthy",
        "services": {
            "hospital_registry": "up",
            "patient_data": "up",
            "mpi": "up",
            "consent": "up",
            "fhir": "up",
            "audit": "up",
        },
    }
