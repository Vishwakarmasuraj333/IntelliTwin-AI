"""
Application Configuration & Environment Settings
------------------------------------------------
Uses Pydantic BaseSettings for strong typing, secure secrets, and environment overrides.
"""

import os
import sys
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
ML_ENGINE_DIR = os.path.join(PROJECT_ROOT, "ml-engine")
ML_MODELS_DIR = os.path.join(ML_ENGINE_DIR, "models")
DEFAULT_SQLITE_PATH = os.path.join(BACKEND_DIR, "intellitwin.db")

if ML_ENGINE_DIR not in sys.path:
    sys.path.insert(0, ML_ENGINE_DIR)

class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="allow")

    PROJECT_NAME: str = "IntelliTwin AI"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Security & Cryptographic Tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "intellitwin_dev_secret_key_change_in_production_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database (PostgreSQL URL or local SQLite fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE_PATH}")
    
    # Secure Administrator Bootstrap
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@intellitwin.ai")
    ADMIN_PASSWORD: Optional[str] = os.getenv("ADMIN_PASSWORD", None)
    
    # ML Engine Model Directory
    MODELS_DIR: str = os.getenv("MODELS_DIR", ML_MODELS_DIR)
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_AUTH_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_AUTH_PER_MINUTE", "20"))
    RATE_LIMIT_PREDICT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PREDICT_PER_MINUTE", "120"))
    RATE_LIMIT_REPORTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REPORTS_PER_MINUTE", "30"))

    # CORS Whitelist (Environment configurable, never wildcard with credentials)
    BACKEND_CORS_ORIGINS: List[str] = (
        [origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()]
        if os.getenv("CORS_ORIGINS")
        else [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ]
    )

settings = Settings()
