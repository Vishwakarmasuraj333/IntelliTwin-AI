"""
IntelliTwin AI - FastAPI Core Application
------------------------------------------
Production-grade Cybersecurity Anomaly Detection & GenAI Analyst Gateway.
Includes structured request tracing, correlation IDs, latency measurement,
health/readiness probes, and hardened CORS.
"""

import time
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.database import init_db, SessionLocal
from app.api.routes import auth, detection, gemini, events, models, dashboard, admin
from app.services.ml_service import ml_engine
from app.services.shap_service import shap_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("IntelliTwin_Core")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Sequence
    logger.info("Initializing IntelliTwin AI Platform Services...")
    try:
        init_db()
        ml_engine.load_models()
        shap_service.load_explainer()
        logger.info("All services, models, and database initialized successfully.")
    except Exception as e:
        logger.error(f"Startup warning / error: {e}")
    yield
    # Teardown Sequence
    logger.info("Shutting down IntelliTwin AI Platform...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise Cybersecurity Anomaly Detection, Explainable AI (SHAP) & GenAI Analyst Platform",
    lifespan=lifespan
)

# CORS Middleware (Whitelisted origins only)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"]
)

# Request ID & Latency Tracking Middleware
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{process_time_ms}ms"
    
    # Log structured, privacy-conscious request summary
    logger.info(
        f"req_id={request_id[:8]} method={request.method} path={request.url.path} "
        f"status={response.status_code} latency={process_time_ms}ms"
    )
    return response

# Global Exception Handler (Never crash application or leak stack traces)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Platform Error",
            "message": "An unexpected error occurred during request processing. Diagnostic event logged.",
            "path": str(request.url.path)
        }
    )

# Include API Routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(detection.router, prefix=settings.API_V1_PREFIX)
app.include_router(gemini.router, prefix=settings.API_V1_PREFIX)
app.include_router(events.router, prefix=settings.API_V1_PREFIX)
app.include_router(models.router, prefix=settings.API_V1_PREFIX)
app.include_router(dashboard.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_PREFIX
    }

@app.get("/health")
def liveness_check():
    """Liveness probe for container orchestrators and platform monitoring."""
    return {"status": "LIVE", "timestamp": time.time()}

@app.get("/ready")
def readiness_check():
    """Readiness probe checking database connectivity and ML engine readiness."""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(admin.User.__table__.select().limit(1))
        db.close()
        db_ok = True
    except Exception as e:
        logger.warning(f"Database readiness probe failed: {e}")

    ml_ok = ml_engine.model is not None and ml_engine.preprocessor is not None

    if db_ok and ml_ok:
        return {
            "status": "READY",
            "database": "CONNECTED",
            "ml_engine": "INITIALIZED",
            "active_model": ml_engine.model_name
        }
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "NOT_READY",
            "database": "CONNECTED" if db_ok else "UNAVAILABLE",
            "ml_engine": "INITIALIZED" if ml_ok else "PENDING_TRAINING"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
