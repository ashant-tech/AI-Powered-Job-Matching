import json
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user import User
from app.models.cv import CV
from app.models.job import ExternalJob
from app.models.match import Match
from app.models.notification import Notification
from app.services.external_job_service import upsert_jobs
from app.services.job_service import JobService
from app.services.notification_service import NotificationService
from app.services.matching_service import MatchingService


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def user(db_session):
    user = User(email="test@example.com", username="testuser", hashed_password="hash", full_name="Test User")
    db_session.add(user)
    db_session.commit()
    return user


def _seed_job(db, external_id, days_offset):
    deadline = datetime.utcnow() + timedelta(days=days_offset)
    upsert_jobs(db, [{
        "external_id": external_id,
        "title": f"Role {external_id}",
        "company": "Example Co",
        "description": "A job description",
        "deadline": deadline.isoformat(),
    }])
    return db.query(ExternalJob).filter(ExternalJob.external_id == external_id).one()


def test_get_jobs_excludes_expired(db_session):
    _seed_job(db_session, "future", 10)
    _seed_job(db_session, "past", -10)

    jobs = JobService(db_session).get_jobs()
    assert [job.external_id for job in jobs] == ["future"]


def test_deactivate_expired_jobs(db_session):
    job = _seed_job(db_session, "aging", 10)

    # Simulate time passing: deadline now in the past but still flagged active
    job.deadline = datetime.utcnow() - timedelta(days=1)
    db_session.commit()

    deactivated = JobService(db_session).deactivate_expired_jobs()
    assert deactivated == 1
    db_session.refresh(job)
    assert job.is_active is False

    # Second run is a no-op
    assert JobService(db_session).deactivate_expired_jobs() == 0


def test_purge_expired_matches(db_session, user):
    active = _seed_job(db_session, "active", 10)
    expired = _seed_job(db_session, "expired", -10)

    cv = CV(user_id=user.id, title="CV", file_path="/cv.pdf", file_name="cv.pdf", parsed_text="text")
    db_session.add(cv)
    db_session.commit()
    for job in (active, expired):
        db_session.add(Match(user_id=user.id, cv_id=cv.id, external_job_id=job.external_id, match_score=0.9))
    db_session.commit()

    deleted = JobService(db_session).purge_expired_matches()
    assert deleted == 1
    remaining = db_session.query(Match).all()
    assert [match.external_job_id for match in remaining] == ["active"]


def test_purge_expired_notifications_deletes_and_trims(db_session, user):
    active = _seed_job(db_session, "active", 10)
    expired = _seed_job(db_session, "expired", -10)

    service = NotificationService(db_session)
    partial = service.create_notification(
        user.id, "match", "Matches", "original message",
        send_telegram=False,
        external_job_ids=[active.external_id, expired.external_id],
    )
    all_expired = service.create_notification(
        user.id, "match", "Matches", "stale message",
        send_telegram=False,
        external_job_ids=[expired.external_id],
    )

    deleted = service.purge_expired_notifications(user_id=user.id)
    assert deleted == 1
    assert db_session.query(Notification).filter(Notification.id == all_expired.id).first() is None

    db_session.refresh(partial)
    assert json.loads(partial.external_job_ids) == [active.external_id]
    assert active.title in partial.message
    assert expired.title not in partial.message


def test_matching_skips_expired_jobs_and_notifies(db_session, user):
    _seed_job(db_session, "expired", -10)
    future = datetime.utcnow() + timedelta(days=10)
    upsert_jobs(db_session, [{
        "external_id": "active",
        "title": "Python Developer",
        "company": "Tech Corp",
        "description": "Python developer role requiring 2 years of experience",
        "skills": '["python"]',
        "location": "Remote",
        "job_type": "remote",
        "deadline": future.isoformat(),
    }])

    cv = CV(
        user_id=user.id,
        title="CV",
        file_path="/cv.pdf",
        file_name="cv.pdf",
        parsed_text="Python developer with 3 years of experience building APIs",
        skills='["python"]',
    )
    db_session.add(cv)
    db_session.commit()

    matches = MatchingService(db_session).find_matches_for_cv(user.id, cv.id)

    assert [match.external_job_id for match in matches] == ["active"]
    assert matches[0].job is not None
    assert matches[0].job.deadline is not None

    notifications = db_session.query(Notification).filter(Notification.user_id == user.id).all()
    assert len(notifications) == 1
    assert json.loads(notifications[0].external_job_ids) == ["active"]
    assert "Python Developer" in notifications[0].message


def test_find_matches_for_all_users(db_session, user):
    _seed_job(db_session, "active", 10)
    cv = CV(
        user_id=user.id,
        title="CV",
        file_path="/cv.pdf",
        file_name="cv.pdf",
        parsed_text="Python developer with 3 years of experience",
        skills='["python"]',
    )
    db_session.add(cv)
    db_session.commit()

    processed = MatchingService(db_session).find_matches_for_all_users()
    assert processed == 1
    assert db_session.query(Match).count() == 1
