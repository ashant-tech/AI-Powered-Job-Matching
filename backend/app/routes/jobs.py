from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.models.cv import CV
from app.schemas.job import ExternalJob
from app.services.field_classifier import FIELDS, normalize_department
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
    field: Optional[str] = None,
    remote_only: Optional[bool] = Query(None, description="Filter for remote jobs only"),
    salary_min: Optional[float] = Query(None, description="Minimum salary"),
    salary_max: Optional[float] = Query(None, description="Maximum salary"),
    deadline_days: Optional[int] = Query(None, description="Jobs with deadline within X days"),
    db: Session = Depends(get_db)
):
    if field and field not in FIELDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown field. Valid fields: {', '.join(FIELDS)}"
        )
    job_service = JobService(db)
    return job_service.get_jobs(
        skip=skip,
        limit=limit,
        search=search,
        location=location,
        job_type=job_type,
        field=field,
        remote_only=remote_only,
        salary_min=salary_min,
        salary_max=salary_max,
        deadline_days=deadline_days
    )

@router.get("/fields", response_model=list[str])
async def get_fields():
    """Valid job fields a department can map to (for UI filter dropdowns)."""
    return list(FIELDS)

@router.get("/recommended", response_model=list[ExternalJob])
async def get_recommended_jobs(
    limit: int = 50,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Jobs matched to the current user's department (and CV skills when available).

    A computer-science user gets computer/IT-related jobs first; users without
    a department get the general listing ranked by CV skills.
    """
    cv = db.query(CV).filter(CV.user_id == current_user.id).first()
    return JobService(db).get_recommended_jobs(current_user, cv=cv, limit=limit)

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
