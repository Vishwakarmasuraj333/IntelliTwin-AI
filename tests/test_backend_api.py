"""
Automated Test Suite: FastAPI Backend & Security Gateway
---------------------------------------------------------
Validates API endpoints, JWT auth, RBAC authorization, real-time prediction,
dynamic metrics serving, GenAI reporting, correlation IDs, readiness probes,
and rate limiting error handling.
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(TEST_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
from app.core.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_test_database():
    init_db()

@pytest.fixture
def client():
    return TestClient(app)

def test_api_root(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["platform"] == "IntelliTwin AI"
    assert data["status"] == "OPERATIONAL"

def test_liveness_and_readiness_probes(client):
    res_live = client.get("/health")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "LIVE"

    res_ready = client.get("/ready")
    assert res_ready.status_code in [200, 503]
    if res_ready.status_code == 200:
        data = res_ready.json()
        assert data["status"] == "READY"
        assert data["database"] == "CONNECTED"

def test_request_correlation_and_timing_headers(client):
    res = client.get("/")
    assert "x-request-id" in res.headers
    assert "x-response-time" in res.headers

def test_get_attack_presets(client):
    res = client.get("/api/detection/presets")
    assert res.status_code == 200
    presets = res.json()
    assert isinstance(presets, list)
    assert len(presets) >= 4
    assert any(p["name"] == "TCP SYN Flood DDoS Attempt" for p in presets)

def test_real_time_prediction_normal_traffic(client):
    normal_payload = {
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
    res = client.post("/api/detection/predict", json=normal_payload)
    assert res.status_code == 200
    data = res.json()
    assert "event_id" in data
    assert data["prediction"] in ["NORMAL", "ANOMALY"]
    assert 0 <= data["risk_score"] <= 100
    assert 0.0 <= data["classifier_probability"] <= 1.0
    assert "uncertainty" in data
    assert "shap_values" in data
    assert isinstance(data["shap_values"], list)

def test_real_time_prediction_ddos_traffic(client):
    ddos_payload = {
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
    res = client.post("/api/detection/predict", json=ddos_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"]
    assert data["risk_score"] >= 0
    assert len(data["shap_values"]) > 0

def test_prediction_input_validation_error(client):
    """Verify negative duration or invalid fields return HTTP 422."""
    invalid_payload = {
        "proto": "tcp",
        "dur": -10.0, # Negative duration is invalid
        "sbytes": 1000
    }
    res = client.post("/api/detection/predict", json=invalid_payload)
    assert res.status_code == 422

def test_dynamic_model_metrics_endpoint(client):
    res = client.get("/api/models/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "XGBoost" in data["models"]
    assert "accuracy" in data["models"]["XGBoost"]
    assert "confusion_matrix" in data["models"]["XGBoost"]

def test_dashboard_stats_endpoint(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    data = res.json()
    assert data["total_analyzed"] >= 0
    assert 0.0 <= data["anomaly_rate_percent"] <= 100.0
    assert isinstance(data["timeline"], list)
    assert isinstance(data["attack_distribution"], list)

def test_admin_system_health(client):
    res = client.get("/api/admin/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert data["ml_models_loaded"] is True
    assert data["active_model"]

def test_authentication_login_success(client):
    login_payload = {
        "email": "admin@intellitwin.ai",
        "password": "Admin@123456"
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "ADMIN"

def test_authentication_login_failure(client):
    login_payload = {
        "email": "admin@intellitwin.ai",
        "password": "WrongPassword999"
    }
    res = client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 401

def test_user_registration_and_duplicate_prevention(client):
    test_email = "analyst_temp_test@intellitwin.ai"
    reg_payload = {
        "name": "Audit Test Analyst",
        "email": test_email,
        "password": "SecurePassword@123",
        "role": "SECURITY_ANALYST"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code in [201, 400] # 201 if first time, 400 if already exists
    
    # Attempt duplicate registration -> must return 400
    res_dup = client.post("/api/auth/register", json=reg_payload)
    assert res_dup.status_code == 400

def test_rbac_unauthorized_access(client):
    """Accessing admin audit logs without token must be rejected with 401."""
    res = client.get("/api/admin/audit-logs")
    assert res.status_code == 401

def test_rbac_authorized_admin_access(client):
    """Admin user with valid JWT can access audit logs."""
    login_res = client.post("/api/auth/login", json={
        "email": "admin@intellitwin.ai",
        "password": "Admin@123456"
    })
    token = login_res.json()["access_token"]
    res = client.get("/api/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert isinstance(res.json(), list)

def test_rbac_insufficient_privilege(client):
    """Analyst user attempting to switch models must be rejected with 403 Forbidden."""
    analyst_login = client.post("/api/auth/login", json={
        "email": "analyst@intellitwin.ai",
        "password": "Analyst@123456"
    })
    analyst_token = analyst_login.json()["access_token"]
    res = client.post("/api/models/switch/XGBoost", headers={"Authorization": f"Bearer {analyst_token}"})
    assert res.status_code == 403

def test_genai_report_generation_and_fallback(client):
    predict_res = client.post("/api/detection/predict", json={
        "proto": "tcp", "dur": 0.01, "sbytes": 5000, "dbytes": 0, "spkts": 100, "dpkts": 0
    })
    event_id = predict_res.json()["event_id"]
    
    report_res = client.post("/api/reports/generate", json={"event_id": event_id})
    assert report_res.status_code == 200
    rep_data = report_res.json()
    assert "executive_summary" in rep_data
    assert "technical_analysis" in rep_data
    assert "why_suspicious" in rep_data
    assert "investigation_steps" in rep_data
    assert "mitigation_playbook" in rep_data
    assert "evidence_sources" in rep_data
    assert "limitations" in rep_data
    assert len(rep_data["investigation_steps"]) > 0
    assert len(rep_data["mitigation_playbook"]) > 0

def test_invalid_event_report_not_found(client):
    res = client.post("/api/reports/generate", json={"event_id": "non-existent-uuid-9999"})
    assert res.status_code == 404
