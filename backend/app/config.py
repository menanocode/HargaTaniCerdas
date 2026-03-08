from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # Database
    DATABASE_URL: str = "sqlite:///./hargatani.db"

    # SP2KP API (local)
    SP2KP_BASE_URL: str = "http://127.0.0.1:5500"
    SP2KP_KODE_PROVINSI: str = "33"
    SP2KP_KODE_KAB_KOTA: str = "3315"

    # BMKG (local)
    BMKG_API_URL: str = "http://127.0.0.1:8500"
    BMKG_ADM4: str = "33.15.00.0000"

    # BPS
    BPS_API_KEY: str = ""

    # Local News API
    LOCAL_NEWS_API_URL: str = "http://127.0.0.1:9500"

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
