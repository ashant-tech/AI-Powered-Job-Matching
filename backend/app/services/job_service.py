import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.cv import CV
from app.models.job import ExternalJob
from app.models.match import Match
from app.models.user import User
from app.services.external_job_service import ExternalJobService, upsert_jobs
from app.services.field_classifier import classify_job, field_matches, normalize_department


def backfill_job_fields(db: Session) -> int:
    """Classify jobs that don't have a field yet. Returns rows updated."""
    jobs = db.query(ExternalJob).filter(ExternalJob.field.is_(None)).all()
    for job in jobs:
        job.field = classify_job(job.title, job.description or "", job.skills or "", job.requirements or "")
    if jobs:
        db.commit()
    return len(jobs)


def _parse_skills(skills_json: Optional[str]) -> set:
    if not skills_json:
        return set()
    try:
        parsed = json.loads(skills_json)
        if isinstance(parsed, list):
            return {str(s).lower() for s in parsed}
    except (ValueError, TypeError):
        pass
    return set()


class JobService:
    def __init__(self, db: Session):
        self.db = db

    def upsert_jobs(self, records: list[dict]) -> dict:
        return upsert_jobs(self.db, records)

    def get_jobs(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        location: Optional[str] = None,
        job_type: Optional[str] = None,
        field: Optional[str] = None
    ) -> List[ExternalJob]:
        jobs = ExternalJobService(self.db).fetch_jobs()

        if search:
            search_lower = search.lower()
            jobs = [job for job in jobs if search_lower in f"{job.title} {job.description or ''} {job.company}".lower()]
        if location:
            jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        if field:
            jobs = [job for job in jobs if field_matches(job.field, field)]

        return jobs[skip:skip + limit]

    def get_recommended_jobs(self, user: User, cv: Optional[CV] = None, limit: int = 50) -> List[ExternalJob]:
        """Jobs for a specific user: field auto-detected from their CV (department as
        fallback), ranked by CV skill overlap."""
        user_field = None
        if cv is not None and cv.field and cv.field != "other":
            user_field = cv.field
        if not user_field:
            user_field = normalize_department(user.department)
        jobs = [job for job in ExternalJobService(self.db).fetch_jobs() if field_matches(job.field, user_field, strict=True)]

        cv_skills = _parse_skills(cv.skills if cv else None)

        def rank_key(job):
            overlap = len(cv_skills & _parse_skills(job.skills)) if cv_skills else 0
            # same classified field first, then skill overlap, then newest
            same_field = 1 if (user_field and job.field == user_field) else 0
            return (same_field, overlap, job.posted_at or job.created_at)

        jobs.sort(key=rank_key, reverse=True)
        return jobs[:limit]

    def get_job(self, external_id: str) -> Optional[ExternalJob]:
        job = self.db.query(ExternalJob).filter(ExternalJob.external_id == external_id).first()
        if job and self._is_current(job):
            return job
        return None

    def deactivate_expired_jobs(self) -> int:
        """Mark jobs whose deadline has passed as inactive. Returns the number deactivated."""
        now = datetime.utcnow()
        expired_ids = [
            row[0] for row in self.db.query(ExternalJob.external_id).filter(
                ExternalJob.is_active == True,  # noqa: E712
                ExternalJob.deadline.isnot(None),
                ExternalJob.deadline <= now,
            ).all()
        ]
        if not expired_ids:
            return 0

        self.db.query(ExternalJob).filter(
            ExternalJob.external_id.in_(expired_ids)
        ).update({"is_active": False}, synchronize_session=False)
        self.db.commit()
        return len(expired_ids)

    def purge_expired_matches(self) -> int:
        """Delete matches pointing at inactive jobs. Returns the number deleted."""
        inactive_ids = [
            row[0] for row in self.db.query(ExternalJob.external_id).filter(
                ExternalJob.is_active == False  # noqa: E712
            ).all()
        ]
        if not inactive_ids:
            return 0

        deleted = self.db.query(Match).filter(
            Match.external_job_id.in_(inactive_ids)
        ).delete(synchronize_session=False)
        self.db.commit()
        return deleted

    @staticmethod
    def _is_current(job: ExternalJob) -> bool:
        if not job.is_active:
            return False
        return job.deadline is None or job.deadline > datetime.utcnow()
