# IntelliTwin AI — Technical System Architecture

This document provides the definitive architectural blueprint of the **IntelliTwin AI** cybersecurity anomaly detection and Generative AI incident triage platform.

---

## 1. System Context & Overview

IntelliTwin AI is an end-to-end cyber threat intelligence platform that unifies real-time machine learning anomaly detection, game-theoretic Explainable AI (SHAP), and Large Language Model (LLM) incident response synthesis.

```mermaid
graph TD
    User([SOC Analyst / Admin]) -->|HTTPS / UI| Frontend[Next.js 16 Web Dashboard]
    NetworkSensor([Network Tap / Zeek Sensor]) -->|Flow Telemetry| APIGateway[FastAPI Backend Gateway]
    Frontend -->|REST API / JWT| APIGateway

    subgraph Backend Core
        APIGateway --> SecurityMiddleware[Auth, RBAC & Rate Limiting]
        SecurityMiddleware --> Controller[API Route Handlers]
        Controller --> MLService[ML Inference Service]
        Controller --> SHAPService[SHAP TreeExplainer Service]
        Controller --> GeminiService[Google Gemini SOC Copilot]
    end

    subgraph Storage & Models
        Controller --> DB[(PostgreSQL / SQLite Database)]
        MLService --> ModelRegistry[(In-Memory Joblib Model Cache)]
        SHAPService --> ModelRegistry
    end

    subgraph External Cloud Services
        GeminiService -->|TLS / JSON| GoogleGemini[Google Gemini 1.5 Pro/Flash]
    end
```

---

## 2. Component Deconstruction

### 2.1 Web Presentation Tier (`frontend/`)
- **Framework**: Next.js 16.4 (App Router) using React 19 and TypeScript 5.
- **Styling & UI**: Tailwind CSS v4 with custom dark cybersecurity theme (graphite `#0d1117`, cyan `#06b6d4`, emerald `#10b981`, rose `#f43f5e`).
- **Data Visualization**: Recharts for dynamic ROC curves, precision-recall curves, and risk gauge dials.
- **Micro-Interactions**: Framer Motion for smooth tab transitions and live radar scan animations.
- **Key Views**:
  - `/dashboard`: High-level operational command center showing live threat distribution and active alerts.
  - `/detection`: Interactive packet injection simulator with real-time SHAP waterfall charts.
  - `/models`: Dynamic model registry, comparative cross-validation metrics, and ROC curves.
  - `/reports`: Archive of verified GenAI SOC incident reports with MITRE ATT&CK mappings.
  - `/settings`: Infrastructure health monitor, runtime logs, and token-gated live audit trail.

### 2.2 API & Business Logic Tier (`backend/`)
- **Framework**: FastAPI on Python 3.12 with asynchronous ASGI event loop.
- **Concurrency Model**: CPU-bound inference (`model.predict_proba`) is offloaded to threadpools using `asyncio.to_thread` to ensure zero blocking of the async event loop.
- **Security Middleware**: Direct bcrypt password hashing, RFC 7519 JWT validation, and sliding window IP rate limiting.
- **Observability**: Structured JSON logging, unique `X-Request-ID` correlation propagation, and `X-Response-Time` header calculation.

### 2.3 Machine Learning & Explainability Engine (`ml-engine/`)
- **Dataset**: Authentic UNSW-NB15 benchmark flow dataset (25,000 stratified flow partition).
- **Preprocessing Pipeline**: Scikit-learn `ColumnTransformer` with `RobustScaler` for numerical outliers and `OrdinalEncoder` for categorical protocols and states, fitted exclusively on training splits.
- **Ensemble Classifiers**:
  - **XGBoost Classifier** (Champion, 94.48% test accuracy, 0.9901 ROC-AUC)
  - **Random Forest** (94.02% test accuracy, 0.9903 ROC-AUC)
  - **Isolation Forest** (Unsupervised baseline, 59.78% test accuracy, 0.8323 ROC-AUC)
- **Explainability (XAI)**: `shap.TreeExplainer` providing local Shapley feature attributions ($\phi$) for every inference.

### 2.4 Generative AI SOC Copilot (`backend/app/services/gemini_service.py`)
- **Engine**: Google Gemini 1.5 Flash/Pro with Pydantic v2 structured output validation.
- **Prompt Injection Defense**: Multi-stage text filtering and structural isolation of raw telemetry.
- **Autonomous Fallback**: Graceful degradation to deterministic threat correlation if API quotas are exhausted or network access is restricted.

---

## 3. Data Flow Architecture

### 3.1 Real-Time Anomaly Detection & SHAP Pipeline
```mermaid
sequenceDiagram
    autonumber
    actor Analyst as SOC Analyst
    participant Frontend as Next.js UI
    participant Backend as FastAPI Router
    participant Preprocessor as ColumnTransformer
    participant Model as XGBoost Champion
    participant SHAP as TreeExplainer
    participant DB as SecurityEvent Table

    Analyst->>Frontend: Submit Packet Telemetry (IP, Port, Bytes, Rate)
    Frontend->>Backend: POST /api/detection/predict (Bearer JWT)
    Backend->>Backend: Validate Pydantic Schema & Rate Limit
    Backend->>Preprocessor: Transform(Feature Vector)
    Preprocessor-->>Backend: Transformed Numerical Matrix
    Backend->>Model: predict_proba(Matrix)
    Model-->>Backend: P(Normal), P(Anomaly)
    Backend->>SHAP: shap_values(Matrix)
    SHAP-->>Backend: Marginal Feature Contributions
    Backend->>Backend: Compute Calibrated Risk Score (0-100) & Severity
    Backend->>DB: Persist SecurityEvent record
    Backend-->>Frontend: JSON (Label, Risk Score, Probabilities, SHAP Array)
    Frontend-->>Analyst: Render Alert Badge & Waterfall Attribution Chart
```

### 3.2 GenAI Tier-3 Incident Report Synthesis
```mermaid
sequenceDiagram
    autonumber
    actor Analyst as SOC Analyst
    participant Frontend as Next.js UI
    participant Backend as FastAPI Router
    participant Gemini as Google Gemini API
    participant DB as IncidentReport Table

    Analyst->>Frontend: Request AI Triage Report for Event #1042
    Frontend->>Backend: POST /api/reports/generate (event_id)
    Backend->>Backend: Fetch Event Telemetry & Verify Ownership
    Backend->>Backend: Sanitize Prompt & Structure Prompt JSON
    alt Gemini API Configured & Responsive
        Backend->>Gemini: Generate Content (15s Timeout)
        Gemini-->>Backend: Structured Triage JSON (MITRE, Root Cause, Playbook)
    else Timeout / Quota Limit / Missing Key
        Backend->>Backend: Trigger Autonomous SOC Fallback Engine
    end
    Backend->>DB: Save IncidentReport with Audit Metadata
    Backend-->>Frontend: JSON (Executive Summary, MITRE ATT&CK, Remediation)
    Frontend-->>Analyst: Render Structured SOC Incident Report
```

---

## 4. Database Schema (Entity-Relationship)

```mermaid
erDiagram
    USERS ||--o{ SECURITY_EVENTS : analyzes
    USERS ||--o{ AUDIT_LOGS : performs
    SECURITY_EVENTS ||--o| INCIDENT_REPORTS : triggers

    USERS {
        int id PK
        string email UK
        string hashed_password
        string role "ADMIN | SECURITY_ANALYST | USER"
        datetime created_at
    }

    SECURITY_EVENTS {
        int id PK
        string source_ip
        string destination_ip
        int destination_port
        string protocol
        float risk_score
        string severity "LOW | MEDIUM | HIGH | CRITICAL"
        string predicted_class "NORMAL | ANOMALY"
        json raw_features
        json shap_values
        datetime timestamp
    }

    INCIDENT_REPORTS {
        int id PK
        int event_id FK
        string title
        string executive_summary
        string root_cause
        json mitre_attack
        json remediation_steps
        string generated_by "Gemini 1.5 Flash | Autonomous Fallback"
        boolean is_fallback
        datetime created_at
    }

    AUDIT_LOGS {
        int id PK
        int user_id FK
        string action
        string resource
        string ip_address
        string request_id
        datetime timestamp
    }

    ML_MODELS {
        int id PK
        string name UK
        string version
        float accuracy
        float precision
        float recall
        float f1_score
        float roc_auc
        json metrics_json
        datetime registered_at
    }
```

---

## 5. API Interface Contracts

| Method | Endpoint | Auth | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | Public | Authenticates credentials and returns JWT access token |
| `POST` | `/api/auth/register` | Public | Self-registration for analyst accounts |
| `GET` | `/api/auth/me` | Bearer | Returns active authenticated user identity and role |
| `POST` | `/api/detection/predict` | Bearer | Evaluates network flow, outputs calibrated risk and SHAP |
| `GET` | `/api/detection/presets` | Public | Returns benchmark attack and normal flow presets |
| `GET` | `/api/models/metrics` | Public | Dynamic performance metrics, confusion matrices, and ROC points |
| `GET` | `/api/dashboard/stats` | Public | Aggregated event counts, risk distribution, and attack ratios |
| `POST` | `/api/reports/generate` | Bearer | Synthesizes Gemini GenAI Tier-3 SOC incident report |
| `GET` | `/api/reports/` | Bearer | Retrieves past generated incident triage reports |
| `GET` | `/api/admin/audit-logs` | Admin | Fetches immutable system audit log trail |
| `GET` | `/api/admin/system-health` | Admin | Comprehensive subsystem diagnostics and memory footprint |
| `GET` | `/health` | Public | Operational liveness probe |
| `GET` | `/ready` | Public | Operational readiness probe (DB + Model RAM check) |
