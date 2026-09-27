import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.config.database import SessionLocal
from app.models.user import User
from app.services.field_classifier import (
    classify_cv,
    classify_job,
    field_matches,
    normalize_department,
)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    from app.routes.auth import register_limiter, login_limiter
    register_limiter.reset()
    login_limiter.reset()
    yield


def test_classify_job_computer():
    assert classify_job("Senior Software Developer", "", '["python", "django", "sql"]') == "computer_it"
    assert classify_job("IT Officer", "network and hardware support") == "computer_it"
    assert classify_job("Data Scientist", "", '["machine learning", "python"]') == "computer_it"


def test_classify_job_other_fields():
    assert classify_job("Registered Nurse", "hospital patient care") == "health"
    assert classify_job("Site Engineer", "construction supervision") == "engineering"
    assert classify_job("Accountant", "", '["auditing", "tax"]') == "business_finance"
    assert classify_job("Grade 5 Teacher", "school curriculum delivery") == "education"


def test_normalize_department():
    assert normalize_department("Computer Science") == "computer_it"
    assert normalize_department("Software Engineering") == "computer_it"
    assert normalize_department("Computer Engineering") == "computer_it"
    assert normalize_department("Electrical Engineering") == "engineering"
    assert normalize_department("Civil Engineering") == "engineering"
    assert normalize_department("Mechanical Engineering") == "engineering"
    assert normalize_department("Nursing") == "health"
    assert normalize_department("Accounting and Finance") == "business_finance"
    assert normalize_department("Law") == "law"
    assert normalize_department("") is None
    assert normalize_department(None) is None


def test_field_matches():
    assert field_matches("computer_it", "computer_it") is True
    assert field_matches("health", "computer_it") is False
    # unknown job field or no department -> keep
    assert field_matches(None, "computer_it") is True
    assert field_matches("other", "computer_it") is True
    assert field_matches("health", None) is True


def test_field_matches_strict_excludes_generic():
    # Strict (personalized feed): generic 'other' jobs are dropped for a known field
    assert field_matches("other", "computer_it", strict=True) is False
    assert field_matches(None, "computer_it", strict=True) is False
    assert field_matches("computer_it", "computer_it", strict=True) is True
    assert field_matches("health", "computer_it", strict=True) is False
    # No detected field -> still see everything, even in strict mode
    assert field_matches("other", None, strict=True) is True
    assert field_matches("health", "other", strict=True) is True


def test_classify_cv_from_education_and_skills():
    # No manual department: the field comes from the CV itself
    assert classify_cv(
        "BSc in Computer Science graduate seeking software role",
        '["python", "django", "sql"]',
        '[{"degree": "BSc", "field": "Computer Science"}]',
    ) == "computer_it"
    assert classify_cv(
        "Registered nurse with 3 years hospital experience",
        '["patient care", "clinical"]',
        '["BSc Nursing"]',
    ) == "health"
    assert classify_cv(
        "Accounting and finance graduate",
        '["auditing", "tax"]',
        '["BA Accounting and Finance"]',
    ) == "business_finance"
    # "Computer Engineering" must land in computer_it, not generic engineering
    assert classify_cv(
        "Computer Engineering graduate",
        '["c++", "embedded systems"]',
        '["BSc Computer Engineering"]',
    ) == "computer_it"
    # ...while other engineering disciplines stay in engineering
    assert classify_cv(
        "Civil Engineering graduate",
        '["autocad", "structural analysis"]',
        '["BSc Civil Engineering"]',
    ) == "engineering"


@pytest.fixture()
def dept_user():
    db = SessionLocal()
    db.query(User).filter(User.email == "deptuser@example.com").delete()
    db.commit()
    db.close()
    response = client.post(
        "/api/auth/register",
        json={
            "email": "deptuser@example.com",
            "username": "deptuser",
            "password": "TestPass123",
            "full_name": "Dept User",
            "is_seeker": True,
            "department": "Computer Science",
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["department"] == "Computer Science"
    token = client.post(
        "/api/auth/login",
        data={"username": "deptuser@example.com", "password": "TestPass123"},
    ).json()["access_token"]
    yield token
    db = SessionLocal()
    db.query(User).filter(User.email == "deptuser@example.com").delete()
    db.commit()
    db.close()


def test_jobs_field_filter():
    response = client.get("/api/jobs/?field=computer_it&limit=100")
    assert response.status_code == 200
    jobs = response.json()
    for job in jobs:
        assert job["field"] in ("computer_it", "other", None)


def test_jobs_invalid_field():
    response = client.get("/api/jobs/?field=underwater_basket_weaving")
    assert response.status_code == 400


def test_recommended_requires_auth():
    assert client.get("/api/jobs/recommended").status_code == 401


def test_recommended_for_computer_department(dept_user):
    response = client.get(
        "/api/jobs/recommended",
        headers={"Authorization": f"Bearer {dept_user}"},
    )
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) > 0
    for job in jobs:
        # only computer/IT or cross-field 'other' jobs
        assert job["field"] in ("computer_it", "other", None)
    # computer_it jobs are ranked before cross-field 'other' jobs
    seen_other = False
    for job in jobs:
        if job["field"] in ("other", None):
            seen_other = True
        else:
            assert not seen_other, "computer_it job ranked after an 'other' job"


def test_matching_respects_department(dept_user):
    """Matches created for a department user never point at a different-field job."""
    from app.models.cv import CV
    from app.models.match import Match
    from app.models.job import ExternalJob
    from app.services.matching_service import MatchingService

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "deptuser@example.com").first()
        cv = CV(
            user_id=user.id,
            title="Test CV",
            file_path="/tmp/x.pdf",
            file_name="x.pdf",
            parsed_text="python developer with sql and django experience",
            skills='["python", "sql", "django"]',
        )
        db.add(cv)
        db.commit()
        db.refresh(cv)

        MatchingService(db).find_matches_for_cv(user.id, cv.id)

        matches = db.query(Match).filter(Match.user_id == user.id, Match.cv_id == cv.id).all()
        assert matches, "expected at least one match"
        job_fields = {
            j.external_id: j.field
            for j in db.query(ExternalJob).filter(
                ExternalJob.external_id.in_([m.external_job_id for m in matches])
            ).all()
        }
        for match in matches:
            assert field_matches(job_fields.get(match.external_job_id), "computer_it")

        db.query(Match).filter(Match.cv_id == cv.id).delete()
        db.query(CV).filter(CV.id == cv.id).delete()
        db.commit()
    finally:
        db.close()


def test_matching_uses_cv_detected_field_without_department():
    """A user who never typed a department still gets field-filtered matches
    because the field is detected from the CV itself."""
    from app.models.cv import CV
    from app.models.match import Match
    from app.models.job import ExternalJob
    from app.services.field_classifier import classify_cv
    from app.services.matching_service import MatchingService

    db = SessionLocal()
    try:
        db.query(User).filter(User.email == "nodpt@example.com").delete()
        db.commit()
        user = User(
            email="nodpt@example.com",
            username="nodpt",
            hashed_password="x",
            full_name="No Department",
            is_seeker=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        assert user.department is None

        cv = CV(
            user_id=user.id,
            title="Auto CV",
            file_path="/tmp/y.pdf",
            file_name="y.pdf",
            parsed_text="BSc in Computer Science. Python developer with sql and django experience.",
            skills='["python", "sql", "django"]',
            education='[{"degree": "BSc", "field": "Computer Science"}]',
        )
        # Simulate what analyze_cv does automatically on upload
        cv.field = classify_cv(cv.parsed_text, cv.skills or "", cv.education or "")
        assert cv.field == "computer_it"
        db.add(cv)
        db.commit()
        db.refresh(cv)

        MatchingService(db).find_matches_for_cv(user.id, cv.id)

        matches = db.query(Match).filter(Match.user_id == user.id, Match.cv_id == cv.id).all()
        assert matches, "expected at least one match"
        job_fields = {
            j.external_id: j.field
            for j in db.query(ExternalJob).filter(
                ExternalJob.external_id.in_([m.external_job_id for m in matches])
            ).all()
        }
        for match in matches:
            assert field_matches(job_fields.get(match.external_job_id), "computer_it")

        db.query(Match).filter(Match.cv_id == cv.id).delete()
        db.query(CV).filter(CV.id == cv.id).delete()
        db.query(User).filter(User.id == user.id).delete()
        db.commit()
    finally:
        db.close()
