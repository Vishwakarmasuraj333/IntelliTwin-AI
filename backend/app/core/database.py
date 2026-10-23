"""
Database Session Management & Schema Initialization
---------------------------------------------------
Supports PostgreSQL in production and SQLite in local environment.
Implements secure administrator bootstrapping, environment-aware credential handling,
and dynamic ML model metric synchronization.
"""

import os
import json
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.ml_model import MLModel
from app.core.security import get_password_hash

logger = logging.getLogger("Database")

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes tables and seeds users & model metrics safely."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Secure Administrator Bootstrap
        admin_email = settings.ADMIN_EMAIL
        admin_user = db.query(User).filter(User.email == admin_email).first()

        if settings.ENVIRONMENT == "production":
            if not admin_user and settings.ADMIN_PASSWORD:
                logger.info(f"Bootstrapping production ADMIN account ({admin_email}) via environment secret...")
                admin_user = User(
                    name="Chief Information Security Officer",
                    email=admin_email,
                    password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                    role="ADMIN",
                    is_active=True
                )
                db.add(admin_user)
            elif not admin_user:
                logger.warning(
                    "Production Mode: No ADMIN_PASSWORD provided. Default credentials will NOT be seeded. "
                    "Set ADMIN_PASSWORD environment variable to bootstrap administrator account."
                )
        else:
            # Development / Capstone Viva mode: Seed accounts with known evaluation credentials
            if not admin_user:
                logger.info("Seeding development evaluation ADMIN user (admin@intellitwin.ai)...")
                admin_user = User(
                    name="Chief Information Security Officer",
                    email="admin@intellitwin.ai",
                    password_hash=get_password_hash("Admin@123456"),
                    role="ADMIN",
                    is_active=True
                )
                db.add(admin_user)

            analyst_user = db.query(User).filter(User.email == "analyst@intellitwin.ai").first()
            if not analyst_user:
                logger.info("Seeding development evaluation SECURITY_ANALYST user (analyst@intellitwin.ai)...")
                analyst_user = User(
                    name="Senior SOC Analyst",
                    email="analyst@intellitwin.ai",
                    password_hash=get_password_hash("Analyst@123456"),
                    role="SECURITY_ANALYST",
                    is_active=True
                )
                db.add(analyst_user)
            
        # Synchronize ML Models from model_metrics.json
        metrics_file = os.path.join(settings.MODELS_DIR, "model_metrics.json")
        if os.path.exists(metrics_file):
            with open(metrics_file, "r") as f:
                metrics_data = json.load(f)
                
            models_info = metrics_data.get("models", {})
            best_model_name = metrics_data.get("best_model", "XGBoost")
            
            for m_name, m_metrics in models_info.items():
                existing = db.query(MLModel).filter(MLModel.model_name == m_name).first()
                is_champ = (m_name == best_model_name)
                
                if not existing:
                    logger.info(f"Registering ML model in database: {m_name}")
                    model_record = MLModel(
                        model_name=m_name,
                        version="1.0.0",
                        algorithm=m_name,
                        is_active=is_champ,
                        metrics=m_metrics,
                        feature_names=metrics_data.get("dataset", {}).get("feature_list", [])
                    )
                    db.add(model_record)
                else:
                    existing.metrics = m_metrics
                    existing.is_active = is_champ
                    
        db.commit()
        logger.info("Database schema and seed synchronization complete.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database initialization: {e}")
        raise e
    finally:
        db.close()
