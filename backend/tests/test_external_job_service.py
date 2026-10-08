import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.job import ExternalJob
from app.services.external_job_service import ExternalJobService, upsert_jobs
from app.services.job_service import backfill_job_fields


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


def test_upsert_jobs_merges_cross_source_copies(db_session):
    description = (
        "Responsible for managing financial reports, budgets, reconciliations, monthly closes, "
        "regulatory filings, audit support, and internal controls across the organization."
    )
    future = datetime.utcnow() + timedelta(days=10)
    counts = upsert_jobs(db_session, [{
        "external_id": "telegram-101",
        "title": "Finance Officer",
        "company": "Example Microfinance",
        "location": "Addis Ababa, Ethiopia",
        "description": description,
        "skills": "Excel, Budgeting",
        "source": "Telegram",
        "apply_url": "https://t.me/jobs/101",
        "deadline": future.isoformat(),
    }])
    assert counts == {"created": 1, "updated": 0, "skipped": 0}

    counts = upsert_jobs(db_session, [{
        "external_id": "website-finance-officer",
        "title": "Job Vacancy: Finance Officer",
        "company": "Example Microfinance",
        "location": "Addis Ababa",
        "description": description + " Candidates should submit an updated CV.",
        "skills": ["Accounting"],
        "source": "Ethiojobs",
        "apply_url": "https://careers.example.com/finance-officer",
        "deadline": (datetime.utcnow() - timedelta(days=1)).isoformat(),
    }])

    job = db_session.query(ExternalJob).one()
    assert counts == {"created": 0, "updated": 1, "skipped": 0}
    assert job.external_id == "telegram-101"
    assert job.source == "Telegram, Ethiojobs"
    assert job.apply_url == "https://careers.example.com/finance-officer"
    assert "Excel" in job.skills
    assert "Budgeting" in job.skills
    assert "Accounting" in job.skills
    assert job.is_active is True


def test_upsert_jobs_keeps_distinct_openings_separate(db_session):
    upsert_jobs(db_session, [
        {
            "external_id": "finance-opening",
            "title": "Finance Officer",
            "company": "Example Microfinance",
            "location": "Addis Ababa",
            "description": (
                "Manage financial reports, budgets, reconciliations, monthly closes, regulatory "
                "filings, audit support, and internal controls across the organization."
            ),
        },
        {
            "external_id": "finance-trainee",
            "title": "Finance Officer",
            "company": "Example Microfinance",
            "location": "Addis Ababa",
            "description": (
                "Provide customer support, process new account applications, maintain client "
                "records, answer inquiries, and coordinate branch service schedules."
            ),
        },
    ])

    assert db_session.query(ExternalJob).count() == 2


def test_fetch_jobs_hides_stored_cross_source_duplicates(db_session):
    deadline = datetime.utcnow() + timedelta(days=5)
    description = (
        "Responsible for managing financial reports, budgets, reconciliations, monthly closes, "
        "regulatory filings, audit support, and internal controls across the organization."
    )
    db_session.add_all([
        ExternalJob(
            external_id="stored-telegram-copy",
            title="Finance Officer",
            company="Example Microfinance",
            location="Addis Ababa",
            description=description,
            source="Telegram",
            apply_url="https://t.me/jobs/102",
            deadline=deadline,
            is_active=True,
        ),
        ExternalJob(
            external_id="stored-website-copy",
            title="Job Vacancy: Finance Officer",
            company="Example Microfinance",
            location="Addis Ababa, Ethiopia",
            description=description,
            source="Ethiojobs",
            apply_url="https://careers.example.com/finance-officer",
            deadline=deadline,
            is_active=True,
        ),
    ])
    db_session.commit()

    jobs = ExternalJobService(db_session).fetch_jobs()

    assert len(jobs) == 1
    assert jobs[0].apply_url == "https://careers.example.com/finance-officer"


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


def test_backfill_reclassifies_existing_incorrect_fields(db_session):
    db_session.add(ExternalJob(
        external_id="stale-field-classification",
        title="Assistant Registrar Head for TVET Program",
        company="Example College",
        description="Manages student academic records and supports registration.",
        skills='["education", "it, computer science and software engineering"]',
        field="computer_it",
    ))
    db_session.commit()

    assert backfill_job_fields(db_session) == 1
    assert db_session.query(ExternalJob).filter_by(
        external_id="stale-field-classification"
    ).one().field == "education"
    assert backfill_job_fields(db_session) == 0
