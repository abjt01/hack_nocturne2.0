import os
import json
import psycopg2
from psycopg2.extras import RealDictConnection

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL, connection_factory=RealDictConnection)
    with conn.cursor() as cur:
        cur.execute("SET search_path TO audit_service")
    return conn

def init_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("CREATE SCHEMA IF NOT EXISTS audit_service")
    cursor.execute("SET search_path TO audit_service")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_events (
            event_id TEXT PRIMARY KEY,
            event_type TEXT,
            timestamp TEXT,
            actor_hospital_id TEXT,
            actor_service TEXT,
            subject_patient_id TEXT,
            resource_type TEXT,
            resource_id TEXT,
            outcome TEXT,
            failure_reason TEXT,
            blockchain_hash TEXT,
            tx_hash TEXT,
            full_event_json TEXT
        )
    ''')
    conn.close()

def save_event(event_id: str, event_data: dict, blockchain_hash: str, tx_hash: str, timestamp: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audit_events (
            event_id, event_type, timestamp, actor_hospital_id, actor_service,
            subject_patient_id, resource_type, resource_id, outcome,
            failure_reason, blockchain_hash, tx_hash, full_event_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ''', (
        event_id,
        event_data.get("event_type"),
        timestamp,
        event_data.get("actor", {}).get("hospital_id") or event_data.get("actor_hospital_id"),
        event_data.get("actor", {}).get("service") or event_data.get("actor_service"),
        event_data.get("subject", {}).get("patient_id") or event_data.get("subject_patient_id"),
        event_data.get("resource", {}).get("type") or event_data.get("resource_type"),
        event_data.get("resource", {}).get("id") or event_data.get("resource_id"),
        event_data.get("outcome"),
        event_data.get("failure_reason"),
        blockchain_hash,
        tx_hash,
        json.dumps(event_data)
    ))
    conn.commit()
    conn.close()

def get_event(event_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_events WHERE event_id = %s', (event_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_all_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audit_events ORDER BY timestamp DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
