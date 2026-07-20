"""Unit tests for services.auth_service — strict black-box, AAA pattern.

Every external dependency (repositories, bcrypt) is mocked so that the
unit under test runs in complete isolation.
"""

import pytest
from unittest.mock import patch, MagicMock

from core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from services.auth_service import get_current_user, signup, login, logout


# ---------------------------------------------------------------------------
# Test 1: signup — successful registration
# ---------------------------------------------------------------------------
@patch("services.auth_service.create_session")
@patch("services.auth_service.create_user")
@patch("services.auth_service.bcrypt")
@patch("services.auth_service.get_user_by_email")
def test_signup_success(mock_get_user, mock_bcrypt, mock_create_user, mock_create_session):
    # Arrange
    name = "Alice"
    email = "alice@example.com"
    password = "securepass"

    mock_get_user.return_value = None
    mock_bcrypt.hashpw.return_value = b"hashed_password"
    mock_bcrypt.gensalt.return_value = b"salt"
    mock_create_user.return_value = 1
    mock_create_session.return_value = "mock_session_id"

    # Act
    result = signup(name, email, password)

    # Assert
    user_dict, session_id = result
    assert user_dict["id"] == 1
    assert user_dict["name"] == name
    assert user_dict["email"] == email
    assert session_id == "mock_session_id"


# ---------------------------------------------------------------------------
# Test 2: signup — password too short
# ---------------------------------------------------------------------------
def test_signup_password_too_short():
    # Arrange
    name = "Bob"
    email = "bob@example.com"
    password = "short"  # < 6 characters

    # Act & Assert
    with pytest.raises(ValidationError):
        signup(name, email, password)


# ---------------------------------------------------------------------------
# Test 3: signup — email already exists
# ---------------------------------------------------------------------------
@patch("services.auth_service.get_user_by_email")
def test_signup_email_already_exists(mock_get_user):
    # Arrange
    name = "Charlie"
    email = "charlie@example.com"
    password = "validpass"

    mock_get_user.return_value = {
        "id": 99,
        "name": "Existing User",
        "email": email,
        "password_hash": "some_hash",
    }

    # Act & Assert
    with pytest.raises(ConflictError):
        signup(name, email, password)


# ---------------------------------------------------------------------------
# Test 4: login — successful login
# ---------------------------------------------------------------------------
@patch("services.auth_service.create_session")
@patch("services.auth_service.delete_user_sessions")
@patch("services.auth_service.bcrypt")
@patch("services.auth_service.get_user_by_email")
def test_login_success(mock_get_user, mock_bcrypt, mock_delete_sessions, mock_create_session):
    # Arrange
    email = "test@test.com"
    password = "correctpass"

    mock_get_user.return_value = {
        "id": 1,
        "name": "Test",
        "email": "test@test.com",
        "password_hash": "hashed_pass",
    }
    mock_bcrypt.checkpw.return_value = True
    mock_delete_sessions.return_value = None
    mock_create_session.return_value = "new_session_id"

    # Act
    result = login(email, password)

    # Assert
    user_dict, session_id = result
    assert user_dict["id"] == 1
    assert user_dict["name"] == "Test"
    assert user_dict["email"] == email
    assert session_id == "new_session_id"
    mock_delete_sessions.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Test 5: login — invalid credentials (wrong password)
# ---------------------------------------------------------------------------
@patch("services.auth_service.bcrypt")
@patch("services.auth_service.get_user_by_email")
def test_login_wrong_password(mock_get_user, mock_bcrypt):
    # Arrange
    email = "test@test.com"
    password = "wrongpass"

    mock_get_user.return_value = {
        "id": 1,
        "name": "Test",
        "email": "test@test.com",
        "password_hash": "hashed_pass",
    }
    mock_bcrypt.checkpw.return_value = False

    # Act & Assert
    with pytest.raises(AuthenticationError):
        login(email, password)


# ---------------------------------------------------------------------------
# Test 6: logout — successful logout
# ---------------------------------------------------------------------------
@patch("services.auth_service.delete_session")
def test_logout_success(mock_delete_session):
    # Arrange
    session_id = "mock_session_id"

    # Act
    logout(session_id)

    # Assert
    mock_delete_session.assert_called_once_with("mock_session_id")


# ---------------------------------------------------------------------------
# Test 7: signup — missing fields
# ---------------------------------------------------------------------------
def test_signup_missing_fields():
    # Arrange
    name = ""
    email = "email@test.com"
    password = "pass"

    # Act & Assert
    with pytest.raises(ValidationError):
        signup(name, email, password)


# ---------------------------------------------------------------------------
# Test 8: login — user not found
# ---------------------------------------------------------------------------
@patch("services.auth_service.get_user_by_email")
def test_login_user_not_found(mock_get_user):
    # Arrange
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(AuthenticationError):
        login("unknown@test.com", "pass")


# ---------------------------------------------------------------------------
# Test 9: get_current_user — success
# ---------------------------------------------------------------------------
@patch("services.auth_service.get_user_by_id")
def test_get_current_user_success(mock_get_user_by_id):
    # Arrange
    expected_user = {"id": 1, "name": "Test", "email": "test@test.com"}
    mock_get_user_by_id.return_value = expected_user

    # Act
    result = get_current_user(1)

    # Assert
    assert result == expected_user
    mock_get_user_by_id.assert_called_once_with(1)


# ---------------------------------------------------------------------------
# Test 10: get_current_user — not found
# ---------------------------------------------------------------------------
@patch("services.auth_service.get_user_by_id")
def test_get_current_user_not_found(mock_get_user_by_id):
    # Arrange
    mock_get_user_by_id.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        get_current_user(99)
