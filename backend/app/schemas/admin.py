"""
Admin Dashboard, Audit Log & Health Schemas
-------------------------------------------
Pydantic v2 schemas for administrative operations and platform health.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class AuditLogItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    action: str
    user: str
    ip_address: Optional[str]
    details: Optional[Dict[str, Any]]
    timestamp: datetime

class SystemHealthResponse(BaseModel):
    status: str # 'HEALTHY', 'DEGRADED', 'UNHEALTHY'
    database: str
    ml_models_loaded: bool
    active_model: str
    shap_explainer_ready: bool
    gemini_api_configured: bool
    uptime_seconds: float
    timestamp: datetime
