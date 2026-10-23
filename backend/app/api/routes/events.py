"""
Threat History & Security Events Query Endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.event import SecurityEvent

router = APIRouter(prefix="/events", tags=["Threat History"])

@router.get("")
def list_security_events(
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    prediction: Optional[str] = Query(None, description="Filter by prediction: NORMAL, ANOMALY"),
    category: Optional[str] = Query(None, description="Filter by attack category"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(SecurityEvent)
    
    if severity:
        query = query.filter(SecurityEvent.severity == severity.upper())
    if prediction:
        query = query.filter(SecurityEvent.prediction == prediction.upper())
    if category:
        query = query.filter(SecurityEvent.attack_category.ilike(f"%{category}%"))
        
    total = query.count()
    events = query.order_by(SecurityEvent.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": [
            {
                "id": e.id,
                "user_id": e.user_id,
                "prediction": e.prediction,
                "confidence": e.confidence,
                "risk_score": e.risk_score,
                "severity": e.severity,
                "attack_category": e.attack_category,
                "model_version": e.model_version,
                "created_at": e.created_at,
                "event_data": e.event_data,
                "shap_factors": e.shap_explanation
            }
            for e in events
        ]
    }

@router.get("/{event_id}")
def get_security_event_by_id(event_id: str, db: Session = Depends(get_db)):
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Security event not found.")
    return {
        "id": event.id,
        "user_id": event.user_id,
        "prediction": event.prediction,
        "confidence": event.confidence,
        "risk_score": event.risk_score,
        "severity": event.severity,
        "attack_category": event.attack_category,
        "model_version": event.model_version,
        "created_at": event.created_at,
        "event_data": event.event_data,
        "shap_factors": event.shap_explanation
    }
