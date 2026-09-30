import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.config.database import SessionLocal
from app.config.settings import settings
from app.models.user import User, PasswordResetToken
from app.routes.auth import forgot_limiter, reset_limiter

client = TestClient(app)

EMAIL = f"reset_flow_{int(time.time())}@example.com"
USERNAME = EMAIL.split('@')[0]


@pytest.fixture(autouse=True)
def _reset_limiters_and_expose_token(monkeypatch):
    forgot_limiter.reset()
    reset_limiter.reset()
    monkeypatch.setattr(settings, "EXPOSE_RESET_TOKEN", True)
    yield


@pytest.fixture(scope="module", autouse=True)
def _seed_user():
    db = SessionLocal()
    db.query(User).filter(User.email == EMAIL).delete()
    db.commit()
    db.close()

    resp = client.post("/api/auth/register", json={
        "email": EMAIL,
        "username": USERNAME,
        "password": "OldPass123",
        "full_name": "Reset Flow",
    })
    assert resp.status_code == 200
    yield

    db = SessionLocal()
    user = db.query(User).filter(User.email == EMAIL).first()
    if user:
        db.query(PasswordResetToken).filter(PasswordResetToken.user_id == user.id).delete()
        db.delete(user)
        db.commit()
    db.close()


def _get_token():
    resp = client.post("/api/auth/forgot-password", json={"email": EMAIL})
    assert resp.status_code == 200
    token = resp.json()["reset_token"]
    assert token
    return token


def test_forgot_password_returns_generic_detail_for_unknown_email():
    resp = client.post("/api/auth/forgot-password", json={"email": "nobody@nowhere.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["reset_token"] is None
    assert "If an account exists" in body["detail"]


def test_reset_password_short_password_rejected():
    token = _get_token()
    resp = client.post("/api/auth/reset-password", json={"token": token, "new_password": "abc"})
    assert resp.status_code == 400


def test_reset_password_invalid_token_rejected():
    resp = client.post("/api/auth/reset-password", json={"token": "garbage", "new_password": "NewPass456"})
    assert resp.status_code == 400


def test_full_reset_flow_and_token_single_use():
    token = _get_token()

    resp = client.post("/api/auth/reset-password", json={"token": token, "new_password": "NewPass456"})
    assert resp.status_code == 200

    # New password works, old password no longer does.
    assert client.post("/api/auth/login", data={"username": EMAIL, "password": "NewPass456"}).status_code == 200
    assert client.post("/api/auth/login", data={"username": EMAIL, "password": "OldPass123"}).status_code == 401

    # Reusing the same token fails.
    reuse = client.post("/api/auth/reset-password", json={"token": token, "new_password": "Another123"})
    assert reuse.status_code == 400

    # Restore the known password for any later tests in the module.
    fresh = _get_token()
    client.post("/api/auth/reset-password", json={"token": fresh, "new_password": "OldPass123"})
