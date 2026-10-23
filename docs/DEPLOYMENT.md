# IntelliTwin AI — Production Deployment Guide

This guide details the deployment architecture and step-by-step procedures for deploying **IntelliTwin AI** across modern cloud infrastructure:
- **Frontend**: Vercel (Edge CDN + Next.js App Router)
- **Backend API & ML Serving**: Render, Railway, AWS ECS, or DigitalOcean App Platform
- **Database**: Managed PostgreSQL (Supabase, Neon, AWS RDS, or Render Postgres)

---

## 1. Cloud Architecture Overview

```
                        [End Users / SOC Analysts]
                                    │
                                    ▼
                      [Vercel Global Edge Network]
                     (Next.js 16 Static + Dynamic)
                                    │
                       API Requests │ HTTPS / JWT
                                    ▼
                [Cloud Application Layer: Render / AWS]
                      FastAPI + Uvicorn Worker Pool
                     ├── ML Inference Engine (Cached)
                     └── Gemini GenAI SOC Copilot
                                    │
                   ┌────────────────┴────────────────┐
                   ▼                                 ▼
         [Managed PostgreSQL]             [Google Cloud Gemini]
         (Neon / Supabase / RDS)          (Gemini 1.5 Pro/Flash)
```

---

## 2. Environment Variables & Secret Configuration

Create production environment variables in your hosting provider's dashboard. **Never commit production `.env` files to Git.**

### 2.1 Backend Environment Variables

| Variable | Required | Example / Format | Purpose |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | **Yes** | `postgresql://user:pass@ep-xyz.neon.tech/intellitwin?sslmode=require` | Persistent PostgreSQL connection URI |
| `SECRET_KEY` | **Yes** | `d4f8e9...` (64 hex characters) | Cryptographic signature key for JWT tokens |
| `ENVIRONMENT` | **Yes** | `production` | Enables strict production guards |
| `CORS_ORIGINS` | **Yes** | `https://intellitwin.vercel.app,https://soc.company.com` | Comma-delimited list of allowed web origins |
| `ADMIN_INITIAL_PASSWORD`| **Yes** | Strong pass (16+ chars) | Bootstrap password for the initial `admin@intellitwin.ai` account |
| `GEMINI_API_KEY` | Optional | `AIzaSy...` | Enables LLM incident triage reports (fallback if omitted) |
| `GEMINI_MODEL` | Optional | `gemini-1.5-flash` | Gemini model variant |
| `MODEL_DIR` | Optional | `/app/ml-engine/models` | Absolute path to serialized `.joblib` model directory |

### 2.2 Frontend Environment Variables

| Variable | Required | Example / Format | Purpose |
| :--- | :--- | :--- | :--- |
| `NEXT_PUBLIC_API_URL` | **Yes** | `https://api.intellitwin.yourdomain.com/api` | Public backend API URL for client-side fetching |
| `BACKEND_INTERNAL_URL`| Optional | `http://backend:8000` | Internal network URL for Docker/Kubernetes reverse rewrites |
| `NODE_ENV` | **Yes** | `production` | Enforces optimized React build |

---

## 3. Database Setup & Migration

### 3.1 Provisioning Managed PostgreSQL
Provision a database on Supabase, Neon, AWS RDS, or Render:
1. Ensure SSL mode is enabled (`sslmode=require`).
2. Verify connection string format starts with `postgresql://` (or `postgres://`).

### 3.2 Automated Schema Creation & Bootstrap
Upon service startup, FastAPI executes `init_db()` in `backend/app/core/database.py`:
- Creates all required tables: `users`, `security_events`, `ml_models`, `audit_logs`, `incident_reports`.
- Instantiates composite performance indexes:
  - `idx_events_risk_timestamp` on `security_events (risk_score, timestamp)`
  - `idx_events_ip_lookup` on `security_events (source_ip, destination_ip)`
  - `idx_reports_created` on `incident_reports (created_at)`
- Seeds the root `ADMIN` and `SECURITY_ANALYST` accounts securely using bcrypt hashing with individual cryptographic salts.
- **Security Guard**: In `production`, if `ADMIN_INITIAL_PASSWORD` is not explicitly set in the environment, the server aborts initialization with a critical configuration exception rather than defaulting to weak credentials.

---

## 4. Backend Deployment (Render / Railway / AWS)

### Option A: Render (Web Service)
1. Link your Git repository to Render.
2. Choose **Docker** as the Environment:
   - **Dockerfile Path**: `backend/Dockerfile`
   - **Docker Context**: Root directory (`.`) — *critical so `ml-engine/models/` is copied into the container*.
3. Add the Environment Variables listed in Section 2.1.
4. Set Health Check Path to `/health`.
5. Deploy.

### Option B: Railway
1. Create a new Railway project and connect the repository.
2. Select root directory as build context and specify `backend/Dockerfile`.
3. Link the Railway PostgreSQL database plugin; Railway automatically populates `DATABASE_URL`.
4. Configure `SECRET_KEY`, `CORS_ORIGINS`, and `ADMIN_INITIAL_PASSWORD`.

### Option C: AWS Elastic Container Service (ECS Fargate)
1. Build and push image to AWS ECR:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
   docker build -t intellitwin-backend -f backend/Dockerfile .
   docker tag intellitwin-backend:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/intellitwin-backend:latest
   docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/intellitwin-backend:latest
   ```
2. Configure Fargate task definition with 1 vCPU and 2 GB memory.
3. Attach Application Load Balancer targeting port 8000 with health check on `/health`.

---

## 5. Frontend Deployment (Vercel)

1. Import the Git repository into Vercel.
2. Set **Root Directory** to `frontend`.
3. Vercel automatically detects Next.js:
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
   - **Install Command**: `npm install`
4. Add Environment Variable:
   - `NEXT_PUBLIC_API_URL`: Your deployed backend API URL (e.g., `https://api.intellitwin.onrender.com/api`).
5. Click **Deploy**. Vercel will build and distribute the app across its global Edge network with full static prerendering.

---

## 6. Model Artifact Persistence on Ephemeral Hosting

Hosting providers such as Render and Heroku possess ephemeral filesystems. In IntelliTwin AI:
1. **Container Packing**: Model weights (`.joblib` files) reside in `ml-engine/models/` and are baked directly into the Docker image during the build stage (`COPY ml-engine/models/ /app/ml-engine/models/`).
2. **Version Pinning**: This guarantees that every deployment runs with the exact audited model artifacts without depending on network downloads or external storage mount failures.
3. **Enterprise S3 Strategy (For Continuous Re-training)**:
   For teams training models dynamically in production, update `backend/app/services/ml_service.py` to fetch artifacts from AWS S3 upon boot:
   ```bash
   aws s3 sync s3://company-ml-bucket/intellitwin/latest /app/ml-engine/models/
   ```

---

## 7. Verification & Post-Deployment Checklist

After deployment, perform these verification steps:
1. **Verify Liveness**: `curl -f https://<backend-url>/health` (Expect `{"status": "ok"}`).
2. **Verify Readiness**: `curl -f https://<backend-url>/ready` (Expect `{"status": "ready", "database": "connected", "model": "loaded"}`).
3. **Verify CORS**: Check that the frontend domain is accepted and can query `/api/models/metrics`.
4. **Verify Authentication**: Log in to the frontend with the configured admin credentials.
5. **Verify Anomaly Detection**: Submit a synthetic attack vector on `/detection` and confirm non-zero SHAP attributions render.
6. **Verify GenAI**: Click "Generate Gemini AI Report" and verify an incident triage report generates without error.
