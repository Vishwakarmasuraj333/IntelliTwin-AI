"""
ML Model Information & Dynamic Metrics Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

class RocPoint(BaseModel):
    fpr: float
    tpr: float

class FeatureImportanceItem(BaseModel):
    feature: str
    importance: float

class ModelMetricsData(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: List[List[int]]
    roc_curve: Optional[List[RocPoint]] = []
    feature_importances: Optional[List[FeatureImportanceItem]] = []

class ModelDetailResponse(BaseModel):
    id: str
    model_name: str
    version: str
    algorithm: str
    is_active: bool
    metrics: ModelMetricsData
    feature_names: List[str]
    trained_at: datetime
    
    class Config:
        from_attributes = True

class ModelComparisonResponse(BaseModel):
    dataset_info: Dict[str, Any]
    best_model: str
    models: Dict[str, ModelMetricsData]
