from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.job import ExternalJob
from app.services.external_job_service import ExternalJobService

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job: ExternalJob) -> ExternalJob:
        raise ValueError("External jobs cannot be created or stored locally")

    def get_job(self, external_id: str) -> ExternalJob | None:
        return next((job for job in ExternalJobService().fetch_jobs() if job.external_id == external_id), None)

    def get_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> List[ExternalJob]:
        jobs = ExternalJobService().fetch_jobs()
        if search:
            search_lower = search.lower()
            jobs = [job for job in jobs if search_lower in f"{job.title} {job.description} {job.company}".lower()]
        if location:
            jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        return jobs[skip:skip + limit]
