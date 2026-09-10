from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.ai.embeddings import embed_text
from app.ai.job_analyzer import analyze_job
from app.middleware.error_handler import AppError
from app.models.job import Job
from app.schemas.job import JobCreate
from app.services.cv_service import get_or_create_skills


def create_job(db: Session, data: JobCreate) -> Job:
    if data.source_url and db.query(Job).filter(Job.source_url == data.source_url).first():
        raise AppError("Job with this source URL already exists", 409)
    auto_skills, auto_years = analyze_job(data.description, data.requirements)
    skills = sorted(set(data.skills) | set(auto_skills))
    job = Job(
        **data.model_dump(exclude={"skills", "min_years_experience"}),
        min_years_experience=data.min_years_experience or auto_years,
        embedding=embed_text(f"{data.title}\n{data.description}\n{data.requirements}"),
    )
    job.skills = get_or_create_skills(db, skills)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def list_jobs(db: Session, q: str | None = None, location: str | None = None, limit: int = 50, offset: int = 0) -> list[Job]:
    query = db.query(Job).filter(Job.is_active.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Job.title.ilike(like), Job.company.ilike(like), Job.description.ilike(like)))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    return query.order_by(Job.posted_at.desc(), Job.id.desc()).offset(offset).limit(limit).all()


def get_job(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise AppError("Job not found", 404)
    return job
