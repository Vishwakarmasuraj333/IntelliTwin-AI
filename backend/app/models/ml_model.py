"""
ML Model Registry ORM Model
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from app.models.base import Base

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_name = Column(String(100), nullable=False) # 'Random Forest', 'XGBoost', 'Isolation Forest'
    version = Column(String(50), nullable=False)
    algorithm = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=False)
    
    # Real test set evaluation metrics dynamically loaded
    metrics = Column(JSON, nullable=False)
    feature_names = Column(JSON, nullable=False)
    
    trained_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
