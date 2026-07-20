"""Integration tests for Flask auth API endpoints — strict black-box, AAA pattern.

Each test exercises the full HTTP request/response cycle through the Flask
test client, with the service layer mocked to avoid database dependencies.
"""

import pytest
from unittest.mock import patch

from app import create_app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def client():
    """Yield a Flask test client with testing mode enabled."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Test 1: POST /api/signup — successful registration (201)
# ---------------------------------------------------------------------------
@patch("services.auth_service.create_session")
@patch("services.auth_service.create_user")
@patch("services.auth_service.bcrypt")
@patch("services.auth_service.get_user_by_email")
def test_signup_returns_201(mock_get_user, mock_bcrypt, mock_create_user, mock_create_session, client):
    # Arrange
    mock_get_user.return_value = None
    mock_bcrypt.hashpw.return_value = b"hashed_password"
    mock_bcrypt.gensalt.return_value = b"salt"
    mock_create_user.return_value = 1
    mock_create_session.return_value = "mock_session_id"

    payload = {
        "name": "IntUser",
        "email": "int@test.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/signup", json=payload)

    # Assert
    assert response.status_code == 201


# ---------------------------------------------------------------------------
# Test 2: POST /api/login — successful login (200)
# ---------------------------------------------------------------------------
@patch("services.auth_service.create_session")
@patch("services.auth_service.delete_user_sessions")
@patch("services.auth_service.bcrypt")
@patch("services.auth_service.get_user_by_email")
def test_login_returns_200(mock_get_user, mock_bcrypt, mock_delete_sessions, mock_create_session, client):
    # Arrange
    mock_get_user.return_value = {
        "id": 1,
        "name": "IntUser",
        "email": "int@test.com",
        "password_hash": "hashed_pass",
    }
    mock_bcrypt.checkpw.return_value = True
    mock_delete_sessions.return_value = None
    mock_create_session.return_value = "mock_session_id"

    payload = {
        "email": "int@test.com",
        "password": "password123",
    }

    # Act
    response = client.post("/api/login", json=payload)

    # Assert
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Test 3: POST /api/logout — successful logout (200)
# ---------------------------------------------------------------------------
@patch("services.auth_service.delete_session")
def test_logout_returns_200(mock_delete_session, client):
    # Arrange
    mock_delete_session.return_value = None

    # Act
    response = client.post("/api/logout")

    # Assert
    assert response.status_code == 200
