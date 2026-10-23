"""
Automated End-to-End Live User Flow Integration Test
----------------------------------------------------
Validates the complete analyst workflow:
Login -> Dashboard Stats -> Submit Network Telemetry -> ML Inference & Calibrated Risk
-> SHAP TreeExplainer Attributions -> Event Persistence -> GenAI Report (Offline/Fallback & Active)
-> Report Persistence -> Report Archive Retrieval.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from app.core.database import SessionLocal, init_db
from app.models.event import SecurityEvent
from app.models.report import IncidentReport
from app.models.user import User

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_full_live_analyst_flow_e2e(client):
    # --------------------------------------------------------------------------
    # Step 1: Login as Security Analyst
    # --------------------------------------------------------------------------
    login_res = client.post("/api/auth/login", json={
        "email": "analyst@intellitwin.ai",
        "password": "Analyst@123456"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    auth_data = login_res.json()
    token = auth_data["access_token"]
    assert auth_data["user"]["role"] == "SECURITY_ANALYST"
    headers = {"Authorization": f"Bearer {token}"}

    # --------------------------------------------------------------------------
    # Step 2: Dashboard Overview Telemetry Query
    # --------------------------------------------------------------------------
    dash_res = client.get("/api/dashboard/stats", headers=headers)
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert "total_analyzed" in dash_data
    assert "anomaly_rate_percent" in dash_data
    assert isinstance(dash_data["attack_distribution"], list)

    # --------------------------------------------------------------------------
    # Step 3: Submit Network Flow Telemetry (Authentic UNSW-NB15 Anomaly)
    # --------------------------------------------------------------------------
    flow_payload = {
        "proto": "unas",
        "dur": 0.000005,
        "sbytes": 200,
        "dbytes": 0,
        "spkts": 2,
        "dpkts": 0,
        "service": "-",
        "state": "INT",
        "ct_srv_src": 7,
        "ct_dst_ltm": 5,
        "ct_src_dport_ltm": 4,
        "ct_dst_sport_ltm": 4,
        "ct_dst_src_ltm": 10,
        "sttl": 254,
        "dttl": 0,
        "sloss": 0,
        "dloss": 0,
        "rate": 200000.0
    }
    pred_res = client.post("/api/detection/predict", json=flow_payload, headers=headers)
    assert pred_res.status_code == 200, f"Inference failed: {pred_res.text}"
    pred_data = pred_res.json()

    # Verify ML Inference & Risk Calibration outputs
    assert pred_data["prediction"] == "ANOMALY"
    assert pred_data["risk_score"] >= 80.0
    assert pred_data["severity"] in ["HIGH", "CRITICAL"]
    assert 0.0 <= pred_data["uncertainty"] <= 1.0
    assert pred_data["classifier_probability"] > 0.8
    assert pred_data["model_name"] in ["XGBoost", "Random Forest"]

    # Verify SHAP TreeExplainer Attributions
    shap_vals = pred_data["shap_values"]
    assert len(shap_vals) > 0
    assert all("shap_value" in s and "direction" in s for s in shap_vals)

    event_id = pred_data["event_id"]
    assert event_id is not None

    # Verify Database Persistence of SecurityEvent
    db = SessionLocal()
    try:
        saved_event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
        assert saved_event is not None
        assert saved_event.prediction == "ANOMALY"
        assert saved_event.risk_score == pred_data["risk_score"]
        assert saved_event.severity == pred_data["severity"]
    finally:
        db.close()

    # --------------------------------------------------------------------------
    # Step 4: Generate GenAI Incident Report (Offline / Autonomous Fallback Case)
    # --------------------------------------------------------------------------
    report_res = client.post(
        "/api/reports/generate",
        json={"event_id": event_id, "custom_notes": "Analyst verified anomalous burst on internal gateway."},
        headers=headers
    )
    assert report_res.status_code == 200, f"Report generation failed: {report_res.text}"
    report_data = report_res.json()

    assert report_data["event_id"] == event_id
    assert report_data["report_id"] is not None
    assert "executive_summary" in report_data and len(report_data["executive_summary"]) > 0
    assert "technical_analysis" in report_data and len(report_data["technical_analysis"]) > 0
    assert isinstance(report_data["mitre_attack"], list) and len(report_data["mitre_attack"]) > 0
    assert isinstance(report_data["investigation_steps"], list) and len(report_data["investigation_steps"]) >= 3
    assert isinstance(report_data["mitigation_playbook"], list) and len(report_data["mitigation_playbook"]) >= 3
    
    # Offline report must explicitly identify as fallback and not fabricate live AI
    assert report_data["is_ai_generated"] is False
    assert "Fallback" in report_data["model_used"] or "Autonomous" in report_data["model_used"]
    assert "candidate vectors" in report_data["limitations"].lower() or "deterministic" in report_data["limitations"].lower()

    # --------------------------------------------------------------------------
    # Step 5: Verify IncidentReport Persistence in Database
    # --------------------------------------------------------------------------
    report_id = report_data["report_id"]
    db = SessionLocal()
    try:
        saved_report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()
        assert saved_report is not None
        assert saved_report.event_id == event_id
        assert saved_report.title == report_data["title"]
        assert saved_report.summary == report_data["executive_summary"]
    finally:
        db.close()

    # --------------------------------------------------------------------------
    # Step 6: Query Incident Reports Archive (GET /api/reports)
    # --------------------------------------------------------------------------
    archive_res = client.get("/api/reports", headers=headers)
    assert archive_res.status_code == 200
    archive_data = archive_res.json()
    assert isinstance(archive_data, list)
    matching = [r for r in archive_data if r.get("report_id") == report_id or r.get("id") == report_id]
    assert len(matching) >= 1, "Saved report not found in reports archive listing"
    retrieved = matching[0]
    assert retrieved["title"] == report_data["title"]
    assert retrieved["executive_summary"] == report_data["executive_summary"]
    assert len(retrieved["investigation_steps"]) > 0
    assert len(retrieved["mitigation_playbook"]) > 0

    # --------------------------------------------------------------------------
    # Step 7: Query Single Report Detail (GET /api/reports/{report_id})
    # --------------------------------------------------------------------------
    detail_res = client.get(f"/api/reports/{report_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data.get("report_id") == report_id or detail_data.get("id") == report_id
    assert detail_data["title"] == report_data["title"]

def test_configured_gemini_mocked_success_flow(client):
    """Verifies behavior when Gemini API is actively configured and succeeds."""
    # First create an anomaly event
    pred_res = client.post("/api/detection/predict", json={
        "proto": "unas", "dur": 0.000005, "sbytes": 200, "dbytes": 0, "spkts": 2, "dpkts": 0,
        "rate": 200000.0, "sttl": 254, "state": "INT"
    })
    event_id = pred_res.json()["event_id"]

    # Mock response from Gemini
    mock_gemini_json = (
        '{\n'
        '  "title": "Suspected Distributed Denial-of-Service (DDoS) Flood Attack",\n'
        '  "executive_summary": "High-volume unidirectional flood detected from unassigned protocol.",\n'
        '  "technical_analysis": "Flow exhibits zero response bytes with 200k pkts/s rate.",\n'
        '  "attack_category": "Denial of Service",\n'
        '  "mitre_attack": [{"id": "T1498.001", "name": "Direct Network Flood", "tactic": "Impact"}],\n'
        '  "why_suspicious": ["Extreme packet rate", "Zero return traffic"],\n'
        '  "investigation_steps": ["Inspect firewall connection table", "Trace source subnet routing", "Block anomalous IP"],\n'
        '  "mitigation_playbook": ["Enable ingress filtering", "Apply rate-limiting ACL at perimeter", "Update firewall drop policy"],\n'
        '  "confidence_assessment": "High confidence based on UNSW-NB15 flow characteristics",\n'
        '  "evidence_sources": ["XGBoost probability 0.99", "SHAP rate factor +0.34"],\n'
        '  "limitations": "Model evaluated on flow telemetry; encrypted payload uninspected."\n'
        '}'
    )

    mock_response = MagicMock()
    mock_response.text = mock_gemini_json
    mock_model = MagicMock()
    mock_model.generate_content.return_value = mock_response

    from app.services.gemini_service import gemini_analyst
    original_key = gemini_analyst.api_key
    gemini_analyst.api_key = "test_mock_api_key_ai_za_123"

    try:
        with patch("google.generativeai.GenerativeModel", return_value=mock_model):
            report_res = client.post(
                "/api/reports/generate",
                json={"event_id": event_id}
            )

        assert report_res.status_code == 200
        data = report_res.json()
        assert data["is_ai_generated"] is True
        assert "Gemini" in data["model_used"]
        assert any(m["id"] == "T1498.001" for m in data["mitre_attack"])
    finally:
        gemini_analyst.api_key = original_key
