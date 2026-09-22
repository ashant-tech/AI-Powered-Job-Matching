from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.schemas.job import ExternalJob
from app.services.job_service import JobService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.get("/", response_model=list[ExternalJob])
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

@router.get("/{external_id}", response_model=ExternalJob)
async def get_job(external_id: str, db: Session = Depends(get_db)):
    job_service = JobService(db)
    job = job_service.get_job(external_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job
