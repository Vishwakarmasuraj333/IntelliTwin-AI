"""
GenAI Security Operations Center (SOC) Analyst Endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_optional_user
from app.models.user import User
from app.models.event import SecurityEvent
from app.models.report import IncidentReport
from app.schemas.report import GeminiReportRequest, GeminiReportResponse
from app.services.gemini_service import gemini_analyst
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/reports", tags=["GenAI Security Analyst"])

@router.post("/generate", response_model=GeminiReportResponse)
def generate_ai_report(
    req: GeminiReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    event = db.query(SecurityEvent).filter(SecurityEvent.id == req.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Security event with ID '{req.event_id}' not found."
        )
        
    user_id = current_user.id if current_user else None
    user_email = current_user.email if current_user else "analyst"
    
    # Generate report via Gemini API / Autonomous Fallback
    report_dict = gemini_analyst.generate_incident_report(
        event_data=event.event_data,
        prediction=event.prediction,
        risk_score=event.risk_score,
        severity=event.severity,
        attack_category=event.attack_category,
        shap_factors=event.shap_explanation or [],
        analyst_notes=req.custom_notes
    )
    
    # Save Report in Database
    report = IncidentReport(
        event_id=event.id,
        analyst_id=user_id,
        title=report_dict.get("title", f"Security Anomaly Incident #{event.id[:8]}"),
        summary=report_dict.get("executive_summary", ""),
        attack_vector=report_dict.get("attack_category", event.attack_category or "Unknown"),
        mitre_techniques=report_dict.get("mitre_attack", []),
        investigation_steps=report_dict.get("investigation_steps", []),
        mitigation_playbook=report_dict.get("mitigation_playbook", []),
        gemini_raw_output=str(report_dict)
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    
    record_audit_log(
        db,
        action="AI_REPORT_GENERATED",
        user=user_email,
        details={"report_id": report.id, "event_id": event.id, "model_used": report_dict.get("model_used")}
    )
    
    return {
        "report_id": report.id,
        "event_id": event.id,
        "title": report.title,
        "executive_summary": report.summary,
        "technical_analysis": report_dict.get("technical_analysis", ""),
        "attack_category": report.attack_vector,
        "mitre_attack": report.mitre_techniques or [],
        "why_suspicious": report_dict.get("why_suspicious", []),
        "investigation_steps": report.investigation_steps,
        "mitigation_playbook": report.mitigation_playbook,
        "confidence_assessment": report_dict.get("confidence_assessment", "High confidence"),
        "generated_at": report.created_at,
        "model_used": report_dict.get("model_used", "Gemini 1.5")
    }

@router.get("", response_model=List[dict])
def list_reports(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    reports = db.query(IncidentReport).order_by(IncidentReport.created_at.desc()).offset(offset).limit(limit).all()
    out = []
    for r in reports:
        out.append({
            "id": r.id,
            "event_id": r.event_id,
            "title": r.title,
            "summary": r.summary,
            "attack_vector": r.attack_vector,
            "mitre_techniques": r.mitre_techniques,
            "investigation_steps": r.investigation_steps,
            "mitigation_playbook": r.mitigation_playbook,
            "created_at": r.created_at
        })
    return out

@router.get("/{report_id}")
def get_report_detail(report_id: str, db: Session = Depends(get_db)):
    r = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Incident report not found.")
    return {
        "id": r.id,
        "event_id": r.event_id,
        "title": r.title,
        "summary": r.summary,
        "attack_vector": r.attack_vector,
        "mitre_techniques": r.mitre_techniques,
        "investigation_steps": r.investigation_steps,
        "mitigation_playbook": r.mitigation_playbook,
        "created_at": r.created_at
    }
