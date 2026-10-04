"""Integration tests for password reset API endpoints — AAA pattern.

Each test exercises the full HTTP request/response cycle through the Flask
test client, with the service layer mocked to avoid database/email dependencies.
"""

import pytest
from datetime import datetime, timedelta, timezone
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
# POST /api/reset-request
# ---------------------------------------------------------------------------

@patch("services.reset_service.send_email")
@patch("services.reset_service.create_reset_token")
@patch("services.reset_service.invalidate_user_tokens")
@patch("services.reset_service.get_user_by_email")
def test_request_reset_returns_200(mock_get_user, mock_invalidate,
                                    mock_create, mock_send, client):
    """Test 1: Reset request always returns 200."""
    # Arrange
    mock_get_user.return_value = {"id": 1, "name": "Test", "email": "test@test.com"}
    mock_create.return_value = 1

    # Act
    response = client.post("/api/reset-request", json={"email": "test@test.com"})

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert "reset link" in data["message"].lower() or "sent" in data["message"].lower()


def test_request_reset_empty_email_returns_400(client):
    """Test 2: Empty email returns 400."""
    # Act
    response = client.post("/api/reset-request", json={"email": ""})

    # Assert
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/reset-confirm
# ---------------------------------------------------------------------------

@patch("services.reset_service.delete_user_sessions")
@patch("services.reset_service.mark_token_used")
@patch("services.reset_service.update_password_hash")
@patch("services.reset_service.bcrypt")
@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_returns_200(mock_get_reset, mock_bcrypt,
                                    mock_update_pw, mock_mark, mock_logout_all, client):
    """Test 3: Valid token and password returns 200."""
    # Arrange
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    mock_get_reset.return_value = {
        "id": 1, "user_id": 10, "token": "validtoken",
        "expires_at": future, "used": 0,
    }
    mock_bcrypt.hashpw.return_value = b"new_hash"
    mock_bcrypt.gensalt.return_value = b"salt"

    # Act
    response = client.post("/api/reset-confirm", json={
        "token": "validtoken",
        "password": "newpassword123",
    })

    # Assert
    assert response.status_code == 200


@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_invalid_token_returns_404(mock_get_reset, client):
    """Test 4: Invalid token returns 404."""
    # Arrange
    mock_get_reset.return_value = None

    # Act
    response = client.post("/api/reset-confirm", json={
        "token": "bad_token",
        "password": "newpassword123",
    })

    # Assert
    assert response.status_code == 404


def test_confirm_reset_short_password_returns_400(client):
    """Test 5: Short password returns 400."""
    # Act
    response = client.post("/api/reset-confirm", json={
        "token": "some_token",
        "password": "short",
    })

    # Assert
    assert response.status_code == 400
