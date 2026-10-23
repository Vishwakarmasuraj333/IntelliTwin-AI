"""
Audit Logging Service
---------------------
Persists immutable operational and administrative actions for SOC compliance.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

def record_audit_log(
    db: Session,
    action: str,
    user: str,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    try:
        log_entry = AuditLog(
            action=action,
            user=user,
            ip_address=ip_address,
            details=details
        )
        db.add(log_entry)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to record audit log: {e}")
