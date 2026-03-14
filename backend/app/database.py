from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all tables in the database."""
    from sqlalchemy import text
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS patient_service"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS consent_service"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS registry_service"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS audit_service"))
        conn.commit()
    Base.metadata.create_all(bind=engine)
