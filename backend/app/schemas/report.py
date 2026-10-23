"""
GenAI Security Analyst Report Schemas
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class MitreTechnique(BaseModel):
    id: str
    name: str
    tactic: str

class GeminiReportRequest(BaseModel):
    event_id: str
    custom_notes: Optional[str] = None

class GeminiReportResponse(BaseModel):
    report_id: str
    event_id: str
    title: str
    executive_summary: str
    technical_analysis: str
    attack_category: str
    mitre_attack: List[MitreTechnique]
    why_suspicious: List[str]
    investigation_steps: List[str]
    mitigation_playbook: List[str]
    confidence_assessment: str
    generated_at: datetime
    model_used: str
