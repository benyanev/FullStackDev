"""Integration tests for report and admin API endpoints — AAA pattern.

Each test exercises the full HTTP request/response cycle through the Flask
test client (routes → middleware → controller → service), with the
repository layer mocked to avoid database dependencies.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from app import create_app

VALID_SESSION = {"user_id": 1, "expires_at": datetime(2099, 1, 1)}
ADMIN_USER = {"id": 1, "name": "Admin", "role": "admin"}
NORMAL_USER = {"id": 1, "name": "Normal", "role": "user"}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture()
def client():
    """Yield a Flask test client with testing mode enabled."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        test_client.set_cookie("session_id", "mock_session")
        yield test_client


# ---------------------------------------------------------------------------
# POST /api/reports
# ---------------------------------------------------------------------------
@patch("services.report_service.repo_create_report")
@patch("services.report_service.get_post_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_create_report_returns_201(mock_session, mock_get_post, mock_create, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_post.return_value = {"id": 5, "author_id": 2}
    mock_create.return_value = True

    # Act
    response = client.post("/api/reports", json={"post_id": 5, "reason": "Spam"})

    # Assert
    assert response.status_code == 201
    mock_create.assert_called_once_with(1, 5, "Spam")


@patch("middlewares.auth_middleware.get_session")
def test_create_report_missing_post_id_returns_400(mock_session, client):
    # Arrange
    mock_session.return_value = VALID_SESSION

    # Act
    response = client.post("/api/reports", json={"reason": "Spam"})

    # Assert
    assert response.status_code == 400


def test_create_report_requires_auth():
    # Arrange — a client with no session cookie
    app = create_app()
    app.config["TESTING"] = True

    # Act
    response = app.test_client().post("/api/reports", json={"post_id": 5, "reason": "x"})

    # Assert
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# admin_required
# ---------------------------------------------------------------------------
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_admin_route_rejects_normal_user_403(mock_session, mock_get_user, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = NORMAL_USER

    # Act
    response = client.get("/api/admin/reports")

    # Assert
    assert response.status_code == 403


def test_admin_route_requires_login_401():
    # Arrange — a client with no session cookie
    app = create_app()
    app.config["TESTING"] = True

    # Act
    response = app.test_client().get("/api/admin/reports")

    # Assert
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Admin endpoints (logged in as admin)
# ---------------------------------------------------------------------------
@patch("services.admin_service.get_pending_reports")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_get_reports_returns_200(mock_session, mock_get_user, mock_reports, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = ADMIN_USER
    mock_reports.return_value = [
        {"id": 1, "post_id": 5, "reason": "Spam", "created_at": datetime(2026, 1, 1)},
    ]

    # Act
    response = client.get("/api/admin/reports")

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["reason"] == "Spam"
    assert data[0]["created_at"] == "2026-01-01T00:00:00+00:00"


@patch("services.admin_service.update_report_status")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_dismiss_report_returns_200(mock_session, mock_get_user, mock_update, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = ADMIN_USER
    mock_update.return_value = True

    # Act
    response = client.put("/api/admin/reports/3", json={"status": "dismissed"})

    # Assert
    assert response.status_code == 200
    mock_update.assert_called_once_with(3, "dismissed")


@patch("services.admin_service.repo_delete_post")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_delete_post_returns_200(mock_session, mock_get_user, mock_delete, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = ADMIN_USER
    mock_delete.return_value = True

    # Act
    response = client.delete("/api/admin/posts/5")

    # Assert
    assert response.status_code == 200
    mock_delete.assert_called_once_with(5)


@patch("services.admin_service.repo_delete_post")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_delete_missing_post_returns_404(mock_session, mock_get_user, mock_delete, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = ADMIN_USER
    mock_delete.return_value = False

    # Act
    response = client.delete("/api/admin/posts/999")

    # Assert
    assert response.status_code == 404


@patch("services.admin_service.get_users_paginated")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_get_admin_users_returns_200(mock_session, mock_get_user, mock_users, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_user.return_value = ADMIN_USER
    mock_users.return_value = [{"id": 7, "name": "Bob", "role": "user", "is_banned": 0}]

    # Act
    response = client.get("/api/admin/users")

    # Assert
    assert response.status_code == 200
    assert response.get_json()[0]["role"] == "user"


@patch("services.admin_service.delete_user_sessions")
@patch("services.admin_service.set_user_banned")
@patch("services.admin_service.get_user_by_id")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_ban_user_returns_200(mock_session, mock_auth_user, mock_get_user,
                              mock_set_banned, mock_delete_sessions, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_auth_user.return_value = ADMIN_USER
    mock_get_user.return_value = {"id": 7}

    # Act
    response = client.put("/api/admin/users/7/ban", json={"banned": True})

    # Assert
    assert response.status_code == 200
    mock_set_banned.assert_called_once_with(7, True)
    mock_delete_sessions.assert_called_once_with(7)


@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_ban_self_returns_400(mock_session, mock_auth_user, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_auth_user.return_value = ADMIN_USER

    # Act
    response = client.put("/api/admin/users/1/ban", json={"banned": True})

    # Assert
    assert response.status_code == 400


@patch("services.admin_service.set_user_role")
@patch("services.admin_service.get_user_by_id")
@patch("middlewares.auth_middleware.get_user_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_promote_user_returns_200(mock_session, mock_auth_user, mock_get_user,
                                  mock_set_role, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_auth_user.return_value = ADMIN_USER
    mock_get_user.return_value = {"id": 7}

    # Act
    response = client.put("/api/admin/users/7/role", json={"role": "admin"})

    # Assert
    assert response.status_code == 200
    mock_set_role.assert_called_once_with(7, "admin")
