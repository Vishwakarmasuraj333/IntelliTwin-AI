"""
Security Event ORM Model for Telemetry & Real-Time Detections
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    session_id = Column(String(64), nullable=True)
    
    # Raw Packet Flow Data
    event_data = Column(JSON, nullable=False)
    
    # Detection Output
    prediction = Column(String(20), nullable=False, index=True) # NORMAL or ANOMALY
    confidence = Column(Float, nullable=False)      # 0.0 to 1.0
    risk_score = Column(Integer, nullable=False)    # 0 to 100
    severity = Column(String(20), nullable=False, index=True)   # LOW, MEDIUM, HIGH, CRITICAL
    attack_category = Column(String(50), nullable=True) # Normal, DoS, Exploits, Fuzzers, Reconnaissance, etc.
    
    # Explainable AI Attributions
    shap_explanation = Column(JSON, nullable=True)
    model_version = Column(String(50), nullable=False)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    user = relationship("User", back_populates="events")
    reports = relationship("IncidentReport", back_populates="event", cascade="all, delete-orphan")
