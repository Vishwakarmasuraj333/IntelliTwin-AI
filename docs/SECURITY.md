# IntelliTwin AI — Application Security & Hardening Architecture

This document articulates the defense-in-depth security model implemented across the **IntelliTwin AI** cybersecurity anomaly detection and GenAI SOC copilot platform.

---

## 1. Security Philosophy & Threat Model

As a security-centric platform designed for enterprise Security Operations Centers (SOCs), IntelliTwin AI enforces zero-trust principles across all tiers. The system assumes:
1. **Network traffic telemetry is untrusted**: Packet attributes may contain adversarial perturbations or malformed boundary values.
2. **LLM inputs are adversarial vectors**: External telemetry or user-submitted notes could attempt prompt injection or data exfiltration.
3. **Clients are untrusted**: All authorizations, rate limits, and data ownership validations are enforced server-side.

---

## 2. Authentication & Session Security

### 2.1 Cryptographic Password Hashing
- IntelliTwin AI uses **direct `bcrypt` hashing** (`bcrypt.hashpw(password, bcrypt.gensalt(rounds=12))`).
- Every password hash is generated with an individual cryptographically secure 128-bit random salt and a work factor of 12 rounds, providing robust defense against GPU rainbow table attacks.
- Legacy or vulnerable schemes (MD5, SHA1, plaintext) are prohibited.

### 2.2 JSON Web Token (JWT) Lifecycle
- Authentication issues RFC 7519 compliant JSON Web Tokens signed with the HMAC-SHA256 (`HS256`) algorithm.
- Token payload incorporates:
  - `sub`: User email address
  - `role`: Authorization scope (`ADMIN`, `SECURITY_ANALYST`, `USER`)
  - `exp`: Strictly bounded 24-hour expiration timestamp
  - `iat`: Issuance timestamp
- Secret keys are retrieved exclusively from environment variables (`SECRET_KEY`). If omitted in production, the application refuses to start.

### 2.3 Secure Admin Bootstrapping
- In development, default credentials (`admin@intellitwin.ai` / `Admin@123456`) facilitate local testing with explicit warnings.
- In `production` (`ENVIRONMENT=production`), the database initializer mandates the presence of `ADMIN_INITIAL_PASSWORD`. The application will crash-exit if weak default credentials are used in production.

---

## 3. Role-Based Access Control (RBAC)

FastAPI dependencies enforce least-privilege role boundaries on every API route:

| Role | Permissions | Accessible Endpoints |
| :--- | :--- | :--- |
| **`USER`** | Read-only access to models and public metrics. | `GET /api/models/*`, `GET /api/dashboard/stats` |
| **`SECURITY_ANALYST`** | Execute real-time inferences, submit telemetry, trigger SHAP explainability, and generate GenAI incident reports. | All `USER` permissions + `POST /api/detection/predict`, `POST /api/reports/generate`, `GET /api/reports/*` |
| **`ADMIN`** | Full system control: view audit logs, trigger model retraining, inspect database connection pools, manage users. | All platform routes including `GET /api/admin/audit-logs`, `GET /api/admin/system-health`, `POST /api/admin/retrain` |

Route enforcement example:
```python
@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    current_user: User = Depends(require_role("ADMIN")),
    db: Session = Depends(get_db)
):
    ...
```

---

## 4. Input Sanitization & Defensive Validation

### 4.1 Strict Schema Enforcement (Pydantic v2)
Every inbound payload is validated through strongly typed Pydantic models with explicit bounds:
- `dur`: Float $\ge 0.0$
- `sbytes`, `dbytes`: Integer $\ge 0$
- `rate`: Float $\ge 0.0$
- Network protocol and state are validated against enumerated whitelists.
- Extra unknown fields are safely handled; malformed or infinite (`inf`, `NaN`) numeric values trigger immediate `422 Unprocessable Entity` responses prior to preprocessing.

### 4.2 SQL Injection Prevention
- All database interactions utilize the **SQLAlchemy 2.0 ORM** with parameterized queries and explicit type binding.
- Raw string concatenation into SQL statements is prohibited across all routes and services.

---

## 5. Denial-of-Service Defense & Rate Limiting

An in-memory sliding token bucket rate limiter (`backend/app/core/rate_limit.py`) throttles incoming traffic per client IP address:
- **Authentication Routes (`/api/auth/*`)**: 60 requests / minute (mitigates brute-force credential stuffing).
- **Inference Routes (`/api/detection/predict`)**: 120 requests / minute (prevents resource exhaustion of tree ensembles).
- **GenAI Report Generation (`/api/reports/generate`)**: 20 requests / minute (protects external LLM quota and budget).
- When thresholds are exceeded, the server returns `HTTP 429 Too Many Requests` with a descriptive retry-after header.

---

## 6. Generative AI & Prompt Injection Hardening

The Google Gemini integration (`backend/app/services/gemini_service.py`) operates as a secure copilot:

### 6.1 Input Sanitization
User-supplied event descriptions and raw packet telemetry are scrubbed before prompt construction:
```python
def sanitize_prompt_input(text: str) -> str:
    # Strips delimiter breaks and injection instructions
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"(ignore\s+all\s+previous\s+instructions|system\s+prompt|disregard|you\s+are\s+now)", "[FILTERED]", text, flags=re.IGNORECASE)
    return text[:2000]
```

### 6.2 Structural Isolation
Telemetry data and SHAP feature attributions are formatted as strictly quoted JSON data blocks within the prompt, explicitly separated from system instructions.

### 6.3 Bounded Retries & Hard Timeouts
- Gemini API calls are wrapped in an explicit **15-second timeout**.
- Downstream failures or rate limits fail gracefully into the internal **Autonomous SOC Fallback Engine**, ensuring the platform never crashes or leaks API keys.

---

## 7. Audit Logging & Non-Repudiation

- Critical administrative and analyst actions (logins, inferences, report generation, role updates) are recorded in an append-only `audit_logs` database table.
- Each entry records:
  - `user_id` & `user_email`
  - `action` & `resource`
  - `ip_address`
  - `request_id` (UUID4 correlation token)
  - `timestamp` (UTC)
- The audit log endpoint is strictly restricted to the `ADMIN` role. Deletion and modification of audit entries are not exposed via any API endpoint.

---

## 8. Safe Error Handling & Information Disclosure

- In production mode, unhandled server exceptions return generic error responses (`{"detail": "Internal server error"}`) without exposing Python tracebacks, database table names, SQL dialect information, or file paths.
- Response headers strip server banner disclosures (`X-Powered-By`).
