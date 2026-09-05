from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from pathlib import Path
from typing import Optional, Union, List
from dotenv import load_dotenv

# Ensure .env is loaded from backend directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Student Skill Gap Analyzer"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./skillgap.db"
    
    # Security / Auth
    JWT_SECRET: str = "super_secret_skill_gap_jwt_key_phase1_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Gemini AI
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    # Industry Job Market API
    JOB_API_URL: str = ""
    JOB_API_KEY: str = ""
    JOB_INTELLIGENCE_MENTION_THRESHOLD_CANDIDATE: int = 3
    JOB_INTELLIGENCE_MENTION_THRESHOLD_REQUIRED: int = 5
    
    # Official European Commission ESCO Web Service API
    ESCO_API_BASE_URL: str = "https://ec.europa.eu/esco/api"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "https://kdk-hackathon-o4cu-gamma.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    CORS_ORIGIN_REGEX: Optional[str] = r"https:\/\/.*\.vercel\.app"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
