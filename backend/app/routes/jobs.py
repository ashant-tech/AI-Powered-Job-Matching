from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.schemas.job import JobCreate, JobResponse
from app.services.job_service import JobService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=JobResponse)
async def create_job(job: JobCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    job_service = JobService(db)
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
