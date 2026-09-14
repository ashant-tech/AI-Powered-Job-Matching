import pytest
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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
