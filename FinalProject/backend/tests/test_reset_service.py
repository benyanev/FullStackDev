"""Unit tests for services.reset_service — strict black-box, AAA pattern.

Every external dependency (repositories, bcrypt, email) is mocked so
that the unit under test runs in complete isolation.
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from core.exceptions import NotFoundError, ValidationError
from services.reset_service import request_reset, confirm_reset


# ---------------------------------------------------------------------------
# request_reset tests
# ---------------------------------------------------------------------------

@patch("services.reset_service.send_email")
@patch("services.reset_service.create_reset_token")
@patch("services.reset_service.invalidate_user_tokens")
@patch("services.reset_service.get_user_by_email")
def test_request_reset_success(mock_get_user, mock_invalidate,
                                mock_create_token, mock_send_email):
    """Test 1: Successful reset request sends an email."""
    # Arrange
    mock_get_user.return_value = {"id": 1, "name": "Alice", "email": "alice@test.com"}
    mock_create_token.return_value = 1

    # Act
    result = request_reset("alice@test.com")

    # Assert
    assert result is True
    mock_invalidate.assert_called_once_with(1)
    mock_create_token.assert_called_once()
    mock_send_email.assert_called_once()


@patch("services.reset_service.get_user_by_email")
def test_request_reset_unknown_email(mock_get_user):
    """Test 2: Unknown email silently succeeds (no user enumeration)."""
    # Arrange
    mock_get_user.return_value = None

    # Act
    result = request_reset("unknown@test.com")

    # Assert — returns True without raising
    assert result is True


def test_request_reset_empty_email():
    """Test 3: Empty email raises ValidationError."""
    with pytest.raises(ValidationError):
        request_reset("")


# ---------------------------------------------------------------------------
# confirm_reset tests
# ---------------------------------------------------------------------------

@patch("services.reset_service.delete_user_sessions")
@patch("services.reset_service.mark_token_used")
@patch("services.reset_service.update_password_hash")
@patch("services.reset_service.bcrypt")
@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_success(mock_get_reset, mock_bcrypt,
                                mock_update_pw, mock_mark_used, mock_logout_all):
    """Test 4: Successful reset updates password and marks token used."""
    # Arrange
    future = datetime.now(timezone.utc) + timedelta(hours=1)
    mock_get_reset.return_value = {
        "id": 1, "user_id": 10, "token": "abc123",
        "expires_at": future, "used": 0,
    }
    mock_bcrypt.hashpw.return_value = b"new_hashed_password"
    mock_bcrypt.gensalt.return_value = b"salt"

    # Act
    result = confirm_reset("abc123", "newpass123")

    # Assert
    assert result is True
    mock_update_pw.assert_called_once_with(10, "new_hashed_password")
    mock_mark_used.assert_called_once_with("abc123")
    # every device is logged out after a password reset
    mock_logout_all.assert_called_once_with(10)


@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_invalid_token(mock_get_reset):
    """Test 5: Invalid token raises NotFoundError."""
    # Arrange
    mock_get_reset.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        confirm_reset("bad_token", "newpass123")


@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_already_used(mock_get_reset):
    """Test 6: Already-used token raises ValidationError."""
    # Arrange
    mock_get_reset.return_value = {
        "id": 1, "user_id": 10, "token": "abc123",
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
        "used": 1,
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        confirm_reset("abc123", "newpass123")


@patch("services.reset_service.mark_token_used")
@patch("services.reset_service.get_reset_by_token")
def test_confirm_reset_expired_token(mock_get_reset, mock_mark_used):
    """Test 7: Expired token raises ValidationError."""
    # Arrange
    past = datetime.now(timezone.utc) - timedelta(hours=2)
    mock_get_reset.return_value = {
        "id": 1, "user_id": 10, "token": "abc123",
        "expires_at": past, "used": 0,
    }

    # Act & Assert
    with pytest.raises(ValidationError):
        confirm_reset("abc123", "newpass123")
    mock_mark_used.assert_called_once_with("abc123")


def test_confirm_reset_empty_token():
    """Test 8: Empty token raises ValidationError."""
    with pytest.raises(ValidationError):
        confirm_reset("", "newpass123")


def test_confirm_reset_short_password():
    """Test 9: Short password raises ValidationError."""
    with pytest.raises(ValidationError):
        confirm_reset("abc123", "short")
