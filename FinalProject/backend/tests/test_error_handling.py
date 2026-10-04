"""Bad or unexpected requests get clear JSON errors instead of crashes — AAA."""

from datetime import datetime
from unittest.mock import patch

import pytest

from app import create_app

VALID_SESSION = {"user_id": 1, "expires_at": datetime(2099, 1, 1), "is_banned": 0}


@pytest.fixture()
def client():
    app = create_app()
    with app.test_client() as test_client:
        test_client.set_cookie("session_id", "mock_session")
        yield test_client


@pytest.mark.parametrize("body", ["null", "[1]", "5", "not json"])
@pytest.mark.parametrize("path", ["/api/login", "/api/signup", "/api/reset-request"])
def test_non_object_body_returns_400(client, path, body):
    # Act
    response = client.post(path, data=body, content_type="application/json")

    # Assert — a validation error, not a 500
    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("middlewares.auth_middleware.get_session", return_value=VALID_SESSION)
def test_wrong_types_on_logged_in_endpoints_return_400(mock_session, client):
    # Act
    post = client.post("/api/posts", json={"title": 5, "body": ["x"]})
    comment = client.post("/api/posts/1/comments", data="null", content_type="application/json")
    profile = client.put("/api/users/1/profile", json={"name": 5})

    # Assert
    assert [post.status_code, comment.status_code, profile.status_code] == [400, 400, 400]


@patch("services.post_service.get_posts_paginated", return_value=[])
def test_pagination_is_clamped(mock_posts, client):
    # Act
    client.get("/api/posts?_start=-5&_limit=-1")
    client.get("/api/posts?_limit=100000")

    # Assert — (start, limit) passed to the DB are always safe
    assert mock_posts.call_args_list[0].args[:2] == (0, 1)
    assert mock_posts.call_args_list[1].args[:2] == (0, 50)


def test_unknown_url_returns_json_404(client):
    # Act
    response = client.get("/api/does-not-exist")

    # Assert
    assert response.status_code == 404
    assert "error" in response.get_json()


@patch("services.post_service.get_posts_paginated", side_effect=RuntimeError("DB down"))
def test_unexpected_error_returns_json_500_without_details(mock_posts, client):
    # Act
    response = client.get("/api/posts")

    # Assert — generic message, no internal details leaked
    assert response.status_code == 500
    assert "DB down" not in response.get_json()["error"]


# ---------------------------------------------------------------------------
# Sessions: banned users and the optional "who am I" on public endpoints
# ---------------------------------------------------------------------------
@patch("middlewares.auth_middleware.delete_session")
@patch("middlewares.auth_middleware.get_session",
       return_value={**VALID_SESSION, "is_banned": 1})
def test_banned_user_is_stopped_on_next_request(mock_session, mock_delete, client):
    # Act
    response = client.post("/api/posts/1/like")

    # Assert — rejected and logged out
    assert response.status_code == 403
    mock_delete.assert_called_once_with("mock_session")


@patch("services.like_service.has_user_liked", return_value=True)
@patch("services.like_service.get_like_count", return_value=3)
@patch("services.like_service.get_post_by_id", return_value={"id": 1})
@patch("middlewares.auth_middleware.get_session", return_value=VALID_SESSION)
def test_likes_show_my_liked_state_when_logged_in(mock_session, mock_post, mock_count,
                                                  mock_liked, client):
    # Act — public route, but the viewer is logged in
    response = client.get("/api/posts/1/likes")

    # Assert — the red heart survives a page refresh
    assert response.get_json() == {"liked": True, "likeCount": 3}
    mock_liked.assert_called_once_with(1, 1)


@patch("services.like_service.get_like_count", return_value=3)
@patch("services.like_service.get_post_by_id", return_value={"id": 1})
def test_likes_for_visitors(mock_post, mock_count):
    # Act — no cookie at all
    response = create_app().test_client().get("/api/posts/1/likes")

    # Assert
    assert response.get_json() == {"liked": False, "likeCount": 3}
