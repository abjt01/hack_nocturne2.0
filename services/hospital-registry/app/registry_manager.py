from app.database import get_db_connection
from app.models import HospitalCreate, HospitalValidate
import psycopg2
from psycopg2.errors import UniqueViolation

def register_hospital(hospital: HospitalCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO hospitals (id, name, api_key) VALUES (%s, %s, %s)",
            (hospital.id, hospital.name, hospital.api_key)
        )
        conn.commit()
        return True
    except UniqueViolation:
        conn.rollback()
        return False
    finally:
        conn.close()

def validate_hospital(creds: HospitalValidate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 1 FROM hospitals WHERE id = %s AND api_key = %s",
        (creds.id, creds.api_key)
    )
    result = cursor.fetchone()
    conn.close()
    return result is not None

def get_all_hospitals():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, created_at FROM hospitals")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
