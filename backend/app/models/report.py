"""
Incident Report ORM Model for GenAI SOC Analyst Reports
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class IncidentReport(Base):
    __tablename__ = "incident_reports"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(36), ForeignKey("security_events.id", ondelete="CASCADE"), nullable=False, index=True)
    analyst_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    attack_vector = Column(String(100), nullable=False)
    
    mitre_techniques = Column(JSON, nullable=True)     # [{"id": "T1046", "name": "Network Service Discovery"}]
    investigation_steps = Column(JSON, nullable=False) # List of sequential actions
    mitigation_playbook = Column(JSON, nullable=False) # Recommended firewall/ACL rules
    gemini_raw_output = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    event = relationship("SecurityEvent", back_populates="reports")
    analyst = relationship("User", back_populates="reports")
