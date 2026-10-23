"""
Dashboard KPI & Aggregated Telemetry Schemas
"""

from typing import List, Dict, Any
from pydantic import BaseModel

class TimelinePoint(BaseModel):
    timestamp: str
    total: int
    anomalies: int
    normal: int

class AttackDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float

class SeverityBreakdownItem(BaseModel):
    severity: str
    count: int

class DashboardStatsResponse(BaseModel):
    total_analyzed: int
    suspicious_events: int
    normal_events: int
    anomaly_rate_percent: float
    average_risk_score: float
    high_critical_count: int
    severity_breakdown: List[SeverityBreakdownItem]
    attack_distribution: List[AttackDistributionItem]
    timeline: List[TimelinePoint]
