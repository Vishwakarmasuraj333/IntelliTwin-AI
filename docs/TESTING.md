# IntelliTwin AI — Automated Testing & Quality Assurance Report

This document records the testing strategy, test coverage breakdown, automated test suites, execution commands, and verified test results for the **IntelliTwin AI** cybersecurity anomaly detection platform.

---

## 1. Testing Strategy & Pyramid

The testing architecture adheres to rigorous software engineering and scientific validation standards:
1. **Unit & Pipeline Tests (`tests/test_ml_pipeline.py`)**: Validates dataset provenance, strict 80/20 train/test split separation, preprocessing integrity, missing feature resilience, model inference parity, and SHAP explainer mathematical consistency.
2. **Integration & API Tests (`tests/test_backend_api.py`)**: Tests FastAPI REST routes, operational liveness/readiness probes, JWT authentication lifecycles, Role-Based Access Control (RBAC), request tracing headers (`X-Request-ID`), Pydantic schema validation, and Gemini GenAI fallback resilience.
3. **Live User Flow & Integration Tests (`tests/test_live_e2e_flow.py`)**: Tests the full analyst journey from login to dashboard, packet prediction, SHAP waterfall, incident report generation, database persistence, and report history retrieval.
4. **Frontend Compilation & Static Prerender Tests**: Verifies Next.js 16 App Router TypeScript type safety, static page generation, and client bundle compilation across all 6 core routes.

---

## 2. Automated Backend & ML Test Suite Execution

### 2.1 Execution Command
```bash
python -m pytest tests/ -v
```

### 2.2 Verified Execution Log & Test Results
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\Users\imdee\.gemini\antigravity-ide\scratch\IntelliTwin-AI
plugins: anyio-4.15.1
collected 29 items

tests/test_backend_api.py::test_api_root PASSED                          [  3%]
tests/test_backend_api.py::test_liveness_and_readiness_probes PASSED     [  6%]
tests/test_backend_api.py::test_request_correlation_and_timing_headers PASSED [ 10%]
tests/test_backend_api.py::test_get_attack_presets PASSED                [ 13%]
tests/test_backend_api.py::test_real_time_prediction_normal_traffic PASSED [ 17%]
tests/test_backend_api.py::test_real_time_prediction_ddos_traffic PASSED [ 20%]
tests/test_backend_api.py::test_prediction_input_validation_error PASSED [ 24%]
tests/test_backend_api.py::test_dynamic_model_metrics_endpoint PASSED    [ 27%]
tests/test_backend_api.py::test_dashboard_stats_endpoint PASSED          [ 31%]
tests/test_backend_api.py::test_admin_system_health PASSED               [ 34%]
tests/test_backend_api.py::test_authentication_login_success PASSED      [ 37%]
tests/test_backend_api.py::test_authentication_login_failure PASSED      [ 41%]
tests/test_backend_api.py::test_user_registration_and_duplicate_prevention PASSED [ 44%]
tests/test_backend_api.py::test_rbac_unauthorized_access PASSED          [ 48%]
tests/test_backend_api.py::test_rbac_authorized_admin_access PASSED      [ 51%]
tests/test_backend_api.py::test_rbac_insufficient_privilege PASSED       [ 55%]
tests/test_backend_api.py::test_genai_report_generation_and_fallback PASSED [ 58%]
tests/test_backend_api.py::test_invalid_event_report_not_found PASSED    [ 62%]
tests/test_live_e2e_flow.py::test_full_live_analyst_flow_e2e PASSED      [ 65%]
tests/test_live_e2e_flow.py::test_configured_gemini_mocked_success_flow PASSED [ 68%]
tests/test_ml_pipeline.py::test_unsw_dataset_files_exist PASSED          [ 72%]
tests/test_ml_pipeline.py::test_train_test_split_separation PASSED       [ 75%]
tests/test_ml_pipeline.py::test_serialized_models_exist PASSED           [ 79%]
tests/test_ml_pipeline.py::test_dynamic_metrics_schema_and_authenticity PASSED [ 82%]
tests/test_ml_pipeline.py::test_preprocessor_transformation PASSED       [ 86%]
tests/test_ml_pipeline.py::test_preprocessor_resilience_to_malformed_input PASSED [ 89%]
tests/test_ml_pipeline.py::test_model_inference_prediction PASSED        [ 93%]
tests/test_ml_pipeline.py::test_shap_explainer_computes_attributions PASSED [ 96%]
tests/test_ml_pipeline.py::test_experiment_manifest_integrity PASSED     [100%]

============================== 29 passed in 16.20s ==============================
```

- **Total Test Cases**: 29
- **Passed**: 29 (100%)
- **Failed**: 0
- **Execution Time**: 16.20 seconds

---

## 3. Test Case Catalog & Coverage Breakdown

### 3.1 Backend API & Security Tests (`tests/test_backend_api.py` — 18 Tests)

| Test Identifier | Category | Verification Objective | Status |
| :--- | :--- | :--- | :--- |
| `test_api_root` | Smoke | Confirms API gateway returns service name and version | **PASSED** |
| `test_liveness_and_readiness_probes` | Health | Verifies `/health` returns 200 and `/ready` verifies database and loaded models | **PASSED** |
| `test_request_correlation_and_timing_headers`| Observability | Confirms `X-Request-ID` UUID is propagated and `X-Response-Time` header is present | **PASSED** |
| `test_get_attack_presets` | Telemetry | Ensures pre-configured attack presets (DDoS, Recon, Normal) are valid JSON | **PASSED** |
| `test_real_time_prediction_normal_traffic` | ML Serving | Evaluates normal packet flow; verifies Risk Score < 40 and valid output schema | **PASSED** |
| `test_real_time_prediction_ddos_traffic` | ML Serving | Injects volumetric attack; verifies risk evaluation and non-empty SHAP array | **PASSED** |
| `test_prediction_input_validation_error` | Defensive | Submits negative duration; verifies FastAPI returns `HTTP 422 Unprocessable Entity` | **PASSED** |
| `test_dynamic_model_metrics_endpoint` | Data Integrity | Confirms `/api/models/metrics` serves authentic metrics from `model_metrics.json` | **PASSED** |
| `test_dashboard_stats_endpoint` | Dashboard | Verifies real-time event aggregation and threat distribution | **PASSED** |
| `test_admin_system_health` | Admin | Validates admin diagnostics endpoint returning process memory, uptime, and DB status | **PASSED** |
| `test_authentication_login_success` | Auth | Authenticates valid analyst credentials and receives JWT bearer token | **PASSED** |
| `test_authentication_login_failure` | Auth | Rejects invalid password with `HTTP 401 Unauthorized` | **PASSED** |
| `test_user_registration_and_duplicate_prevention`| Auth | Tests analyst self-registration and enforces unique email constraint (`HTTP 400`) | **PASSED** |
| `test_rbac_unauthorized_access` | Security/RBAC | Rejects unauthenticated request to `/api/admin/audit-logs` with `HTTP 401` | **PASSED** |
| `test_rbac_authorized_admin_access` | Security/RBAC | Grants `ADMIN` user access to audit logs and system diagnostics | **PASSED** |
| `test_rbac_insufficient_privilege` | Security/RBAC | Denies `SECURITY_ANALYST` access to admin-only model switching with `HTTP 403 Forbidden` | **PASSED** |
| `test_genai_report_generation_and_fallback` | GenAI | Requests AI incident report; verifies structured schema (MITRE ATT&CK, playbook) | **PASSED** |
| `test_invalid_event_report_not_found` | Defensive | Submits non-existent event ID; verifies `HTTP 404 Not Found` | **PASSED** |

### 3.2 Machine Learning & Pipeline Tests (`tests/test_ml_pipeline.py` — 9 Tests)

| Test Identifier | Category | Verification Objective | Status |
| :--- | :--- | :--- | :--- |
| `test_unsw_dataset_files_exist` | Provenance | Confirms authentic UNSW-NB15 CSV files exist with size > 10MB | **PASSED** |
| `test_train_test_split_separation` | Zero-Leakage | Verifies 20,000 train and 5,000 test sets have non-overlapping indices and identical class distribution | **PASSED** |
| `test_serialized_models_exist` | Artifacts | Verifies all required `.joblib` files exist in `ml-engine/models/` | **PASSED** |
| `test_dynamic_metrics_schema_and_authenticity`| Integrity | Confirms `model_metrics.json` contains authentic non-fabricated metrics (XGBoost 94.48%) | **PASSED** |
| `test_preprocessor_transformation` | Preprocessing | Verifies `ColumnTransformer` transforms 24 features into scaled array | **PASSED** |
| `test_preprocessor_resilience_to_malformed_input`| Defensive | Tests handling of missing or NaN values; verifies median imputation and zero crashes | **PASSED** |
| `test_model_inference_prediction` | Inference | Confirms loaded XGBoost champion outputs probability tuple `[P(Normal), P(Anomaly)]` summing to 1.0 | **PASSED** |
| `test_shap_explainer_computes_attributions` | XAI | Verifies `TreeExplainer` calculates non-zero Shapley values for input features | **PASSED** |
| `test_experiment_manifest_integrity` | Governance | Confirms `experiment_manifest.json` contains dataset checksums, seeds, and hyperparameters | **PASSED** |

### 3.3 Live User Flow & E2E Integration Tests (`tests/test_live_e2e_flow.py` — 2 Tests)

| Test Identifier | Category | Verification Objective | Status |
| :--- | :--- | :--- | :--- |
| `test_full_live_analyst_flow_e2e` | End-to-End | Validates complete user flow: login as analyst, dashboard query, packet prediction, SHAP waterfall, database persistence, offline GenAI fallback report, and archive retrieval. | **PASSED** |
| `test_configured_gemini_mocked_success_flow` | GenAI / Mock | Simulates active Google Gemini API response; verifies Pydantic v2 structured validation, MITRE ATT&CK extraction, and `is_ai_generated: true` tagging. | **PASSED** |

---

## 4. Distinction Between GenAI Execution Modes

To ensure academic and professional transparency, tests distinguish between three operational GenAI states:

1. **Autonomous Deterministic Fallback Mode (Tested in `test_full_live_analyst_flow_e2e`)**:
   - Executes when `GEMINI_API_KEY` is omitted, offline, or rate-limited.
   - Evaluates telemetry using internal deterministic rule heuristics and SHAP feature attributions.
   - Outputs: `is_ai_generated: false`, `model_used: "Autonomous SOC Fallback Engine"`.
   - Discloses explicitly in limitations that MITRE techniques represent candidate vectors rather than verified attribution.
2. **Mocked Gemini API Mode (Tested in `test_configured_gemini_mocked_success_flow`)**:
   - Mocks `google.generativeai.GenerativeModel.generate_content` returning RFC 8259 JSON.
   - Verifies that server-side Pydantic validation (`GeminiStructuredReport`), error handling, and database insertion execute correctly without incurring Google Cloud billing or requiring active internet access.
   - Outputs: `is_ai_generated: true`, `model_used: "Google Gemini (gemini-1.5-flash)"`.
3. **Live Production Gemini Mode**:
   - Activated when a genuine `GEMINI_API_KEY` is provided in the environment.
   - Calls the live Gemini 1.5 Flash endpoint over TLS with a 15-second timeout and 2-attempt bounded retry budget.

---

## 5. Deployment Status Clarification

> **Important**: All tests, builds, and evaluations documented herein were executed and verified **locally** within the development environment (`Python 3.12.10`, `Node v22.20.0`, `Next.js 16.4.2`).
>
> While production container configurations ([backend/Dockerfile](file:///C:/Users/imdee/.gemini/antigravity-ide/scratch/IntelliTwin-AI/backend/Dockerfile), [frontend/Dockerfile](file:///C:/Users/imdee/.gemini/antigravity-ide/scratch/IntelliTwin-AI/frontend/Dockerfile), [docker-compose.yml](file:///C:/Users/imdee/.gemini/antigravity-ide/scratch/IntelliTwin-AI/docker-compose.yml)) and cloud deployment playbooks ([docs/DEPLOYMENT.md](file:///C:/Users/imdee/.gemini/antigravity-ide/scratch/IntelliTwin-AI/docs/DEPLOYMENT.md)) have been authored and verified, **no public cloud deployment is currently active or claimed**.
