"""
Admin Dashboard, Audit Log & Platform Health Endpoints
"""

import time
import os
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, require_role
from app.core.config import settings
from app.models.user import User
from app.models.audit_log import AuditLog
from app.schemas.admin import AuditLogItem, SystemHealthResponse
from app.services.ml_service import ml_engine
from app.services.shap_service import shap_service

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])
START_TIME = time.time()

@router.get("/health", response_model=SystemHealthResponse)
def get_system_health(db: Session = Depends(get_db)):
    db_status = "ONLINE"
    try:
        db.execute(func_text("SELECT 1") if False else User.__table__.select().limit(1))
    except Exception:
        db_status = "DEGRADED"
        
    models_ready = ml_engine.model is not None and ml_engine.preprocessor is not None
    shap_ready = shap_service.explainer is not None or ml_engine.preprocessor is not None
    gemini_ready = bool(settings.GEMINI_API_KEY)
    
    status = "HEALTHY" if (db_status == "ONLINE" and models_ready) else "DEGRADED"
    
    return SystemHealthResponse(
        status=status,
        database=f"SQLAlchemy ({db_status})",
        ml_models_loaded=models_ready,
        active_model=ml_engine.model_name,
        shap_explainer_ready=shap_ready,
        gemini_api_configured=gemini_ready,
        uptime_seconds=round(time.time() - START_TIME, 2),
        timestamp=datetime.now(timezone.utc)
    )

@router.get("/audit-logs", response_model=List[AuditLogItem])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    admin_user = Depends(require_role(["ADMIN"]))
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset).limit(limit).all()
    return logs

@router.get("/users")
def get_registered_users(
    db: Session = Depends(get_db),
    admin_user = Depends(require_role(["ADMIN"]))
):
    users = db.query(User).all()
    return [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]
