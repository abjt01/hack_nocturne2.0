from cryptography.fernet import Fernet
from app.config import get_settings
from sqlalchemy import TypeDecorator, String
from fastapi import Header, HTTPException, status
from enum import Enum

settings = get_settings()
fernet = Fernet(settings.ENCRYPTION_KEY.encode())

class Role(str, Enum):
    HOSPITAL = "hospital"
    PATIENT = "patient"

def get_current_role(
    x_role: str | None = Header(None, alias="X-Role"),
    x_hospital_id: str | None = Header(None, alias="X-Hospital-ID"),
    x_api_key: str | None = Header(None, alias="X-API-Key"),
    x_patient_id: str | None = Header(None, alias="X-Patient-ID")
):
    # Discovery: If role is missing but ID is present, infer role
    if x_role:
        x_role = x_role.lower()
        if x_role not in [r.value for r in Role]:
            x_role = None

    if not x_role:
        if x_hospital_id:
            x_role = Role.HOSPITAL
        elif x_patient_id:
            x_role = Role.PATIENT

    if x_role == Role.HOSPITAL:
        if not x_hospital_id or not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Hospital role requires X-Hospital-ID and X-API-Key"
            )
        return {"role": Role.HOSPITAL, "id": x_hospital_id}
    
    if x_role == Role.PATIENT:
        if not x_patient_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Patient role requires X-Patient-ID"
            )
        return {"role": Role.PATIENT, "id": x_patient_id}
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Identification headers (X-Hospital-ID or X-Patient-ID) missing"
    )

def encrypt_data(data: str) -> str:

    if not data:
        return data
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str) -> str:
    if not token:
        return token
    return fernet.decrypt(token.encode()).decode()

class EncryptedString(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        if value is not None:
            return encrypt_data(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return decrypt_data(value)
        return value

