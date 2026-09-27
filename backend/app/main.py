from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config.database import engine, ensure_schema
from app.config.settings import settings
from app.routes import auth, users, cv, jobs, matching, notifications, collaborations
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    starlette_http_exception_handler
)

# Create database tables and apply lightweight column migrations
ensure_schema(engine)

# Classify any jobs collected before the field column existed
from app.config.database import SessionLocal  # noqa: E402
from app.services.job_service import backfill_job_fields  # noqa: E402

_db = SessionLocal()
try:
    backfill_job_fields(_db)
finally:
    _db.close()

app = FastAPI(
    title="AI Job Matching System",
    description="AI-powered job matching platform with CV analysis",
    version="0.2.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.CORS_ORIGINS == "*" else [
        origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(cv.router, prefix="/api/cv", tags=["cv"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(collaborations.router, prefix="/api/collaborations", tags=["collaborations"])

@app.get("/")
async def root():
    return {"message": "AI Job Matching System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """Liveness + DB connectivity + basic stats for monitoring."""
    from sqlalchemy import text
    from app.config.database import SessionLocal
    from app.models.job import ExternalJob

    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            active_jobs = db.query(ExternalJob).filter(ExternalJob.is_active == True).count()  # noqa: E712
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "unreachable",
            "detail": str(e),
        }

    return {
        "status": "healthy",
        "database": "ok",
        "active_jobs": active_jobs,
    }
