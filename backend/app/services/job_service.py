from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.job import Job
from app.schemas.job import JobCreate

class JobService:
    def __init__(self, db: Session):
        self.db = db

    def create_job(self, job: JobCreate) -> Job:
        db_job = Job(**job.model_dump())
        self.db.add(db_job)
        self.db.commit()
        self.db.refresh(db_job)
        return db_job

    def get_job(self, job_id: int) -> Optional[Job]:
        return self.db.query(Job).filter(Job.id == job_id).first()

    def get_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None
    ) -> List[Job]:
        query = self.db.query(Job).filter(Job.is_active == 1)
        
        if search:
            query = query.filter(
                (Job.title.contains(search)) |
                (Job.description.contains(search)) |
                (Job.company.contains(search))
            )
        
        if location:
            query = query.filter(Job.location.contains(location))
        
        if job_type:
            query = query.filter(Job.job_type == job_type)
        
        return query.offset(skip).limit(limit).all()

    def update_job(self, job_id: int, job_update: dict) -> Job:
        job = self.get_job(job_id)
        if not job:
            raise ValueError("Job not found")
        
        for field, value in job_update.items():
            setattr(job, field, value)
        
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete_job(self, job_id: int) -> bool:
        job = self.get_job(job_id)
        if not job:
            return False
        
        job.is_active = 0
        self.db.commit()
        return True
