"""
GenAI Security Analyst Report Schemas
-------------------------------------
Defines structured input and output schemas for Gemini SOC triage.
Includes evidence provenance, confidence limitations, and AI vs offline markers.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MitreTechnique(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(..., description="MITRE Technique ID (e.g., T1046)")
    name: str = Field(..., description="Technique name")
    tactic: str = Field(..., description="MITRE Tactic (e.g., Discovery)")

class GeminiReportRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    event_id: str = Field(..., description="UUID of the SecurityEvent to analyze")
    custom_notes: Optional[str] = Field(default=None, max_length=1000, description="Optional analyst contextual notes (untrusted text)")

class GeminiStructuredReport(BaseModel):
    """Schema for direct structured output validation from Gemini LLM or fallback."""
    model_config = ConfigDict(extra="ignore")
    title: str = Field(..., description="Concise incident headline")
    executive_summary: str = Field(..., description="High-level 2-3 sentence overview for leadership")
    technical_analysis: str = Field(..., description="Detailed technical behavior analysis")
    attack_category: str = Field(..., description="Attributed attack vector or category")
    mitre_attack: List[MitreTechnique] = Field(default_factory=list, description="Candidate MITRE ATT&CK mappings (hypotheses)")
    why_suspicious: List[str] = Field(default_factory=list, description="Evidence items derived from SHAP and verified telemetry")
    investigation_steps: List[str] = Field(default_factory=list, description="Recommended SOC triage investigation actions")
    mitigation_playbook: List[str] = Field(default_factory=list, description="Actionable firewall / ACL / host remediation steps")
    confidence_assessment: str = Field(..., description="Confidence level and reasoning")

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
    is_ai_generated: bool = False
    evidence_sources: List[str] = Field(default_factory=list)
    limitations: str = "Candidate hypotheses require SOC analyst verification before enforcement."
