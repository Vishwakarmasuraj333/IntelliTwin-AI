# IntelliTwin AI — Operations & Production Runbook

This runbook defines the operational standards, maintenance protocols, monitoring criteria, model lifecycle workflows, and incident response procedures for the **IntelliTwin AI** cybersecurity platform.

---

## 1. System Topology & Process Architecture

The platform operates across three tiers:
1. **Frontend**: Next.js 16 App Router on Node.js 22 runtime. Prerendered statically with dynamic client fetching against the backend API.
2. **Backend**: FastAPI asynchronous REST API on Python 3.12, running under Uvicorn with multiprocessing worker pools.
3. **ML Inference Layer**: In-memory joblib models loaded once during worker initialization and cached in memory to eliminate per-request disk I/O.
4. **Database**: PostgreSQL 16 (production) with automatic fallback to SQLite for zero-configuration local development.

```
[Edge Load Balancer / Reverse Proxy]
                 │
     ┌───────────┴───────────┐
     ▼                       ▼
[Next.js Frontend]    [FastAPI API Workers]
(Node 22 / Port 3000) (Uvicorn / Port 8000)
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     [PostgreSQL DB]  [ML Models RAM]  [Google Gemini API]
     (Persistent)     (Zero-I/O Cache) (Tier-3 SOC LLM)
```

---

## 2. Model Lifecycle, Rollback & Serving Strategy

### 2.1 Model Caching Strategy
- Model weights (`xgboost.joblib`, `random_forest.joblib`, `isolation_forest.joblib`), preprocessing pipelines (`preprocessor.joblib`), and SHAP explainers (`shap_explainer.joblib`) are **lazy-loaded and cached as singletons in memory** within `backend/app/services/ml_service.py` and `shap_service.py`.
- **Zero Request-Blocking Loading**: Models are NOT reloaded from disk on individual HTTP requests. Average inference latency is maintained under 15ms.

### 2.2 Model Versioning & Provenance
Every model artifact corresponds to a pinned record in `ml-engine/evaluation/experiment_manifest.json` containing:
- Model version identifier (e.g., `v2.1.0-unsw-nb15`)
- SHA-256 artifact checksums
- Feature schema (`feature_names.json`)
- Training timestamp and hyperparameters
- 5-Fold Stratified Cross-Validation scores and held-out test metrics

### 2.3 Hot Rollback Procedure
If model drift, degradation, or false positives are observed in production:
1. Revert `backend/app/core/config.py` default model or update environment variable:
   ```bash
   DEFAULT_MODEL_NAME=random_forest  # Or previous validated checkpoint
   ```
2. Trigger graceful reload of Uvicorn worker processes:
   ```bash
   kill -HUP <uvicorn_master_pid>
   ```
3. To roll back serialized weights entirely:
   ```bash
   cp -r /app/ml-engine/models_archive/v2.0.0/* /app/ml-engine/models/
   touch /app/backend/main.py  # Triggers hot reload in containerized environments
   ```

---

## 3. High Availability, Liveness & Readiness Probes

FastAPI exposes two dedicated operational probes:

### 3.1 Liveness Probe (`GET /health`)
- Checks process responsiveness and host resource availability.
- **HTTP 200**: Service process is healthy and accepting TCP connections.
- Kubernetes / ECS Configuration:
  ```yaml
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 15
    timeoutSeconds: 3
    failureThreshold: 3
  ```

### 3.2 Readiness Probe (`GET /ready`)
- Validates that:
  1. Primary database connectivity is verified (`SELECT 1`).
  2. Champion ML model artifact is loaded and functional in RAM.
  3. Preprocessor pipeline is operational.
- **HTTP 200**: Platform is fully initialized to handle network flow predictions.
- **HTTP 503**: System is warming up or experiencing database disconnection. Traffic is held at the load balancer.
  ```yaml
  readinessProbe:
    httpGet:
      path: /ready
      port: 8000
    initialDelaySeconds: 15
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 2
  ```

---

## 4. Concurrency Bounds & Resource Limits

| Resource | Development | Recommended Production |
| :--- | :--- | :--- |
| **Worker Count** | 1 process (reload mode) | `(2 x CPU Cores) + 1` (e.g., 4-8 workers) |
| **Max Memory per Worker** | 512 MB | 1.5 GB (accommodates tree ensembles + SHAP cache) |
| **Request Timeout** | Infinite | 30 seconds (15s hard timeout on Gemini calls) |
| **Database Pool Size** | Default (5 connections) | 20 connections + 10 max overflow |
| **Rate Limiter Cap** | 100 req/min/IP | 60 req/min for auth, 120 req/min for predict |

---

## 5. Structured Logging & Observability

- **Request ID Correlation**: The middleware assigns a unique UUID4 (`X-Request-ID`) to every incoming HTTP request. This ID is propagated across all log entries, database audit trails, and client response headers.
- **Latency Tracking**: Every response header contains `X-Response-Time` (e.g., `12.45ms`) for upstream APM aggregation.
- **Privacy Enforcement**: PII, passwords, JWT tokens, and raw Gemini secrets are scrubbed prior to log serialization.

---

## 6. Backup & Disaster Recovery

### 6.1 Database Backup
Automated daily snapshots of the PostgreSQL database:
```bash
# Export compressed PostgreSQL database dump
pg_dump -U intellitwin_user -d intellitwin -F c -b -v -f /backups/intellitwin_$(date +%Y%m%d_%H%M%S).dump

# Restore from dump in case of data loss
pg_restore -U intellitwin_user -d intellitwin -v -c /backups/intellitwin_target.dump
```

### 6.2 ML Artifact Backup
Model `.joblib` files are immutable once registered. They should be replicated to version-controlled object storage (e.g., AWS S3, Cloudflare R2, or Google Cloud Storage) with versioning enabled:
```bash
aws s3 sync ml-engine/models/ s3://intellitwin-model-registry/v2.1.0/
```

---

## 7. Incident Handling & Alerting Playbook

### Alert: Elevated False Positive Rate (> 5%)
1. Review `/api/dashboard/stats` and filter recent alerts by attack preset.
2. Inspect SHAP feature importance in `/detection` for anomalous feature pushes.
3. If input distribution shifted (covariate shift), switch primary model from XGBoost to Random Forest via `DEFAULT_MODEL_NAME=random_forest`.

### Alert: Gemini API Quota Exhaustion or Downstream Timeout
- The backend automatically enters **Autonomous Fallback Mode** (`is_fallback=true`).
- Reports continue to be generated using internal deterministic rule heuristics and SHAP feature attributions with zero downtime.
- Log error `Gemini API quota exceeded; serving fallback report` without raising 500 internal server errors.
