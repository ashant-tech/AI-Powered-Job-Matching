import json
import re
from datetime import datetime, timedelta
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


def _token_relevance(token: str, job: ExternalJob) -> float:
    """Weight of one search token against a job, or 0.0 if it matches nowhere.
    Title beats skills beats company beats description. Tokens of 4+ chars may
    match inside a word; shorter tokens must match on a word boundary so 'it'
    does not hit 'required'/'abilities' in nearly every posting."""
    word_re = re.compile(r"\b" + re.escape(token) + r"\b")
    allow_substring = len(token) >= 4
    best = 0.0
    for text, weight in (
        (job.title or "", 5.0),
        (job.skills or "", 3.0),
        (job.company or "", 2.0),
        (job.description or "", 1.0),
    ):
        low = text.lower()
        if word_re.search(low) or (allow_substring and token in low):
            best = max(best, weight)
    return best


def _search_relevance(job: ExternalJob, tokens: List[str]) -> float:
    """Total relevance across all query tokens. Returns 0.0 if ANY token is
    unmatched, so results only contain jobs relevant to the whole query."""
    total = 0.0
    for token in tokens:
        score = _token_relevance(token, job)
        if score == 0.0:
            return 0.0
        total += score
    return total


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
        field: Optional[str] = None,
        remote_only: Optional[bool] = None,
        salary_min: Optional[float] = None,
        salary_max: Optional[float] = None,
        deadline_days: Optional[int] = None
    ) -> List[ExternalJob]:
        jobs = ExternalJobService(self.db).fetch_jobs()

        if search:
            tokens = [t for t in re.split(r"\s+", search.lower().strip()) if t]
            if tokens:
                scored = [(_search_relevance(job, tokens), job) for job in jobs]
                scored = [pair for pair in scored if pair[0] > 0.0]
                scored.sort(
                    key=lambda pair: (
                        pair[0],
                        pair[1].posted_at or pair[1].created_at or datetime.min,
                    ),
                    reverse=True,
                )
                jobs = [job for _, job in scored]
        if location:
            jobs = [job for job in jobs if job.location and location.lower() in job.location.lower()]
        if job_type:
            jobs = [job for job in jobs if job.job_type == job_type]
        if field:
            # When user explicitly selects a field, use strict filtering
            # Only show jobs in that exact field, exclude 'other' jobs
            jobs = [job for job in jobs if job.field == field]
        if remote_only:
            jobs = [job for job in jobs if self._is_remote(job)]
        if salary_min is not None:
            jobs = [job for job in jobs if job.salary_min and job.salary_min >= salary_min]
        if salary_max is not None:
            jobs = [job for job in jobs if job.salary_max and job.salary_max <= salary_max]
        if deadline_days is not None:
            jobs = [job for job in jobs if self._matches_deadline(job, deadline_days)]

        return jobs[skip:skip + limit]

    def _is_remote(self, job: ExternalJob) -> bool:
        """Check if a job is remote based on job_type, location, or description."""
        if job.job_type and job.job_type.lower() == 'remote':
            return True
        if job.location and 'remote' in job.location.lower():
            return True
        if job.description and 'remote' in job.description.lower():
            return True
        return False

    def _matches_deadline(self, job: ExternalJob, days: int) -> bool:
        """Check if job deadline is within specified days from now."""
        if not job.deadline:
            return True  # Jobs without deadline match any deadline filter
        now = datetime.utcnow()
        deadline_date = job.deadline
        days_until_deadline = (deadline_date - now).days
        return days_until_deadline <= days and days_until_deadline >= 0

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
