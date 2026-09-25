import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.job import ExternalJob
from app.services.external_job_service import ExternalJobService, upsert_jobs


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


def test_trusted_url_checks(monkeypatch):
    monkeypatch.setenv("TRUSTED_JOB_DOMAINS", "trustedjobs.example")
    service = ExternalJobService()

    assert service._is_trusted_url("https://careers.trustedjobs.example/jobs/1")
    assert service._is_trusted_url("https://trustedjobs.example/jobs/1")
    assert not service._is_trusted_url("http://trustedjobs.example/jobs")  # not HTTPS
    assert not service._is_trusted_url("https://untrusted.example/jobs")
    assert not service._is_trusted_url("https://nottrustedjobs.example/jobs")  # suffix must respect domain boundary


def test_upsert_jobs_creates_and_updates(db_session):
    record = {
        "title": "Python Developer",
        "company": "Example Co",
        "description": "Build APIs",
        "apply_url": "https://careers.trustedjobs.example/jobs/job-1",
        "source": "test",
    }

    counts = upsert_jobs(db_session, [record])
    assert counts == {"created": 1, "updated": 0, "skipped": 0}

    record["title"] = "Senior Python Developer"
    counts = upsert_jobs(db_session, [record])
    assert counts == {"created": 0, "updated": 1, "skipped": 0}

    assert db_session.query(ExternalJob).count() == 1
    job = db_session.query(ExternalJob).first()
    assert job.title == "Senior Python Developer"
    assert job.apply_url == "https://careers.trustedjobs.example/jobs/job-1"


def test_upsert_jobs_skips_invalid_records(db_session):
    counts = upsert_jobs(db_session, [
        {"title": "", "company": "Co", "description": "d"},  # empty title
        {"title": "T", "company": "", "description": "d"},  # empty company
        {"title": "T", "company": "C", "description": "   "},  # blank description
        "not-a-dict",
    ])
    assert counts == {"created": 0, "updated": 0, "skipped": 4}
    assert db_session.query(ExternalJob).count() == 0


def test_upsert_jobs_parses_deadline_from_description(db_session):
    upsert_jobs(db_session, [{
        "external_id": "job-deadline",
        "title": "Accountant",
        "company": "Example Co",
        "description": "Great role. Deadline: October 15, 2026. Apply now.",
    }])

    job = db_session.query(ExternalJob).filter(ExternalJob.external_id == "job-deadline").one()
    assert job.deadline == datetime(2026, 10, 15)
    assert job.is_active is True


def test_upsert_jobs_stores_expired_jobs_as_inactive(db_session):
    past = datetime.utcnow() - timedelta(days=1)
    upsert_jobs(db_session, [{
        "external_id": "job-expired",
        "title": "Old Role",
        "company": "Example Co",
        "description": "Already closed",
        "deadline": past.isoformat(),
    }])

    job = db_session.query(ExternalJob).filter(ExternalJob.external_id == "job-expired").one()
    assert job.is_active is False


def test_upsert_jobs_applies_default_ttl_when_no_deadline(db_session):
    upsert_jobs(db_session, [{
        "external_id": "job-ttl",
        "title": "Role",
        "company": "Example Co",
        "description": "No deadline mentioned",
    }], default_ttl_days=7)

    job = db_session.query(ExternalJob).filter(ExternalJob.external_id == "job-ttl").one()
    assert job.deadline is not None
    assert job.deadline > datetime.utcnow()
    assert job.is_active is True


def test_fetch_jobs_returns_only_active_jobs(db_session):
    future = datetime.utcnow() + timedelta(days=5)
    past = datetime.utcnow() - timedelta(days=5)

    upsert_jobs(db_session, [
        {"external_id": "active", "title": "Open", "company": "Co", "description": "d", "deadline": future.isoformat()},
        {"external_id": "expired", "title": "Closed", "company": "Co", "description": "d", "deadline": past.isoformat()},
        {"external_id": "inactive", "title": "Pulled", "company": "Co", "description": "d", "deadline": future.isoformat(), "is_active": False},
    ])

    jobs = ExternalJobService(db_session).fetch_jobs()
    assert [job.external_id for job in jobs] == ["active"]
