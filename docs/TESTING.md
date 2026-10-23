# IntelliTwin AI — Automated Testing & Quality Assurance Report

This document records the testing strategy, test coverage breakdown, automated test suites, execution commands, and verified test results for the **IntelliTwin AI** cybersecurity anomaly detection platform.

---

## 1. Testing Strategy & Pyramid

The testing architecture adheres to rigorous software engineering and scientific validation standards:
1. **Unit & Pipeline Tests (`tests/test_ml_pipeline.py`)**: Validates dataset provenance, strict 80/20 train/test split separation, preprocessing integrity, missing feature resilience, model inference parity, and SHAP explainer mathematical consistency.
2. **Integration & API Tests (`tests/test_backend_api.py`)**: Tests FastAPI REST routes, operational liveness/readiness probes, JWT authentication lifecycles, Role-Based Access Control (RBAC), request tracing headers (`X-Request-ID`), Pydantic schema validation, and Gemini GenAI fallback resilience.
3. **Frontend Compilation & Static Prerender Tests**: Verifies Next.js 16 App Router TypeScript type safety, static page generation, and client bundle compilation across all 6 core routes.

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
collected 27 items

tests/test_backend_api.py::test_api_root PASSED                          [  3%]
tests/test_backend_api.py::test_liveness_and_readiness_probes PASSED     [  7%]
tests/test_backend_api.py::test_request_correlation_and_timing_headers PASSED [ 11%]
tests/test_backend_api.py::test_get_attack_presets PASSED                [ 14%]
tests/test_backend_api.py::test_real_time_prediction_normal_traffic PASSED [ 18%]
tests/test_backend_api.py::test_real_time_prediction_ddos_traffic PASSED [ 22%]
tests/test_backend_api.py::test_prediction_input_validation_error PASSED [ 25%]
tests/test_backend_api.py::test_dynamic_model_metrics_endpoint PASSED    [ 29%]
tests/test_backend_api.py::test_dashboard_stats_endpoint PASSED          [ 33%]
tests/test_backend_api.py::test_admin_system_health PASSED               [ 37%]
tests/test_backend_api.py::test_authentication_login_success PASSED      [ 40%]
tests/test_backend_api.py::test_authentication_login_failure PASSED      [ 44%]
tests/test_backend_api.py::test_user_registration_and_duplicate_prevention PASSED [ 48%]
tests/test_backend_api.py::test_rbac_unauthorized_access PASSED          [ 51%]
tests/test_backend_api.py::test_rbac_authorized_admin_access PASSED      [ 55%]
tests/test_backend_api.py::test_rbac_insufficient_privilege PASSED       [ 59%]
tests/test_backend_api.py::test_genai_report_generation_and_fallback PASSED [ 62%]
tests/test_backend_api.py::test_invalid_event_report_not_found PASSED    [ 66%]
tests/test_ml_pipeline.py::test_unsw_dataset_files_exist PASSED          [ 70%]
tests/test_ml_pipeline.py::test_train_test_split_separation PASSED       [ 74%]
tests/test_ml_pipeline.py::test_serialized_models_exist PASSED           [ 77%]
tests/test_ml_pipeline.py::test_dynamic_metrics_schema_and_authenticity PASSED [ 81%]
tests/test_ml_pipeline.py::test_preprocessor_transformation PASSED       [ 85%]
tests/test_ml_pipeline.py::test_preprocessor_resilience_to_malformed_input PASSED [ 88%]
tests/test_ml_pipeline.py::test_model_inference_prediction PASSED        [ 92%]
tests/test_ml_pipeline.py::test_shap_explainer_computes_attributions PASSED [ 96%]
tests/test_ml_pipeline.py::test_experiment_manifest_integrity PASSED     [100%]

============================== 27 passed in 16.55s ==============================
```

- **Total Test Cases**: 27
- **Passed**: 27 (100%)
- **Failed**: 0
- **Execution Time**: 16.55 seconds

---

## 3. Test Case Catalog & Coverage Breakdown

### 3.1 Backend API & Security Tests (`tests/test_backend_api.py`)

| Test Identifier | Category | Verification Objective | Status |
| :--- | :--- | :--- | :--- |
| `test_api_root` | Smoke | Confirms API gateway returns service name and version | **PASSED** |
| `test_liveness_and_readiness_probes` | Health | Verifies `/health` returns 200 and `/ready` verifies database and loaded models | **PASSED** |
| `test_request_correlation_and_timing_headers`| Observability | Confirms `X-Request-ID` UUID is propagated and `X-Response-Time` header is present | **PASSED** |
| `test_get_attack_presets` | Telemetry | Ensures pre-configured attack presets (DDoS, Recon, Normal) are valid JSON | **PASSED** |
| `test_real_time_prediction_normal_traffic` | ML Serving | Evaluates normal packet flow; verifies Risk Score < 30 and Severity `LOW` | **PASSED** |
| `test_real_time_prediction_ddos_traffic` | ML Serving | Injects volumetric attack; verifies Risk Score > 80, Severity `CRITICAL`, and valid SHAP array | **PASSED** |
| `test_prediction_input_validation_error` | Defensive | Submits negative duration; verifies FastAPI returns `HTTP 422 Unprocessable Entity` | **PASSED** |
| `test_dynamic_model_metrics_endpoint` | Data Integrity | Confirms `/api/models/metrics` serves authentic metrics from `model_metrics.json` | **PASSED** |
| `test_dashboard_stats_endpoint` | Dashboard | Verifies real-time event aggregation and threat distribution | **PASSED** |
| `test_admin_system_health` | Admin | Validates admin diagnostics endpoint returning process memory, uptime, and DB status | **PASSED** |
| `test_authentication_login_success` | Auth | Authenticates valid analyst credentials and receives JWT bearer token | **PASSED** |
| `test_authentication_login_failure` | Auth | Rejects invalid password with `HTTP 401 Unauthorized` | **PASSED** |
| `test_user_registration_and_duplicate_prevention`| Auth | Tests analyst self-registration and enforces unique email constraint (`HTTP 400`) | **PASSED** |
| `test_rbac_unauthorized_access` | Security/RBAC | Rejects unauthenticated request to `/api/admin/audit-logs` with `HTTP 401` | **PASSED** |
| `test_rbac_authorized_admin_access` | Security/RBAC | Grants `ADMIN` user access to audit logs and system diagnostics | **PASSED** |
| `test_rbac_insufficient_privilege` | Security/RBAC | Denies `SECURITY_ANALYST` access to admin-only audit logs with `HTTP 403 Forbidden` | **PASSED** |
| `test_genai_report_generation_and_fallback` | GenAI | Requests AI incident report; verifies structured schema (MITRE ATT&CK, playbook, fallback flag) | **PASSED** |
| `test_invalid_event_report_not_found` | Defensive | Submits non-existent event ID; verifies `HTTP 404 Not Found` | **PASSED** |

### 3.2 Machine Learning & Pipeline Tests (`tests/test_ml_pipeline.py`)

| Test Identifier | Category | Verification Objective | Status |
| :--- | :--- | :--- | :--- |
| `test_unsw_dataset_files_exist` | Provenance | Confirms authentic UNSW-NB15 CSV files exist with size > 10MB | **PASSED** |
| `test_train_test_split_separation` | Zero-Leakage | Verifies 20,000 train and 5,000 test sets have non-overlapping indices and identical class distribution | **PASSED** |
| `test_serialized_models_exist` | Artifacts | Verifies all required `.joblib` files exist in `ml-engine/models/` | **PASSED** |
| `test_dynamic_metrics_schema_and_authenticity`| Integrity | Confirms `model_metrics.json` contains authentic non-fabricated metrics (XGBoost 94.48%) | **PASSED** |
| `test_preprocessor_transformation` | Preprocessing | Verifies `ColumnTransformer` transforms 42 features into a dense 42-column scaled numpy array | **PASSED** |
| `test_preprocessor_resilience_to_malformed_input`| Defensive | Tests handling of missing or NaN values; verifies median imputation and zero crashes | **PASSED** |
| `test_model_inference_prediction` | Inference | Confirms loaded XGBoost champion outputs probability tuple `[P(Normal), P(Anomaly)]` summing to 1.0 | **PASSED** |
| `test_shap_explainer_computes_attributions` | XAI | Verifies `TreeExplainer` calculates non-zero Shapley values for input features | **PASSED** |
| `test_experiment_manifest_integrity` | Governance | Confirms `experiment_manifest.json` contains dataset checksums, seeds, and hyperparameters | **PASSED** |

---

## 4. Frontend Compilation & Prerendering Verification

### 4.1 Execution Command
```bash
cd frontend
npm run build
```

### 4.2 Verified Next.js 16 Build Output
```text
▲ Next.js 16.4.2 (Turbopack)
✓ Running next.config.ts took 310ms
  Creating an optimized production build ...
✓ Compiled successfully in 6.5s
  Running TypeScript ...
  Finished TypeScript in 11.7s ...
  Collecting page data using 3 workers ...
✓ Generating static pages using 3 workers (9/9) in 1901ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /dashboard
├ ○ /detection
├ ○ /models
├ ○ /reports
└ ○ /settings

○  (Static)  prerendered as static content
```

- **TypeScript Compilation Errors**: 0
- **Routes Successfully Prerendered**: 6 core application routes (`/`, `/dashboard`, `/detection`, `/models`, `/reports`, `/settings`)
