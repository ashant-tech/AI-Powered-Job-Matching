import io
import pytest
from fastapi import UploadFile
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.cv import CV
from app.models.user import User
from app.schemas.cv import CVResponse
from app.services.cv_service import CVService


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