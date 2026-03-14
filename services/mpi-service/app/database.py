import os
import psycopg2
from psycopg2.extras import RealDictConnection

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, connection_factory=RealDictConnection)
    with conn.cursor() as cur:
        cur.execute("SET search_path TO mpi_service")
    return conn

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    
    cursor.execute("CREATE SCHEMA IF NOT EXISTS mpi_service")
    cursor.execute("SET search_path TO mpi_service")
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mpi_records (
            global_patient_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS identities (
            id SERIAL PRIMARY KEY,
            global_patient_id TEXT,
            hospital_id TEXT,
            local_patient_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(global_patient_id) REFERENCES mpi_records(global_patient_id),
            UNIQUE(hospital_id, local_patient_id)
        )
    ''')
    
    conn.close()
