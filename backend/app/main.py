from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.config.database import engine, Base
from app.routes import auth, users, cv, jobs, matching, notifications
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    starlette_http_exception_handler
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Job Matching System",
    description="AI-powered job matching platform with CV analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.get("/")
async def root():
    return {"message": "AI Job Matching System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
