# IntelliTwin AI: Enterprise Cybersecurity Anomaly Detection & GenAI Platform

**M.Sc. IT Final Year Capstone & Professional Cybersecurity Portfolio Project**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2016-black.svg?style=flat&logo=next.js)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat&logo=python)](https://www.python.org)
[![Pytest](https://img.shields.io/badge/Tests-27%20Passed-brightgreen.svg?style=flat&logo=pytest)](https://pytest.org)
[![Dataset](https://img.shields.io/badge/Dataset-UNSW--NB15%20Verified-blue.svg)](https://research.unsw.edu.au/projects/unsw-nb15-dataset)

---

## 1. Executive Summary

**IntelliTwin AI** is an enterprise-grade, full-stack cybersecurity intrusion detection and automated Security Operations Center (SOC) triage platform. It unifies:

1. **Real Machine Learning Inference**: Multi-model detection (XGBoost Champion, Random Forest, and Isolation Forest) trained and evaluated on an authentic stratified partition of **25,000 network flows** from the benchmark **UNSW-NB15** dataset (ACCS).
2. **Explainable AI (XAI)**: `shap.TreeExplainer` integration computing mathematical Shapley values ($\phi$) that quantify the marginal contribution of packet attributes (e.g., packet rate, byte ratios, and connection windows).
3. **Generative AI SOC Copilot**: Google Gemini GenAI engine that transforms telemetry and SHAP vectors into structured Tier-3 SOC incident reports mapped to the MITRE ATT&CK framework with concrete remediation playbooks.
4. **Autonomous Zero-Crash Fallback**: Resilient fallback engine ensuring continuous incident triage even when external LLM APIs are offline or rate-limited.
5. **Zero-Fabrication Policy**: All metrics (Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix) are dynamically served from authentic held-out test evaluation outputs (`model_metrics.json`).

---

## 2. Empirical Model Performance (Authentic UNSW-NB15 Benchmark)

All metrics are loaded dynamically from `ml-engine/models/model_metrics.json` evaluated across **5,000 held-out test records** (with 5-fold cross-validation on 20,000 training records):

| Model Architecture | 5-Fold CV Acc | Test Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Primary Use-Case |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **XGBoost (Champion)** | **94.95%** | **94.48%** | **0.9430** | **0.9780** | **0.9602** | **0.9901** | **0.9954** | Ultra-high recall volumetric & signature detection |
| **Random Forest** | **94.25%** | **94.02%** | **0.9686** | **0.9427** | **0.9555** | **0.9903** | **0.9954** | High-precision multi-variable ensemble voting |
| **Isolation Forest** | N/A | **59.78%** | **0.9168** | **0.4499** | **0.6036** | **0.8323** | **0.8912** | Unsupervised baseline outlier detection |

> **Note on Scientific Integrity**: Earlier prototypes reported an artificial 100.0% accuracy caused by a synthetic data fallback in an older data downloader. IntelliTwin AI forensically resolved this by ingesting authentic UNSW-NB15 benchmark files, producing the authentic 94.48% state-of-the-art result. See [docs/ML_EVALUATION.md](file:///C:/Users/imdee/.gemini/antigravity-ide/scratch/IntelliTwin-AI/docs/ML_EVALUATION.md).

---

## 3. System Architecture

```
+---------------------------------------------------------------------------------------------------------+
|                                    INTELLITWIN AI PLATFORM ARCHITECTURE                                 |
+---------------------------------------------------------------------------------------------------------+
                                                     |
                                                     v
                                      +-------------------------------+
                                      |    Next.js 16 App Router      |
                                      | (TypeScript + Tailwind CSS    |
                                      |  + Framer Motion + Recharts)  |
                                      +---------------+---------------+
                                                      |
                                                      | HTTPS / REST / JWT
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                        FASTAPI BACKEND GATEWAY                                          |
|                                                                                                         |
|  +--------------------+  +---------------------+  +--------------------+  +--------------------------+  |
|  |  Direct Bcrypt     |  | Sliding Token Bucket|  | Pydantic v2 Models |  |   Audit Logging Engine   |  |
|  |  & JWT RBAC        |  | Rate Limiter        |  | (Strict Validation |  |  (Append-Only Non-       |  |
|  | (ADMIN, ANALYST)   |  | (Auth, Predict, Rep)|  |  & Boundary Guards)|  |   Repudiation Trail)     |  |
|  +--------------------+  +---------------------+  +--------------------+  +--------------------------+  |
|                                                     |                                                   |
|                      +------------------------------+-------------------------------+                   |
|                      |                                                              |                   |
|                      v                                                              v                   |
|         +-------------------------+                                    +--------------------------+     |
|         |   ML Inference Engine   |                                    |   GenAI SOC Assistant    |     |
|         |  - XGBoost (Champion)   |                                    |  - Google Gemini API     |     |
|         |  - Random Forest        |                                    |  - MITRE ATT&CK Mapping  |     |
|         |  - Isolation Forest     |                                    |  - Prompt Injection Guard|     |
|         |  - SHAP TreeExplainer   |                                    |  - Autonomous Fallback   |     |
|         +------------+------------+                                    +-------------+------------+     |
|                      |                                                               |                  |
|                      +---------------------------------------------------------------+                  |
|                                                     |                                                   |
+-----------------------------------------------------+---------------------------------------------------+
                                                      |
                                                      v
+---------------------------------------------------------------------------------------------------------+
|                                        DATA & PERSISTENCE LAYER                                         |
|                                                                                                         |
|     PostgreSQL 16 (Production) / SQLite (Zero-Config Development) with Composite DB Indexes             |
+---------------------------------------------------------------------------------------------------------+
```

---

## 4. Local Setup & Execution Guide

### Quick Start (Local Development)

#### 1. Backend Service
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend (Port 8000)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- API Documentation (Swagger): `http://127.0.0.1:8000/docs`
- Health Probe: `http://127.0.0.1:8000/health`
- Readiness Probe: `http://127.0.0.1:8000/ready`

#### 2. Frontend Application
```bash
# Open a new terminal in the frontend directory
cd frontend

# Install dependencies
npm install

# Start Next.js App Router (Port 3000)
npm run dev
```
- Web Application: `http://localhost:3000`

---

## 5. Running the Automated Test Suite

```bash
# In the repository root
python -m pytest tests/ -v
```
All **27 test cases pass** with zero failures across ML pipeline and backend API suites.
