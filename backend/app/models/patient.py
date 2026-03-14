import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Text, JSON
from app.database import Base
from app.security import EncryptedString
import json

class EncryptedJSON(EncryptedString):
    def process_bind_param(self, value, dialect):
        if value is not None:
            return super().process_bind_param(json.dumps(value), dialect)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            decrypted = super().process_result_value(value, dialect)
            return json.loads(decrypted)
        return value

class Patient(Base):
    __tablename__ = "patients"
    __table_args__ = {"schema": "patient_service"}

    global_id = Column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    hospital_id = Column(String, nullable=False, index=True)
    local_patient_id = Column(String, nullable=False)
    given_name = Column(EncryptedString, nullable=True)
    family_name = Column(EncryptedString, nullable=True)
    birth_date = Column(EncryptedString, nullable=True)
    gender = Column(EncryptedString, nullable=True)
    phone = Column(EncryptedString, nullable=True)
    address = Column(EncryptedString, nullable=True)
    data = Column(EncryptedJSON, nullable=True)  # Encrypted Demographics JSON

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
