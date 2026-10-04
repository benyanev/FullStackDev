"""Integration tests for follow, user/profile, post-feed and upload endpoints — AAA.

Full HTTP cycle through the Flask test client (route → middleware →
controller → service); the repository layer is mocked.
"""

import io
from datetime import datetime
from unittest.mock import patch

import pytest

from app import create_app

VALID_SESSION = {"user_id": 1, "expires_at": datetime(2099, 1, 1)}
CREATED = datetime(2026, 1, 1)


@pytest.fixture()
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture()
def client(app):
    """A logged-in test client (get_session is patched per test)."""
    with app.test_client() as test_client:
        test_client.set_cookie("session_id", "mock_session")
        yield test_client


@pytest.fixture()
def logged_in():
    with patch("middlewares.auth_middleware.get_session", return_value=VALID_SESSION):
        yield


# ---------------------------------------------------------------------------
# Follows
# ---------------------------------------------------------------------------
@patch("services.follow_service.follow_user", return_value=True)
@patch("services.follow_service.get_user_by_id", return_value={"id": 2})
def test_follow_returns_200(mock_get_user, mock_follow, client, logged_in):
    # Act
    response = client.post("/api/users/2/follow")

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"message": "Followed.", "following": True}


def test_follow_yourself_returns_400(client, logged_in):
    # Act
    response = client.post("/api/users/1/follow")

    # Assert
    assert response.status_code == 400


@patch("services.follow_service.unfollow_user", return_value=True)
def test_unfollow_returns_200(mock_unfollow, client, logged_in):
    # Act
    response = client.delete("/api/users/2/follow")

    # Assert
    assert response.get_json() == {"message": "Unfollowed.", "following": False}


@patch("services.follow_service.get_followers",
       return_value=[{"id": 5, "name": "Eve", "created_at": CREATED}])
@patch("services.follow_service.get_user_by_id", return_value={"id": 2})
def test_followers_list_returns_200(mock_get_user, mock_followers, client):
    # Act
    response = client.get("/api/users/2/followers")

    # Assert
    data = response.get_json()
    assert data["count"] == 1
    assert data["users"][0]["created_at"] == "2026-01-01T00:00:00+00:00"


@patch("services.follow_service.get_following", return_value=[])
@patch("services.follow_service.get_user_by_id", return_value={"id": 2})
def test_following_list_returns_200(mock_get_user, mock_following, client):
    # Act
    response = client.get("/api/users/2/following")

    # Assert
    assert response.get_json() == {"count": 0, "users": []}


@pytest.mark.parametrize("path", ["/api/users/999/followers", "/api/users/999/following"])
@patch("services.follow_service.get_user_by_id", return_value=None)
def test_follow_lists_unknown_user_404(mock_get_user, path, client):
    # Act / Assert
    assert client.get(path).status_code == 404


@patch("services.follow_service.is_following", return_value=True)
def test_is_following_returns_200(mock_is_following, client, logged_in):
    # Act
    response = client.get("/api/users/2/is-following")

    # Assert
    assert response.get_json() == {"following": True}


# ---------------------------------------------------------------------------
# Users & profiles
# ---------------------------------------------------------------------------
@patch("services.user_service.get_following_count", return_value=0)
@patch("services.user_service.get_followers_count", return_value=0)
@patch("services.user_service.get_users_paginated",
       return_value=[{"id": 1, "name": "Ann", "created_at": CREATED}])
def test_get_users_returns_200(mock_users, mock_followers, mock_following, client):
    # Act
    response = client.get("/api/users?_start=0&_limit=5")

    # Assert
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Ann"
    mock_users.assert_called_once_with(0, 5)


@patch("services.user_service.get_following_count", return_value=1)
@patch("services.user_service.get_followers_count", return_value=2)
@patch("services.user_service.get_user_by_id",
       return_value={"id": 1, "name": "Ann", "created_at": CREATED})
def test_get_single_user_returns_200(mock_user, mock_followers, mock_following, client):
    # Act
    response = client.get("/api/users/1")

    # Assert
    assert response.get_json()["followers_count"] == 2


@patch("services.user_service.get_user_by_id", return_value=None)
def test_get_single_user_404(mock_user, client):
    # Act / Assert
    assert client.get("/api/users/999").status_code == 404


@patch("services.user_service.get_following_count", return_value=0)
@patch("services.user_service.get_followers_count", return_value=0)
@patch("services.user_service.get_user_by_id",
       return_value={"id": 1, "name": "New", "created_at": CREATED})
@patch("services.user_service.update_user_profile", return_value=True)
def test_update_own_profile_returns_200(mock_update, mock_user, mock_followers,
                                        mock_following, client, logged_in):
    # Act
    response = client.put("/api/users/1/profile", json={"name": "New", "bio": "Hi"})

    # Assert
    assert response.status_code == 200
    assert response.get_json()["user"]["name"] == "New"


def test_update_other_profile_returns_403(client, logged_in):
    # Act
    response = client.put("/api/users/2/profile", json={"name": "Hacker"})

    # Assert
    assert response.status_code == 403


# ---------------------------------------------------------------------------
# Post feeds & creation
# ---------------------------------------------------------------------------
@patch("services.post_service.get_posts_paginated",
       return_value=[{"id": 1, "title": "T", "created_at": CREATED}])
def test_global_feed_returns_200(mock_posts, client):
    # Act
    response = client.get("/api/posts?_start=10&_limit=5&userId=3")

    # Assert
    assert response.get_json()[0]["created_at"] == "2026-01-01T00:00:00+00:00"
    mock_posts.assert_called_once_with(10, 5, 3)


@patch("services.post_service.get_following_posts_paginated", return_value=[])
def test_following_feed_returns_200(mock_posts, client, logged_in):
    # Act
    response = client.get("/api/posts/following")

    # Assert
    assert response.status_code == 200
    mock_posts.assert_called_once_with(1, 0, 10)


def test_following_feed_requires_auth(app):
    # Act / Assert
    assert app.test_client().get("/api/posts/following").status_code == 401


@patch("services.post_service.repo_create_post", return_value=7)
def test_create_post_returns_201(mock_create, client, logged_in):
    # Act (conftest blanks the OpenAI key → moderation is skipped)
    response = client.post("/api/posts", json={"title": " T ", "body": "<p>B</p>"})

    # Assert
    assert response.status_code == 201
    assert response.get_json()["id"] == 7
    mock_create.assert_called_once_with(1, "T", "<p>B</p>", "", "")


def test_create_post_missing_body_returns_400(client, logged_in):
    # Act / Assert
    assert client.post("/api/posts", json={"title": "T"}).status_code == 400


# ---------------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("path, folder", [
    ("/api/upload/image", "posts"),
    ("/api/upload/profile-picture", "profiles"),
])
@patch("services.upload_service.upload_file")
def test_upload_returns_201(mock_upload, path, folder, client, logged_in):
    # Arrange
    mock_upload.return_value = f"/static/uploads/{folder}/a.png"

    # Act
    response = client.post(path, data={"file": (io.BytesIO(b"img"), "a.png")},
                           content_type="multipart/form-data")

    # Assert
    assert response.status_code == 201
    assert mock_upload.call_args[0][1] == folder


@patch("services.upload_service.upload_video", return_value="/static/uploads/videos/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp4")
def test_upload_video_returns_201(mock_upload, client, logged_in):
    # Act
    response = client.post("/api/upload/video",
                           data={"file": (io.BytesIO(b"vid"), "clip.mp4")},
                           content_type="multipart/form-data")

    # Assert
    assert response.status_code == 201
    assert response.get_json()["url"].endswith(".mp4")


@patch("services.post_service.repo_create_post", return_value=9)
def test_create_video_post_returns_201(mock_create, client, logged_in):
    # Act
    response = client.post("/api/posts", json={
        "title": "T", "body": "<p>B</p>", "video_url": "/static/uploads/videos/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp4"})

    # Assert
    assert response.status_code == 201
    mock_create.assert_called_once_with(1, "T", "<p>B</p>", "", "/static/uploads/videos/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp4")


def test_oversized_upload_returns_413(app, client, logged_in):
    # Arrange — shrink the limit so the test doesn't need 50 MB of data
    app.config["MAX_CONTENT_LENGTH"] = 10

    # Act
    response = client.post("/api/upload/video",
                           data={"file": (io.BytesIO(b"x" * 100), "clip.mp4")},
                           content_type="multipart/form-data")

    # Assert — JSON error the frontend can show
    assert response.status_code == 413
    assert "too large" in response.get_json()["error"]


@pytest.mark.parametrize("path", ["/api/upload/image", "/api/upload/profile-picture",
                                  "/api/upload/video"])
def test_upload_without_file_returns_400(path, client, logged_in):
    # Act / Assert
    assert client.post(path, data={}, content_type="multipart/form-data").status_code == 400
