"""Integration tests for the AI Assist API endpoints — AAA pattern.

Full HTTP cycle through the Flask test client; the OpenAI call
(``ai_service._chat``) and repositories are mocked.
"""

import json
from datetime import datetime
from unittest.mock import patch

import pytest

from app import create_app

VALID_SESSION = {"user_id": 1, "expires_at": datetime(2099, 1, 1)}


@pytest.fixture()
def client():
    """Yield a logged-in Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        test_client.set_cookie("session_id", "mock_session")
        yield test_client


@patch("services.ai_service._chat")
@patch("middlewares.auth_middleware.get_session")
def test_autocorrect_returns_200(mock_session, mock_chat, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_chat.return_value = "This is correct."

    # Act
    response = client.post("/api/ai/autocorrect", json={"text": "This are corect."})

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"text": "This is correct."}


@patch("services.ai_service._chat")
@patch("middlewares.auth_middleware.get_session")
def test_suggest_post_returns_200(mock_session, mock_chat, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_chat.return_value = json.dumps({"title": "Coffee", "body": "<p>Yum</p>"})

    # Act
    response = client.post("/api/ai/suggest-post", json={"topic": "coffee"})

    # Assert
    assert response.status_code == 200
    assert response.get_json()["title"] == "Coffee"


@patch("services.ai_service._chat")
@patch("services.ai_service.get_comments_by_post")
@patch("services.ai_service.get_post_by_id")
@patch("middlewares.auth_middleware.get_session")
def test_suggest_comment_returns_200(mock_session, mock_get_post, mock_comments,
                                     mock_chat, client):
    # Arrange
    mock_session.return_value = VALID_SESSION
    mock_get_post.return_value = {"id": 1, "title": "T", "body": "B"}
    mock_comments.return_value = []
    mock_chat.return_value = "Great post!"

    # Act
    response = client.post("/api/ai/suggest-comment", json={"post_id": 1})

    # Assert
    assert response.status_code == 200
    assert response.get_json() == {"text": "Great post!"}


@patch("middlewares.auth_middleware.get_session")
def test_suggest_comment_missing_post_id_returns_400(mock_session, client):
    # Arrange
    mock_session.return_value = VALID_SESSION

    # Act
    response = client.post("/api/ai/suggest-comment", json={})

    # Assert
    assert response.status_code == 400


@patch("middlewares.auth_middleware.get_session")
def test_ai_unconfigured_returns_503(mock_session, client):
    # Arrange — conftest blanks OPENAI_API_KEY
    mock_session.return_value = VALID_SESSION

    # Act
    response = client.post("/api/ai/autocorrect", json={"text": "hello"})

    # Assert
    assert response.status_code == 503


def test_ai_requires_auth():
    # Arrange — a client with no session cookie
    app = create_app()
    app.config["TESTING"] = True

    # Act
    response = app.test_client().post("/api/ai/suggest-post", json={"topic": "x"})

    # Assert
    assert response.status_code == 401
