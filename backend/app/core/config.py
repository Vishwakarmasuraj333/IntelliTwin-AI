"""
Application Configuration & Environment Settings
------------------------------------------------
Uses Pydantic BaseSettings for strong typing and environment overrides.
"""

import os
from typing import List
from pydantic_settings import BaseSettings

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
ML_ENGINE_DIR = os.path.join(PROJECT_ROOT, "ml-engine")
ML_MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
DEFAULT_SQLITE_PATH = os.path.join(BACKEND_DIR, "intellitwin.db")

import sys
if ML_ENGINE_DIR not in sys.path:
    sys.path.insert(0, ML_ENGINE_DIR)


class Settings(BaseSettings):
    PROJECT_NAME: str = "IntelliTwin AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "intellitwin_ultra_secure_jwt_secret_key_2026_soc_ai")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database (PostgreSQL URL or local SQLite fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
    
    # ML Engine Model Directory
    MODELS_DIR: str = os.getenv("MODELS_DIR", ML_MODELS_DIR)
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "*"
    ]
    
    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
