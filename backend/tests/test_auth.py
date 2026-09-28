import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app
from app.config.database import SessionLocal
from app.models.user import User
from app.routes.auth import register_limiter, login_limiter

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    register_limiter.reset()
    login_limiter.reset()
    yield


@pytest.fixture(scope="module", autouse=True)
def clean_test_user():
    # These tests hit the real dev DB; remove leftovers from previous runs so
    # registration succeeds on every run.
    db = SessionLocal()
    db.query(User).filter(User.email.in_(["test@example.com", "tguser@example.com"])).delete()
    db.commit()
    db.close()
    yield


def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123",
            "full_name": "Test User",
            "is_seeker": True
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"

def test_login_user():
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user():
    # First login to get token
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_register_duplicate_email():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "TestPass123"
        }
    )
    assert response.status_code == 400

def test_login_invalid_credentials():
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "WrongPassword"
        }
    )
    assert response.status_code == 401

def test_register_with_telegram_username_enables_notifications():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "tguser@example.com",
            "username": "tguser",
            "password": "TestPass123",
            "full_name": "Telegram User",
            "is_seeker": True,
            "telegram_username": "@john_doe"
        }
    )
    assert response.status_code == 200
    assert response.json()["telegram_username"] == "john_doe"

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "tguser@example.com").first()
        assert user.telegram_username == "john_doe"
        assert user.telegram_notifications_enabled is True
    finally:
        db.close()


def test_register_rate_limited():
    # Invalid bodies keep the DB untouched; the limiter dependency still runs
    # and counts each attempt (5/hour allowed).
    for _ in range(5):
        response = client.post("/api/auth/register", json={})
        assert response.status_code == 422

    response = client.post("/api/auth/register", json={})
    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_login_rate_limited():
    for _ in range(20):
        response = client.post(
            "/api/auth/login",
            data={"username": "nobody@example.com", "password": "WrongPassword"}
        )
        assert response.status_code == 401

    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@example.com", "password": "WrongPassword"}
    )
    assert response.status_code == 429


def test_mark_notification_as_read_not_found_returns_404():
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "TestPass123"
        }
    )
    token = login_response.json()["access_token"]

    response = client.put(
        "/api/notifications/99999/read",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"
