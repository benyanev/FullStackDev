"""Unit tests for services.admin_service — strict black-box, AAA pattern.

Repositories are mocked so the service runs in isolation.
"""

import pytest
from unittest.mock import patch

from core.exceptions import NotFoundError, ValidationError
from services import admin_service


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------
@patch("services.admin_service.update_report_status")
def test_update_report_dismiss(mock_update):
    # Arrange
    mock_update.return_value = True

    # Act
    admin_service.update_report(5, "dismissed")

    # Assert
    mock_update.assert_called_once_with(5, "dismissed")


def test_update_report_invalid_status():
    # Act & Assert
    with pytest.raises(ValidationError):
        admin_service.update_report(5, "pending")


@patch("services.admin_service.update_report_status")
def test_update_report_not_found(mock_update):
    # Arrange
    mock_update.return_value = False

    # Act & Assert
    with pytest.raises(NotFoundError):
        admin_service.update_report(999, "resolved")


# ---------------------------------------------------------------------------
# Delete post
# ---------------------------------------------------------------------------
@patch("services.admin_service.repo_delete_post")
def test_delete_post_success(mock_delete):
    # Arrange
    mock_delete.return_value = True

    # Act
    admin_service.delete_post(1)

    # Assert
    mock_delete.assert_called_once_with(1)


@patch("services.admin_service.repo_delete_post")
def test_delete_post_not_found(mock_delete):
    # Arrange
    mock_delete.return_value = False

    # Act & Assert
    with pytest.raises(NotFoundError):
        admin_service.delete_post(999)


# ---------------------------------------------------------------------------
# Ban
# ---------------------------------------------------------------------------
@patch("services.admin_service.delete_user_sessions")
@patch("services.admin_service.set_user_banned")
@patch("services.admin_service.get_user_by_id")
def test_ban_user_logs_them_out(mock_get_user, mock_set_banned, mock_delete_sessions):
    # Arrange
    mock_get_user.return_value = {"id": 7}

    # Act
    admin_service.set_ban(admin_id=1, user_id=7, banned=True)

    # Assert
    mock_set_banned.assert_called_once_with(7, True)
    mock_delete_sessions.assert_called_once_with(7)


@patch("services.admin_service.delete_user_sessions")
@patch("services.admin_service.set_user_banned")
@patch("services.admin_service.get_user_by_id")
def test_unban_user_keeps_sessions(mock_get_user, mock_set_banned, mock_delete_sessions):
    # Arrange
    mock_get_user.return_value = {"id": 7}

    # Act
    admin_service.set_ban(admin_id=1, user_id=7, banned=False)

    # Assert
    mock_set_banned.assert_called_once_with(7, False)
    mock_delete_sessions.assert_not_called()


def test_ban_self_rejected():
    # Act & Assert
    with pytest.raises(ValidationError):
        admin_service.set_ban(admin_id=1, user_id=1, banned=True)


@patch("services.admin_service.get_user_by_id")
def test_ban_unknown_user(mock_get_user):
    # Arrange
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        admin_service.set_ban(admin_id=1, user_id=999, banned=True)


# ---------------------------------------------------------------------------
# Role
# ---------------------------------------------------------------------------
@patch("services.admin_service.set_user_role")
@patch("services.admin_service.get_user_by_id")
def test_set_role_promotes_user(mock_get_user, mock_set_role):
    # Arrange
    mock_get_user.return_value = {"id": 7}

    # Act
    admin_service.set_role(admin_id=1, user_id=7, role="admin")

    # Assert
    mock_set_role.assert_called_once_with(7, "admin")


def test_set_role_invalid_role():
    # Act & Assert
    with pytest.raises(ValidationError):
        admin_service.set_role(admin_id=1, user_id=7, role="superuser")


def test_set_role_self_rejected():
    # Act & Assert
    with pytest.raises(ValidationError):
        admin_service.set_role(admin_id=1, user_id=1, role="user")
