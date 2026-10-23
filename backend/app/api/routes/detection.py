"""
Real-Time Detection & Network Simulator API Endpoints
-----------------------------------------------------
Asynchronous, threadpool-offloaded inference gateway for cybersecurity telemetry.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.api.deps import get_db, get_optional_user
from app.core.rate_limit import predict_limiter
from app.models.user import User
from app.models.event import SecurityEvent
from app.schemas.detection import NetworkPacketInput, PredictionResponse, ShapFeature
from app.services.ml_service import ml_engine
from app.services.shap_service import shap_service
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/detection", tags=["ML Detection & Simulator"])

REALISTIC_PRESETS = [
    {
        "name": "Standard HTTPS Web Traffic",
        "description": "Legitimate secure web browsing session with balanced packet ratios and normal durations.",
        "category": "Normal",
        "payload": {
            "proto": "tcp",
            "dur": 0.45,
            "sbytes": 1420,
            "dbytes": 8900,
            "spkts": 14,
            "dpkts": 22,
            "service": "http",
            "state": "FIN",
            "ct_srv_src": 2,
            "ct_dst_ltm": 3,
            "ct_src_dport_ltm": 1,
            "ct_dst_sport_ltm": 1,
            "ct_dst_src_ltm": 2,
            "sttl": 64,
            "dttl": 60,
            "sloss": 0,
            "dloss": 0
        }
    },
    {
        "name": "TCP SYN Flood DDoS Attempt",
        "description": "Extreme packet volume of tiny packets with no response bytes and high destination connection count.",
        "category": "DoS",
        "payload": {
            "proto": "tcp",
            "dur": 0.005,
            "sbytes": 32000,
            "dbytes": 0,
            "spkts": 800,
            "dpkts": 0,
            "service": "-",
            "state": "INT",
            "ct_srv_src": 45,
            "ct_dst_ltm": 48,
            "ct_src_dport_ltm": 38,
            "ct_dst_sport_ltm": 1,
            "ct_dst_src_ltm": 45,
            "sttl": 254,
            "dttl": 0,
            "sloss": 18,
            "dloss": 0
        }
    },
    {
        "name": "Nmap Aggressive Port Scan",
        "description": "Sweeping distinct destination ports with low dwell times and high distinct port counters.",
        "category": "Reconnaissance",
        "payload": {
            "proto": "tcp",
            "dur": 0.02,
            "sbytes": 480,
            "dbytes": 40,
            "spkts": 8,
            "dpkts": 1,
            "service": "-",
            "state": "REQ",
            "ct_srv_src": 15,
            "ct_dst_ltm": 24,
            "ct_src_dport_ltm": 32,
            "ct_dst_sport_ltm": 28,
            "ct_dst_src_ltm": 20,
            "sttl": 64,
            "dttl": 0,
            "sloss": 1,
            "dloss": 0
        }
    },
    {
        "name": "Remote Code Execution Exploit Payload",
        "description": "Single outbound connection with oversized byte payloads, packet fragmentation, and anomalous states.",
        "category": "Exploits",
        "payload": {
            "proto": "tcp",
            "dur": 2.8,
            "sbytes": 245000,
            "dbytes": 1200,
            "spkts": 180,
            "dpkts": 12,
            "service": "http",
            "state": "CON",
            "ct_srv_src": 4,
            "ct_dst_ltm": 2,
            "ct_src_dport_ltm": 2,
            "ct_dst_sport_ltm": 1,
            "ct_dst_src_ltm": 2,
            "sttl": 62,
            "dttl": 60,
            "sloss": 4,
            "dloss": 1
        }
    },
    {
        "name": "Protocol Fuzzing Attack",
        "description": "High packet corruption and retransmission loss across non-standard transport configurations.",
        "category": "Fuzzers",
        "payload": {
            "proto": "udp",
            "dur": 1.2,
            "sbytes": 18500,
            "dbytes": 200,
            "spkts": 95,
            "dpkts": 2,
            "service": "dns",
            "state": "INT",
            "ct_srv_src": 12,
            "ct_dst_ltm": 10,
            "ct_src_dport_ltm": 8,
            "ct_dst_sport_ltm": 6,
            "ct_dst_src_ltm": 8,
            "sttl": 254,
            "dttl": 29,
            "sloss": 14,
            "dloss": 8
        }
    }
]

@router.get("/presets")
def get_attack_presets():
    """Returns curated realistic network telemetry presets for testing."""
    return REALISTIC_PRESETS

@router.post("/predict", response_model=PredictionResponse)
async def predict_network_event(
    request: Request,
    packet: NetworkPacketInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    predict_limiter.check(request)
    if ml_engine.model is None or ml_engine.preprocessor is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Machine learning inference model or preprocessor is not loaded. Train or deploy models before inference."
        )

    # 1. Run Machine Learning Inference offloaded from event loop
    raw_dict = packet.model_dump()
    result = await run_in_threadpool(ml_engine.predict, raw_dict)
    
    # 2. Compute Explainable AI (SHAP) attributions offloaded from event loop
    shap_factors, base_val, shap_status = await run_in_threadpool(
        shap_service.explain_instance, result["enriched_features"], 8
    )
    
    # 3. Persist Event into Database
    user_id = current_user.id if current_user else None
    user_email = current_user.email if current_user else "anonymous_analyst"
    
    event = SecurityEvent(
        user_id=user_id,
        event_data=result["enriched_features"],
        prediction=result["prediction"],
        confidence=result["confidence"],
        risk_score=result["risk_score"],
        severity=result["severity"],
        attack_category=result["attack_category"],
        shap_explanation=shap_factors,
        model_version=result["model_version"]
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # 4. Log Audit Trail
    record_audit_log(
        db,
        action="INFERENCE_EXECUTED",
        user=user_email,
        details={
            "event_id": event.id,
            "prediction": result["prediction"],
            "risk_score": result["risk_score"],
            "severity": result["severity"]
        }
    )
    
    return {
        "event_id": event.id,
        "prediction": result["prediction"],
        "confidence": result["confidence"],
        "classifier_probability": result["classifier_probability"],
        "risk_score": result["risk_score"],
        "anomaly_score": result["anomaly_score"],
        "uncertainty": result["uncertainty"],
        "severity": result["severity"],
        "attack_category": result["attack_category"],
        "model_name": result["model_name"],
        "model_version": result["model_version"],
        "shap_values": shap_factors,
        "base_value": base_val,
        "shap_status": shap_status,
        "analyzed_at": event.created_at,
        "input_features": result["enriched_features"]
    }
