from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import get_current_user
from app.schemas.job import JobCreate, JobOut
from app.services import job_service

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
def list_jobs(
    q: str | None = None,
    location: str | None = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return job_service.list_jobs(db, q, location, limit, offset)


@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    return job_service.get_job(db, job_id)


@router.post("", response_model=JobOut, status_code=201, dependencies=[Depends(get_current_user)])
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    return job_service.create_job(db, data)
