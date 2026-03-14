import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Integer

from app.database import Base


class MPIRecord(Base):
    __tablename__ = "identities"
    __table_args__ = {"schema": "mpi_service"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    global_patient_id = Column(String, nullable=False, index=True)
    hospital_id = Column(String, nullable=False)
    local_patient_id = Column(String, nullable=False)
