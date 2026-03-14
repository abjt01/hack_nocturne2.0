from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    HOSPITAL_ID: str = "HOSP_001"
    HOSPITAL_NAME: str = "Apollo Delhi"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/vital_db"
    ENCRYPTION_KEY: str = "v_uY7Y_7z-5F0_W_-X-X-X-X-X-X-X-X-X-X-X-X-X-X=" # Placeholder

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
