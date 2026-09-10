from sqlalchemy.orm import Session

from app.ai.ranking import rank_jobs
from app.middleware.error_handler import AppError
from app.models.cv import CV
from app.models.job import Job
from app.models.match import Match
from app.models.user import User
from app.services.cv_service import get_latest_cv
from app.services.notification_service import notify_new_matches

NOTIFY_THRESHOLD = 60.0


def compute_matches(db: Session, user: User, cv_id: int | None = None, limit: int = 20) -> list[Match]:
    cv = db.query(CV).filter(CV.id == cv_id, CV.user_id == user.id).first() if cv_id else get_latest_cv(db, user)
    if cv is None:
        raise AppError("Upload a CV before requesting recommendations", 404)

    jobs = db.query(Job).filter(Job.is_active.is_(True)).all()
    existing = {m.job_id: m for m in db.query(Match).filter(Match.cv_id == cv.id).all()}
    new_matches: list[Match] = []

    for result in rank_jobs(cv, jobs):
        match = existing.get(result.job.id)
        is_new = match is None
        if match is None:
            match = Match(cv_id=cv.id, job_id=result.job.id)
            db.add(match)
        match.score = result.score
        match.skill_score = result.skill_score
        match.semantic_score = result.semantic_score
        match.experience_score = result.experience_score
        match.matched_skills = result.matched_skills
        match.missing_skills = result.missing_skills
        if is_new and result.score >= NOTIFY_THRESHOLD:
            new_matches.append(match)

    db.commit()
    if new_matches:
        notify_new_matches(db, user, new_matches)

    return db.query(Match).filter(Match.cv_id == cv.id).order_by(Match.score.desc()).limit(limit).all()


def list_matches(db: Session, user: User, limit: int = 20) -> list[Match]:
    cv = get_latest_cv(db, user)
    if cv is None:
        return []
    return db.query(Match).filter(Match.cv_id == cv.id).order_by(Match.score.desc()).limit(limit).all()


def match_all_users_for_job(db: Session, job: Job) -> int:
    """Called by the job collector after inserting a job; notifies every user with a good match."""
    count = 0
    for user in db.query(User).filter(User.is_active.is_(True)).all():
        cv = get_latest_cv(db, user)
        if cv is None:
            continue
        result = rank_jobs(cv, [job])[0]
        already = db.query(Match).filter(Match.cv_id == cv.id, Match.job_id == job.id).first()
        if result.score >= NOTIFY_THRESHOLD and already is None:
            match = Match(
                cv_id=cv.id,
                job_id=job.id,
                score=result.score,
                skill_score=result.skill_score,
                semantic_score=result.semantic_score,
                experience_score=result.experience_score,
                matched_skills=result.matched_skills,
                missing_skills=result.missing_skills,
            )
            db.add(match)
            db.commit()
            notify_new_matches(db, user, [match])
            count += 1
    return count
