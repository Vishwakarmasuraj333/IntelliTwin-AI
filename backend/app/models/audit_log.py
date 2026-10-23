"""
Audit Log ORM Model for Enterprise Compliance
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, DateTime
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action = Column(String(100), nullable=False)
    user = Column(String(255), nullable=False) # Email or username
    ip_address = Column(String(45), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
