"""
Admin Dashboard, Audit Log & Health Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class AuditLogItem(BaseModel):
    id: str
    action: str
    user: str
    ip_address: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: datetime
    
    class Config:
        from_attributes = True

class SystemHealthResponse(BaseModel):
    status: str # 'HEALTHY', 'DEGRADED', 'UNHEALTHY'
    database: str
    ml_models_loaded: bool
    active_model: str
    shap_explainer_ready: bool
    gemini_api_configured: bool
    uptime_seconds: float
    timestamp: datetime
