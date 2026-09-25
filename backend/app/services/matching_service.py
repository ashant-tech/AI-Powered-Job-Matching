from sqlalchemy.orm import Session
import json
from typing import List
from app.models.match import Match
from app.models.cv import CV
from app.models.job import ExternalJob
from app.schemas.match import MatchResponse, JobInfo
from app.ai.semantic_matcher import SemanticMatcher
from app.ai.ranking import rank_matches
from app.services.notification_service import NotificationService
from app.services.external_job_service import ExternalJobService
from app.services.job_service import JobService

class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.semantic_matcher = SemanticMatcher()
        self.external_job_service = ExternalJobService(db)
        self.notification_threshold = 0.3  # Lower threshold for notifications (30%)

    def find_matches_for_cv(self, user_id: int, cv_id: int) -> List[MatchResponse]:
        cv = self.db.query(CV).filter(CV.id == cv_id).first()
        if not cv:
            raise ValueError("CV not found")

        # Drop jobs whose deadline passed (and any matches pointing at them) before scoring
        job_service = JobService(self.db)
        job_service.deactivate_expired_jobs()
        job_service.purge_expired_matches()

        jobs = self.external_job_service.fetch_jobs()

        # Calculate match scores for each job
        matches = []
        new_matches = []
        high_quality_matches = []
        for job in jobs:
            match_score = self.semantic_matcher.calculate_match_score(cv, job)

            existing_match = self.db.query(Match).filter(
                Match.user_id == user_id,
                Match.cv_id == cv_id,
                Match.external_job_id == job.external_id
            ).first()

            if existing_match:
                matches.append(existing_match)
                continue

            match = Match(
                user_id=user_id,
                cv_id=cv_id,
                external_job_id=job.external_id,
                match_score=match_score,
                match_reasons=json.dumps({"score_breakdown": match_score})
            )

            self.db.add(match)
            matches.append(match)
            new_matches.append(match)

            # Track high-quality matches for notification
            if match_score >= self.notification_threshold:
                high_quality_matches.append(match)

        self.db.commit()

        # Only send notification for high-quality matches
        if high_quality_matches:
            # Get job objects for notification
            job_objects = []
            for match in high_quality_matches:
                job = next((job for job in jobs if job.external_id == match.external_job_id), None)
                if job:
                    job_objects.append(job)

            NotificationService(self.db).send_match_notification(
                user_id=user_id,
                match_count=len(high_quality_matches),
                top_jobs=job_objects[:5]
            )

        # Rank matches
        ranked_matches = rank_matches(matches)

        # Include job information in response
        match_responses = []
        for match in ranked_matches:
            # Get job information separately to avoid relationship issues
            job = next((job for job in jobs if job.external_id == match.external_job_id), None)
            job_info = JobInfo.model_validate(job) if job else None

            match_dict = MatchResponse.model_validate(match).model_dump()
            match_dict['job'] = job_info.model_dump() if job_info else None
            match_responses.append(MatchResponse(**match_dict))

        return match_responses

    def find_matches_for_all_users(self) -> int:
        """Run matching for every user CV so new jobs generate notifications. Returns CVs processed."""
        processed = 0
        for cv in self.db.query(CV).all():
            try:
                self.find_matches_for_cv(cv.user_id, cv.id)
                processed += 1
            except Exception as e:
                print(f"Error matching CV {cv.id} for user {cv.user_id}: {e}")
        return processed

    def get_user_matches(self, user_id: int) -> List[MatchResponse]:
        matches = self.db.query(Match).filter(Match.user_id == user_id).all()
        jobs = {job.external_id: job for job in self.external_job_service.fetch_jobs()}
        return [self._response(match, jobs.get(match.external_job_id)) for match in matches if match.external_job_id in jobs]

    def get_match(self, match_id: int) -> Match:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def update_match_status(self, match_id: int, status: str) -> Match:
        match = self.get_match(match_id)
        if not match:
            raise ValueError("Match not found")

        match.status = status
        self.db.commit()
        self.db.refresh(match)

        return match

    def get_top_matches(self, user_id: int, limit: int = 10) -> List[MatchResponse]:
        matches = self.db.query(Match).filter(
            Match.user_id == user_id,
            Match.status == "pending"
        ).order_by(Match.match_score.desc()).limit(limit).all()

        jobs = {job.external_id: job for job in self.external_job_service.fetch_jobs()}
        return [self._response(match, jobs.get(match.external_job_id)) for match in matches if match.external_job_id in jobs]

    def _response(self, match: Match, job: ExternalJob | None) -> MatchResponse:
        match_dict = MatchResponse.model_validate(match).model_dump()
        match_dict["job"] = JobInfo.model_validate(job).model_dump() if job else None
        return MatchResponse(**match_dict)
