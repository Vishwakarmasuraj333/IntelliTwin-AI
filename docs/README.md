# IntelliTwin AI: Enterprise Cybersecurity Anomaly Detection & GenAI Platform
**M.Sc. IT Final Year Capstone & Professional Cybersecurity Portfolio Project**

---

## 1. Project Overview

**IntelliTwin AI** is a production-grade, full-stack cybersecurity intrusion detection and automated Security Operations Center (SOC) triage platform. It unifies:
1. **Real Machine Learning Inference**: Multi-model detection (Random Forest, XGBoost, and Isolation Forest) trained and evaluated on 20,000 real-world network traffic records from the benchmark **UNSW-NB15** cybersecurity dataset.
2. **Explainable AI (XAI)**: SHAP (SHapley Additive exPlanations) TreeExplainer integration providing granular local feature attributions that explain *why* any packet signature was classified as an anomaly.
3. **Generative AI SOC Copilot**: Google Gemini Generative AI engine that transforms complex raw telemetry and SHAP vectors into human-readable Tier-3 SOC incident investigation reports, complete with MITRE ATT&CK technique IDs and actionable firewall mitigation playbooks.
4. **Zero-Fabrication Policy**: All metrics (Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix, and ROC Curve points) are dynamically calculated from the held-out test split and served dynamically from `model_metrics.json`.

---

## 2. System Architecture

```
+---------------------------------------------------------------------------------------------------------+
|                                    INTELLITWIN AI PLATFORM ARCHITECTURE                                 |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
                                      +-------------------------------+
                                      |    Next.js 14 App Router      |
                                      | (TypeScript + Tailwind CSS    |
                                      |  + Framer Motion + Recharts)  |
                                      +---------------+---------------+
                                                      |
                                                      | HTTPS / REST / JSON
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                        FASTAPI BACKEND GATEWAY                                          |
|                                                                                                         |
|  +--------------------+  +---------------------+  +--------------------+  +--------------------------+  |
|  |  JWT Auth & RBAC   |  |   Rate Limiting     |  | Pydantic Schemas   |  |   Audit Logging Engine   |  |
|  | (ADMIN, ANALYST,   |  |   & IP Throttling   |  | (Strict Network    |  |  (Immutable Action Trail |  |
|  |  USER)             |  |                     |  |  Event Validation) |  |   with User & Timestamp) |  |
|  +--------------------+  +---------------------+  +--------------------+  +--------------------------+  |
|                                                     |                                                   |
|                      +------------------------------+-------------------------------+                   |
|                      |                                                              |                   |
|                      v                                                              v                   |
|         +-------------------------+                                    +--------------------------+     |
|         |    ML Inference Engine  |                                    |   GenAI SOC Assistant    |     |
|         |  - XGBoost Classifier   |                                    |  - Google Gemini API     |     |
|         |  - Random Forest        |                                    |  - MITRE ATT&CK Mapping  |     |
|         |  - Isolation Forest     |                                    |  - Incident Triage Rep.  |     |
|         |  - SHAP Explainer (XAI) |                                    |  - Response Playbooks    |     |
|         +------------+------------+                                    +-------------+------------+     |
|                      |                                                               |                  |
|                      | (Outputs: Prediction + Feature Contributions)                 |                  |
|                      +---------------------------------------------------------------+                  |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
                                                      |
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                        DATA & PERSISTENCE LAYER                                         |
|                                                                                                         |
|  +---------------------+  +------------------------+  +--------------------+  +----------------------+  |
|  |     Users Table     |  |  SecurityEvents Table  |  |   MLModels Table   |  |   AuditLogs Table    |  |
|  | (Auth, Roles, Salt) |  | (Raw Packet, Risk, XAI)|  | (Versions, Real    |  | (Security Operations |  |
|  |                     |  |                        |  |  Metrics JSON)     |  |  Compliance Log)     |  |
|  +---------------------+  +------------------------+  +--------------------+  +----------------------+  |
|                                                     |                                                   |
|                        PostgreSQL / Enterprise SQLite (Zero-Crash Fallback)                             |
+---------------------------------------------------------------------------------------------------------+
```

---

## 3. Monorepo Structure

```
IntelliTwin-AI/
├── frontend/                     # Next.js 14 App Router (React 19, TypeScript, Tailwind)
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx        # Command Center root layout & global cyber theme
│   │   │   ├── page.tsx          # High-converting platform overview & hero showcase
│   │   │   ├── dashboard/        # Live SOC Telemetry Command Center & KPIs
│   │   │   ├── detection/        # ML Network Simulator & SHAP Waterfall Workspace
│   │   │   ├── models/           # Model Registry, Dynamic Metrics & ROC Curves
│   │   │   ├── reports/          # GenAI SOC Incident Investigation Archive
│   │   │   └── settings/         # Subsystem Health, Gemini Config & Audit Trails
│   │   ├── components/           # Modular Badges, Radar pulses, Modals, SHAP charts
│   │   └── lib/                  # API client, TypeScript definitions
│   └── package.json
│
├── backend/                      # Python FastAPI REST Service
│   ├── app/
│   │   ├── api/routes/           # Auth, Detection, Gemini, Models, Dashboard, Admin
│   │   ├── core/                 # Config, Database sessions, Direct Bcrypt Security
│   │   ├── models/               # SQLAlchemy ORM (Users, Events, Models, Audit, Reports)
│   │   ├── schemas/              # Pydantic v2 strict boundary models
│   │   └── services/             # ML inference, SHAP TreeExplainer, Gemini AI client
│   ├── main.py                   # FastAPI Application Entrypoint
│   └── requirements.txt
│
├── ml-engine/                    # Machine Learning Pipeline
│   ├── dataset/                  # UNSW-NB15 Data Ingestion & benchmark splits
│   ├── preprocessing/            # LabelEncoders, RobustScaler, Feature pipeline
│   ├── training/                 # Multi-model training routines (RF, XGBoost, IF)
│   ├── evaluation/               # Held-out test set evaluation & report generator
│   └── models/                   # Serialized .joblib artifacts & model_metrics.json
│
├── tests/                        # Automated Pytest Suite (17 tests passing)
│   ├── test_ml_pipeline.py       # Validates data shapes, metrics, joblib & SHAP
│   └── test_backend_api.py       # Validates endpoints, JWT auth, inference & GenAI
│
└── docs/
    ├── README.md                 # Production architecture & operational manual
    └── PROJECT_REPORT.md         # Full Academic M.Sc. IT Final Year Capstone Report
```

---

## 4. Empirical Model Performance (UNSW-NB15 Benchmark)

All metrics are loaded dynamically from `ml-engine/models/model_metrics.json` computed across 4,000 held-out test network flow records:

| Model Architecture | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Primary Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Random Forest (Champion)** | **100.0%** | **1.0000** | **1.0000** | **1.0000** | **1.0000** | High-precision multi-variable classification |
| **XGBoost Classifier** | **99.98%** | **0.9995** | **1.0000** | **0.9997** | **1.0000** | Ultra-fast gradient boosting inference |
| **Isolation Forest** | **88.50%** | **0.8711** | **0.8824** | **0.8767** | **0.9481** | Unsupervised zero-day outlier baseline |

---

## 5. Getting Started & Installation

### Prerequisites
- Python 3.11 or 3.12
- Node.js 18+ or 22+ & npm

### Backend & ML Engine Setup
```bash
cd backend
python -m pip install -r requirements.txt

# Run the backend dev server (Port 8000)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install

# Run the Next.js App Router dev server (Port 3000)
npm run dev
```

### Executing the Automated Pytest Suite
```bash
# In the repository root
python -m pytest tests/ -v
```

---

## 6. Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL or SQLite database URI | `sqlite:///backend/intellitwin.db` |
| `SECRET_KEY` | JWT signing secret key | `intellitwin_ultra_secure_jwt_secret_key_2026_soc_ai` |
| `GEMINI_API_KEY` | Google Gemini API key for live LLM reports | Optional (Autonomous SOC Fallback if empty) |
| `GEMINI_MODEL` | Gemini model identifier | `gemini-1.5-flash` |
| `NEXT_PUBLIC_API_URL`| Frontend API endpoint | `http://127.0.0.1:8000/api` |

---

## 7. Default Credentials (Seeded Automatically)

- **Admin Account**: `admin@intellitwin.ai` / `Admin@123456` (Role: `ADMIN`)
- **Analyst Account**: `analyst@intellitwin.ai` / `Analyst@123456` (Role: `SECURITY_ANALYST`)
