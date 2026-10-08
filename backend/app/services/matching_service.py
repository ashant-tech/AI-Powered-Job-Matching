from sqlalchemy.orm import Session
import json
import logging
import re
from typing import List
from app.models.match import Match
from app.models.cv import CV
from app.models.job import ExternalJob
from app.models.user import User
from app.schemas.match import MatchResponse, JobInfo
from app.ai.semantic_matcher import SemanticMatcher
from app.ai.ranking import filter_low_quality_matches, rank_matches
from app.services.notification_service import NotificationService
from app.services.external_job_service import ExternalJobService
from app.services.field_classifier import field_matches, normalize_department
from app.services.job_service import JobService


MIN_MATCH_SCORE = 45.0
logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.semantic_matcher = SemanticMatcher()
        self.external_job_service = ExternalJobService(db)
        self.notification_threshold = MIN_MATCH_SCORE

    def find_matches_for_cv(self, user_id: int, cv_id: int) -> List[MatchResponse]:
        cv = self.db.query(CV).filter(CV.id == cv_id).first()
        if not cv or cv.user_id != user_id:
            raise ValueError("CV not found")

        # Drop jobs whose deadline passed (and any matches pointing at them) before scoring
        job_service = JobService(self.db)
        job_service.deactivate_expired_jobs()
        job_service.purge_expired_matches()

        jobs = self.external_job_service.fetch_jobs()

        # Restrict candidates to the user's field, auto-detected from their CV
        # (education/skills/text); a manually set department is the fallback.
        # Jobs classified as 'other' are never excluded.
        user_field = cv.field if cv.field and cv.field != "other" else None
        if not user_field:
            user = self.db.query(User).filter(User.id == user_id).first()
            user_field = normalize_department(user.department) if user else None
        jobs = [job for job in jobs if field_matches(job.field, user_field, strict=True)]
        jobs_by_id = {job.external_id: job for job in jobs}
        feedback_examples = [
            (jobs_by_id[match.external_job_id], match.status)
            for match in self.db.query(Match).filter(
                Match.user_id == user_id,
                Match.cv_id == cv_id,
                Match.status.in_(["relevant", "not_relevant"]),
            ).all()
            if match.external_job_id in jobs_by_id
        ]

        # Calculate match scores for each job
        matches = []
        new_matches = []
        high_quality_matches = []
        for job in jobs:
            # Use enhanced matching with details
            match_details = self.semantic_matcher.calculate_match_with_details(cv, job)
            cv_match_score = match_details["match_score"]
            feedback_adjustment = self._feedback_adjustment(job, feedback_examples)
            match_score = round(max(0.0, min(100.0, cv_match_score + feedback_adjustment)), 2)
            match_details["match_score"] = match_score
            match_details["cv_match_score"] = cv_match_score
            match_details["feedback_adjustment"] = feedback_adjustment
            if feedback_adjustment:
                direction = "similar roles you marked relevant" if feedback_adjustment > 0 else "similar roles you marked not relevant"
                match_details["match_reasons"].append(
                    f"Your feedback on {direction} adjusted this estimate by {feedback_adjustment:+.1f} points."
                )
            if match_score >= 75 and match_details["score_confidence"] >= 60:
                match_details["fit_level"] = "Strong"
            elif match_score >= 55 and match_details["score_confidence"] >= 40:
                match_details["fit_level"] = "Good"
            else:
                match_details["fit_level"] = "Possible"

            existing_match = self.db.query(Match).filter(
                Match.user_id == user_id,
                Match.cv_id == cv_id,
                Match.external_job_id == job.external_id
            ).first()

            if existing_match:
                existing_match.match_score = match_score
                existing_match.match_reasons = self._serialize_match_details(match_details)
                if existing_match.status != "not_relevant":
                    matches.append(existing_match)
                continue

            if match_score < MIN_MATCH_SCORE:
                continue

            match = Match(
                user_id=user_id,
                cv_id=cv_id,
                external_job_id=job.external_id,
                match_score=match_score,
                match_reasons=self._serialize_match_details(match_details)
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

            try:
                NotificationService(self.db).send_match_notification(
                    user_id=user_id,
                    match_count=len(high_quality_matches),
                    top_jobs=job_objects[:5]
                )
            except Exception:
                self.db.rollback()
                logger.exception(
                    "Failed to send match notification for user %s after saving matches",
                    user_id,
                )

        # Rank matches
        ranked_matches = filter_low_quality_matches(
            rank_matches(matches),
            threshold=MIN_MATCH_SCORE,
        )

        # Include job information in response
        match_responses = []
        for match in ranked_matches:
            # Get job information separately to avoid relationship issues
            job = next((job for job in jobs if job.external_id == match.external_job_id), None)
            job_info = JobInfo.model_validate(job) if job else None

            # Calculate skill gaps for this match
            skill_gaps = None
            if job:
                skill_gaps = self.semantic_matcher._calculate_skill_gaps(cv, job)

            # Extract detailed reasons from match_reasons
            detailed_reasons = None
            detail_fields = {}
            if match.match_reasons:
                try:
                    reasons_data = json.loads(match.match_reasons)
                    detailed_reasons = reasons_data.get("detailed_reasons", [])
                    detail_fields = {
                        "fit_level": reasons_data.get("fit_level"),
                        "score_confidence": reasons_data.get("score_confidence"),
                        "match_caveats": reasons_data.get("match_caveats"),
                        "component_scores": reasons_data.get("component_scores"),
                        "cv_match_score": reasons_data.get("cv_match_score"),
                        "feedback_adjustment": reasons_data.get("feedback_adjustment"),
                    }
                except (json.JSONDecodeError, TypeError):
                    pass

            match_dict = MatchResponse.model_validate(match).model_dump()
            match_dict['job'] = job_info.model_dump() if job_info else None
            match_dict['skill_gaps'] = skill_gaps
            match_dict['detailed_reasons'] = detailed_reasons
            match_dict.update(detail_fields)
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

    def _resolve_user_field(self, user_id: int) -> str | None:
        """Field auto-detected from the user's CV, falling back to a manually set department."""
        for cv in self.db.query(CV).filter(CV.user_id == user_id).all():
            if cv.field and cv.field != "other":
                return cv.field
        user = self.db.query(User).filter(User.id == user_id).first()
        return normalize_department(user.department) if user else None

    def get_user_matches(self, user_id: int) -> List[MatchResponse]:
        user_field = self._resolve_user_field(user_id)
        matches = self.db.query(Match).filter(Match.user_id == user_id).all()
        jobs = {job.external_id: job for job in self.external_job_service.fetch_jobs()}
        return [
            self._response(match, jobs[match.external_job_id])
            for match in matches
            if match.match_score >= MIN_MATCH_SCORE
            and match.external_job_id in jobs
            and field_matches(jobs[match.external_job_id].field, user_field, strict=True)
        ]

    def get_match(self, match_id: int) -> Match:
        return self.db.query(Match).filter(Match.id == match_id).first()

    def update_match_status(self, match_id: int, status: str) -> Match:
        match = self.get_match(match_id)
        if not match:
            raise ValueError("Match not found")
        if status not in {"pending", "viewed", "applied", "rejected", "relevant", "not_relevant"}:
            raise ValueError("Invalid match status")

        match.status = status
        self.db.commit()
        self.db.refresh(match)

        return match

    @staticmethod
    def _feedback_adjustment(
        job: ExternalJob,
        examples: list[tuple[ExternalJob, str]],
    ) -> float:
        weighted_feedback = 0.0
        total_similarity = 0.0
        candidate_skills = MatchingService._job_skills(job)
        candidate_title = MatchingService._job_tokens(job.title)

        for example, status in examples:
            if example.external_id == job.external_id:
                continue
            example_skills = MatchingService._job_skills(example)
            example_title = MatchingService._job_tokens(example.title)
            field_similarity = float(bool(job.field and job.field == example.field))
            skill_union = candidate_skills | example_skills
            skill_similarity = (
                len(candidate_skills & example_skills) / len(skill_union)
                if skill_union else 0.0
            )
            title_union = candidate_title | example_title
            title_similarity = (
                len(candidate_title & example_title) / len(title_union)
                if title_union else 0.0
            )
            similarity = 0.2 * field_similarity + 0.5 * skill_similarity + 0.3 * title_similarity
            if similarity < 0.3 or (skill_similarity < 0.25 and title_similarity < 0.25):
                continue
            sentiment = 1.0 if status == "relevant" else -1.0
            weighted_feedback += sentiment * similarity
            total_similarity += similarity

        if not total_similarity:
            return 0.0
        return round(8.0 * weighted_feedback / max(2.0, total_similarity), 2)

    @staticmethod
    def _job_skills(job: ExternalJob) -> set[str]:
        try:
            values = json.loads(job.skills or "[]")
        except (json.JSONDecodeError, TypeError):
            values = []
        if not isinstance(values, list):
            return set()
        return {
            " ".join(re.findall(r"[a-z0-9+#.]+", str(value).lower()))
            for value in values
            if str(value).strip()
        }

    @staticmethod
    def _job_tokens(value: str | None) -> set[str]:
        stop_words = {"and", "at", "for", "of", "the", "with", "senior", "junior"}
        return {
            token for token in re.findall(r"[a-z0-9+#.]+", (value or "").lower())
            if len(token) > 1 and token not in stop_words
        }

    def get_top_matches(self, user_id: int, limit: int = 10) -> List[MatchResponse]:
        user_field = self._resolve_user_field(user_id)
        matches = self.db.query(Match).filter(
            Match.user_id == user_id,
            Match.status == "pending"
        ).order_by(Match.match_score.desc()).all()

        jobs = {job.external_id: job for job in self.external_job_service.fetch_jobs()}
        filtered = [
            match for match in matches
            if match.external_job_id in jobs and field_matches(jobs[match.external_job_id].field, user_field, strict=True)
        ]
        return [self._response(match, jobs[match.external_job_id]) for match in filtered[:limit]]

    def _response(self, match: Match, job: ExternalJob | None) -> MatchResponse:
        match_dict = MatchResponse.model_validate(match).model_dump()
        match_dict["job"] = JobInfo.model_validate(job).model_dump() if job else None

        # Extract detailed reasons from match_reasons
        detailed_reasons = None
        detail_fields = {}
        if match.match_reasons:
            try:
                reasons_data = json.loads(match.match_reasons)
                detailed_reasons = reasons_data.get("detailed_reasons", [])
                detail_fields = {
                    "fit_level": reasons_data.get("fit_level"),
                    "score_confidence": reasons_data.get("score_confidence"),
                    "match_caveats": reasons_data.get("match_caveats"),
                    "component_scores": reasons_data.get("component_scores"),
                    "cv_match_score": reasons_data.get("cv_match_score"),
                    "feedback_adjustment": reasons_data.get("feedback_adjustment"),
                }
            except (json.JSONDecodeError, TypeError):
                pass
        match_dict["detailed_reasons"] = detailed_reasons
        match_dict.update(detail_fields)

        # Calculate skill gaps if job is available
        if job:
            cv = self.db.query(CV).filter(CV.id == match.cv_id).first()
            if cv:
                skill_gaps = self.semantic_matcher._calculate_skill_gaps(cv, job)
                match_dict["skill_gaps"] = skill_gaps

        return MatchResponse(**match_dict)

    @staticmethod
    def _serialize_match_details(match_details: dict) -> str:
        return json.dumps({
            "score_breakdown": match_details["match_score"],
            "cv_match_score": match_details["cv_match_score"],
            "feedback_adjustment": match_details["feedback_adjustment"],
            "detailed_reasons": match_details["match_reasons"],
            "component_scores": match_details["component_scores"],
            "fit_level": match_details["fit_level"],
            "score_confidence": match_details["score_confidence"],
            "match_caveats": match_details["match_caveats"],
        })
