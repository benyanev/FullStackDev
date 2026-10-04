"""Integration tests for like and comment API endpoints — AAA pattern.

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


def _auth_cookie(client):
    """Set a fake session cookie so auth_required passes."""
    client.set_cookie('session_id', 'mock_session')


# ---------------------------------------------------------------------------
# Like Integration Tests
# ---------------------------------------------------------------------------

@patch("services.like_service.get_like_count")
@patch("services.like_service.add_like")
@patch("services.like_service.has_user_liked")
@patch("services.like_service.get_post_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_toggle_like_returns_200(mock_session, mock_get_post, mock_has_liked,
                                  mock_add, mock_count, client):
    # Arrange
    mock_session.return_value = {"user_id": 1, "expires_at": __import__("datetime").datetime(2099, 1, 1)}
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_has_liked.return_value = False
    mock_count.return_value = 1
    _auth_cookie(client)

    # Act
    response = client.post("/api/posts/1/like")

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["liked"] is True
    assert data["likeCount"] == 1


@patch("services.like_service.get_like_count")
@patch("services.like_service.get_post_by_id")
def test_get_likes_returns_200(mock_get_post, mock_count, client):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_count.return_value = 5

    # Act
    response = client.get("/api/posts/1/likes")

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["likeCount"] == 5


def test_toggle_like_requires_auth(client):
    # Act — no session cookie
    response = client.post("/api/posts/1/like")

    # Assert
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Comment Integration Tests
# ---------------------------------------------------------------------------

@patch("services.comment_service.repo_create_comment")
@patch("services.comment_service.get_post_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_create_comment_returns_201(mock_session, mock_get_post,
                                     mock_create, client):
    # Arrange
    mock_session.return_value = {"user_id": 1, "expires_at": __import__("datetime").datetime(2099, 1, 1)}
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_create.return_value = 42
    _auth_cookie(client)

    payload = {"body": "Nice post!"}

    # Act
    response = client.post("/api/posts/1/comments", json=payload)

    # Assert
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 42


@patch("services.comment_service.get_comments_by_post")
@patch("services.comment_service.get_post_by_id")
def test_get_comments_returns_200(mock_get_post, mock_get_list, client):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_get_list.return_value = [
        {"id": 1, "body": "Hello", "authorName": "Alice",
         "created_at": "2025-01-01T00:00:00"},
    ]

    # Act
    response = client.get("/api/posts/1/comments")

    # Assert
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 1
    assert len(data["comments"]) == 1


@patch("services.comment_service.repo_create_comment")
@patch("services.comment_service.ensure_not_toxic")
@patch("services.comment_service.get_post_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_create_toxic_comment_returns_422(mock_session, mock_get_post,
                                          mock_moderate, mock_create, client):
    # Arrange
    from core.exceptions import ModerationError
    mock_session.return_value = {"user_id": 1, "expires_at": __import__("datetime").datetime(2099, 1, 1)}
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_moderate.side_effect = ModerationError("This looks offensive (harassment).")
    _auth_cookie(client)

    # Act
    response = client.post("/api/posts/1/comments", json={"body": "nasty"})

    # Assert
    assert response.status_code == 422
    assert "offensive" in response.get_json()["error"]
    mock_create.assert_not_called()


def test_create_comment_requires_auth(client):
    # Act — no session cookie
    response = client.post("/api/posts/1/comments", json={"body": "test"})

    # Assert
    assert response.status_code == 401
