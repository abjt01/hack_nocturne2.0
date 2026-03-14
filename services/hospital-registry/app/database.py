import os
import psycopg2
from psycopg2.extras import RealDictConnection

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, connection_factory=RealDictConnection)
    with conn.cursor() as cur:
        cur.execute("SET search_path TO registry_service")
    return conn

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS registry_service")
    cursor.execute("SET search_path TO registry_service")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            api_key TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Forced migration for stale tables
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'registry_service' AND table_name = 'hospitals'")
    columns = [row[0] for row in cursor.fetchall()]
    if 'hospital_id' in columns:
        cursor.execute("ALTER TABLE hospitals RENAME COLUMN hospital_id TO id")
    if 'hospital_name' in columns:
        cursor.execute("ALTER TABLE hospitals RENAME COLUMN hospital_name TO name")
    
    # Seed data for integration tests
    cursor.execute("""
        INSERT INTO hospitals (id, name, api_key)
        VALUES ('HOSP_001', 'Hospital One', 'key_001'),
               ('HOSP_002', 'Hospital Two', 'key_002')
        ON CONFLICT (id) DO UPDATE SET 
            name = EXCLUDED.name,
            api_key = EXCLUDED.api_key
    """)
    conn.close()
