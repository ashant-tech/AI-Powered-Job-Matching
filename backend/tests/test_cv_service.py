import io
import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.cv import CV
from app.models.job import ExternalJob
from app.models.user import User
from app.schemas.cv import CVResponse
from app.services.cv_service import CVService
from app.services.matching_service import MatchingService
from app.schemas.cv import CVProfileUpdate


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


def test_upload_cv_replaces_existing_cv(db_session, monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.cv_service.settings.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(CVService, "_analyze_cv_async", lambda self, cv_id: None)
    user = User(email="cv@example.com", username="cvuser", hashed_password="hash", full_name="CV User")
    db_session.add(user)
    db_session.commit()

    service = CVService(db_session)
    first = service.upload_cv(user.id, UploadFile(io.BytesIO(b"first cv"), filename="first.txt"), "First CV")
    second = service.upload_cv(user.id, UploadFile(io.BytesIO(b"updated cv"), filename="updated.txt"), "Updated CV")

    assert second.id == first.id
    assert second.title == "Updated CV"
    assert second.parsed_text == "updated cv"
    assert db_session.query(CV).filter(CV.user_id == user.id).count() == 1


def test_upload_cv_succeeds_when_matching_fails_after_commit(db_session, monkeypatch, tmp_path):
    monkeypatch.setattr("app.services.cv_service.settings.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(CVService, "_analyze_cv_async", lambda self, cv_id: None)
    user = User(email="matching-error@example.com", username="matchingerror", hashed_password="hash", full_name="CV User")
    db_session.add(user)
    db_session.commit()

    def fail_matching(self, user_id, cv_id):
        duplicate = CV(
            user_id=user_id,
            title="Duplicate CV",
            file_path="duplicate.docx",
            file_name="duplicate.docx",
        )
        self.db.add(duplicate)
        with pytest.raises(IntegrityError):
            self.db.commit()
        raise RuntimeError("matching failed after database error")

    monkeypatch.setattr("app.services.cv_service.MatchingService.find_matches_for_cv", fail_matching)

    uploaded = CVService(db_session).upload_cv(
        user.id,
        UploadFile(io.BytesIO(b"valid cv text"), filename="cv.txt"),
        "My CV",
    )

    assert uploaded.id is not None
    assert uploaded.title == "My CV"
    assert CVResponse.model_validate(uploaded).id == uploaded.id
    assert db_session.query(CV).filter(CV.user_id == user.id).count() == 1


def test_find_matches_rejects_another_users_cv(db_session):
    owner = User(email="owner@example.com", username="owner", hashed_password="hash")
    other_user = User(email="other@example.com", username="other", hashed_password="hash")
    db_session.add_all([owner, other_user])
    db_session.commit()
    cv = CV(
        user_id=owner.id,
        title="Private CV",
        file_path="private.pdf",
        file_name="private.pdf",
        parsed_text="Software engineer with Python experience.",
    )
    db_session.add(cv)
    db_session.commit()

    with pytest.raises(ValueError, match="CV not found"):
        MatchingService(db_session).find_matches_for_cv(other_user.id, cv.id)


def test_update_matching_profile_saves_user_corrected_cv_signals(db_session):
    user = User(email="profile@example.com", username="profile", hashed_password="hash")
    db_session.add(user)
    db_session.commit()
    cv = CV(
        user_id=user.id,
        title="My CV",
        file_path="cv.pdf",
        file_name="cv.pdf",
        skills='["Python"]',
    )
    db_session.add(cv)
    db_session.commit()

    updated = CVService(db_session).update_matching_profile(
        user.id,
        cv.id,
        CVProfileUpdate(
            skills=[" Python ", "python", "SQL"],
            field="computer_it",
            experience_level="Mid-Level",
            total_years_experience=4,
        ),
    )

    assert updated.skills == '["Python", "SQL"]'
    assert updated.field == "computer_it"
    assert updated.experience_level == "Mid-Level"
    assert updated.total_years_experience == 4


def test_update_matching_profile_rejects_unknown_cv_field(db_session):
    user = User(email="profile-field@example.com", username="profilefield", hashed_password="hash")
    db_session.add(user)
    db_session.commit()
    cv = CV(user_id=user.id, title="My CV", file_path="cv.pdf", file_name="cv.pdf")
    db_session.add(cv)
    db_session.commit()

    with pytest.raises(ValueError, match="Invalid CV field"):
        CVService(db_session).update_matching_profile(
            user.id,
            cv.id,
            CVProfileUpdate(field="not_a_real_field"),
        )


def test_match_response_includes_fit_evidence_and_job_requirements(db_session, monkeypatch):
    user = User(email="matches@example.com", username="matches", hashed_password="hash")
    db_session.add(user)
    db_session.commit()
    cv = CV(
        user_id=user.id,
        title="Software CV",
        file_path="cv.pdf",
        file_name="cv.pdf",
        parsed_text="Software developer with Python and SQL experience building APIs.",
        skills='["python", "sql"]',
        field="computer_it",
        job_titles='["Software Developer"]',
    )
    db_session.add(cv)
    db_session.commit()
    job = ExternalJob(
        external_id="python-role",
        title="Python Developer",
        company="Example Co",
        description="Build software APIs with Python and SQL.",
        requirements="Python and SQL experience.",
        skills='["python", "sql"]',
        field="computer_it",
        apply_url="https://example.com/jobs/python",
    )

    class ExternalJobs:
        def fetch_jobs(self):
            return [job]

    monkeypatch.setattr("app.services.matching_service.ExternalJobService", lambda db: ExternalJobs())
    monkeypatch.setattr(
        "app.services.matching_service.NotificationService.send_match_notification",
        lambda *args, **kwargs: None,
    )

    matches = MatchingService(db_session).find_matches_for_cv(user.id, cv.id)

    assert len(matches) == 1
    assert matches[0].fit_level in {"Strong", "Good", "Possible"}
    assert matches[0].score_confidence is not None
    assert matches[0].component_scores["skill"] == 1.0
    assert matches[0].job.requirements == "Python and SQL experience."