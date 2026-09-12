from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService
from app.services.auth_service import AuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    job_service = JobService(db)
    auth_service = AuthService(db)
    user = auth_service.get_current_user(token)
    
    return job_service.create_job(job)

@router.get("/", response_model=list[JobResponse])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    location: Optional[str] = None,
    job_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    job_service = JobService(db)
    return job_service.get_jobs(skip=skip, limit=limit, search=search, location=location, job_type=job_type)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job
