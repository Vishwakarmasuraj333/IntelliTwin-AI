"""
Security Command Center Dashboard Statistics API
------------------------------------------------
Aggregates authentic telemetry event counts, severity breakdowns, attack distributions,
timeline activity, and risk score metrics directly from the database.
Zero fabricated placeholder metrics.
"""

from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.api.deps import get_db
from app.models.event import SecurityEvent
from app.schemas.stats import (
    DashboardStatsResponse, SeverityBreakdownItem,
    AttackDistributionItem, TimelinePoint
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard Statistics"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_statistics(db: Session = Depends(get_db)):
    total = db.query(SecurityEvent).count()
    anomalies = db.query(SecurityEvent).filter(SecurityEvent.prediction == "ANOMALY").count()
    normal = total - anomalies
    
    # Calculate average risk score
    avg_risk = db.query(func.avg(SecurityEvent.risk_score)).scalar() or 0.0
    high_crit = db.query(SecurityEvent).filter(SecurityEvent.severity.in_(["HIGH", "CRITICAL"])).count()
    
    # Severity breakdown
    sev_rows = db.query(SecurityEvent.severity, func.count(SecurityEvent.id)).group_by(SecurityEvent.severity).all()
    sev_dict = {s: 0 for s in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]}
    for s, c in sev_rows:
        if s in sev_dict:
            sev_dict[s] = c
    severity_breakdown = [SeverityBreakdownItem(severity=k, count=v) for k, v in sev_dict.items()]
    
    # Attack distribution from real events
    attack_rows = db.query(
        SecurityEvent.attack_category, func.count(SecurityEvent.id)
    ).filter(SecurityEvent.prediction == "ANOMALY").group_by(SecurityEvent.attack_category).all()
    
    attack_distribution = []
    anomaly_denom = max(anomalies, 1)
    for cat, c in attack_rows:
        if cat and cat != "Normal":
            attack_distribution.append(AttackDistributionItem(
                category=cat,
                count=c,
                percentage=round((c / anomaly_denom) * 100, 1)
            ))

    anomaly_rate = round((anomalies / max(total, 1)) * 100, 1) if total > 0 else 0.0
    
    # Construct 12-slot 24-hour Timeline from real database events
    now = datetime.now(timezone.utc)
    slot_duration = timedelta(hours=2)
    timeline = []
    
    for i in range(11, -1, -1):
        slot_end = now - (slot_duration * i)
        slot_start = slot_end - slot_duration
        slot_label = slot_end.strftime("%H:%M")

        # Query events occurring in this 2-hour window
        slot_total = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= slot_start,
            SecurityEvent.created_at < slot_end
        ).count()
        
        slot_anomalies = db.query(SecurityEvent).filter(
            SecurityEvent.created_at >= slot_start,
            SecurityEvent.created_at < slot_end,
            SecurityEvent.prediction == "ANOMALY"
        ).count()
        
        slot_normal = slot_total - slot_anomalies
        timeline.append(TimelinePoint(
            timestamp=slot_label,
            total=slot_total,
            anomalies=slot_anomalies,
            normal=slot_normal
        ))
        
    return DashboardStatsResponse(
        total_analyzed=total,
        suspicious_events=anomalies,
        normal_events=normal,
        anomaly_rate_percent=anomaly_rate,
        average_risk_score=round(float(avg_risk), 1),
        high_critical_count=high_crit,
        severity_breakdown=severity_breakdown,
        attack_distribution=attack_distribution,
        timeline=timeline
    )
