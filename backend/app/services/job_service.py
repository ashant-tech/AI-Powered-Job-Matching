from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.job import ExternalJob
from app.models.match import Match
from app.services.external_job_service import ExternalJobService, upsert_jobs


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
        job_type: Optional[str] = None
    ) -> List[ExternalJob]:
        jobs = ExternalJobService(self.db).fetch_jobs()

        if search:
            search_lower = search.lower()
            jobs = [job for job in jobs if search_lower in f"{job.title} {job.description or ''} {job.company}".lower()]
        if location:
            jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]

        return jobs[skip:skip + limit]

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
