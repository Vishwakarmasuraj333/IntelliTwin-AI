"""
Automated Test Suite: FastAPI Backend & Endpoints
--------------------------------------------------
Validates API endpoints, JWT auth, real-time prediction,
dynamic metrics serving, GenAI reporting, and graceful error handling.
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
    assert "shap_values" in data
    assert isinstance(data["shap_values"], list)
    assert len(data["shap_values"]) > 0

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
    # Must compute risk and SHAP
    assert data["risk_score"] >= 0
    assert len(data["shap_values"]) > 0

def test_dynamic_model_metrics_endpoint(client):
    res = client.get("/api/models/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "Random Forest" in data["models"]
    assert "accuracy" in data["models"]["Random Forest"]
    assert "confusion_matrix" in data["models"]["Random Forest"]

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

def test_genai_report_generation_and_fallback(client):
    # 1. First trigger an event to have an event_id
    predict_res = client.post("/api/detection/predict", json={
        "proto": "tcp", "dur": 0.01, "sbytes": 5000, "dbytes": 0, "spkts": 100, "dpkts": 0
    })
    event_id = predict_res.json()["event_id"]
    
    # 2. Trigger report generation
    report_res = client.post("/api/reports/generate", json={"event_id": event_id})
    assert report_res.status_code == 200
    rep_data = report_res.json()
    assert "executive_summary" in rep_data
    assert "technical_analysis" in rep_data
    assert "why_suspicious" in rep_data
    assert "investigation_steps" in rep_data
    assert "mitigation_playbook" in rep_data
    assert len(rep_data["investigation_steps"]) > 0
    assert len(rep_data["mitigation_playbook"]) > 0

def test_invalid_event_report_not_found(client):
    res = client.post("/api/reports/generate", json={"event_id": "non-existent-uuid-9999"})
    assert res.status_code == 404
