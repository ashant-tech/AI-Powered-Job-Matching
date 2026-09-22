import io

from fastapi import UploadFile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.cv import CV
from app.models.user import User
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