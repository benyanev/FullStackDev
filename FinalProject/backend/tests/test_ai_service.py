"""Unit tests for services.ai_service — strict black-box, AAA pattern.

``_chat`` (the single OpenAI call) is mocked for the feature tests;
``urlopen`` is mocked for the ``_chat`` tests.  No real request is made.
"""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from core.exceptions import NotFoundError, ValidationError
from services import ai_service
from services.ai_service import AIUnavailableError


def _openai_reply(content):
    """Build a fake Chat Completions response body."""
    body = {"choices": [{"message": {"content": content}}]}
    return io.BytesIO(json.dumps(body).encode("utf-8"))


# ---------------------------------------------------------------------------
# _chat
# ---------------------------------------------------------------------------
@patch("services.ai_service.urllib.request.urlopen")
@patch("services.ai_service.OPENAI_API_KEY", "sk-test")
def test_chat_returns_reply_text(mock_urlopen):
    # Arrange
    mock_urlopen.return_value = _openai_reply("  Hello there  ")

    # Act
    result = ai_service._chat("system", "user", json_mode=True)

    # Assert
    assert result == "Hello there"
    sent = json.loads(mock_urlopen.call_args[0][0].data)
    assert sent["messages"][0] == {"role": "system", "content": "system"}
    assert sent["response_format"] == {"type": "json_object"}


def test_chat_without_key_raises_503():
    # Act & Assert (conftest blanks the key)
    with pytest.raises(AIUnavailableError) as exc:
        ai_service._chat("system", "user")
    assert exc.value.status_code == 503


@patch("services.ai_service.urllib.request.urlopen")
@patch("services.ai_service.OPENAI_API_KEY", "sk-test")
def test_chat_http_error_raises_503(mock_urlopen):
    # Arrange
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.openai.com", 429, "Too Many Requests", {},
        io.BytesIO(b'{"error": "rate limit"}'))

    # Act & Assert
    with pytest.raises(AIUnavailableError):
        ai_service._chat("system", "user")


@patch("services.ai_service.urllib.request.urlopen")
@patch("services.ai_service.OPENAI_API_KEY", "sk-test")
def test_chat_network_error_raises_503(mock_urlopen):
    # Arrange
    mock_urlopen.side_effect = urllib.error.URLError("timeout")

    # Act & Assert
    with pytest.raises(AIUnavailableError):
        ai_service._chat("system", "user")


# ---------------------------------------------------------------------------
# autocorrect
# ---------------------------------------------------------------------------
@patch("services.ai_service._chat")
def test_autocorrect_returns_fixed_text_without_fences(mock_chat):
    # Arrange
    mock_chat.return_value = "```html\n<p>This is correct.</p>\n```"

    # Act
    result = ai_service.autocorrect("<p>This are corect.</p>")

    # Assert
    assert result == "<p>This is correct.</p>"
    assert mock_chat.call_args[0][1] == "<p>This are corect.</p>"


@pytest.mark.parametrize("text", ["", "<p></p>"])
def test_autocorrect_empty_text(text):
    # Act & Assert
    with pytest.raises(ValidationError):
        ai_service.autocorrect(text)


def test_autocorrect_too_long():
    # Act & Assert
    with pytest.raises(ValidationError):
        ai_service.autocorrect("a" * 5001)


# ---------------------------------------------------------------------------
# suggest_post
# ---------------------------------------------------------------------------
@patch("services.ai_service._chat")
def test_suggest_post_returns_title_and_body(mock_chat):
    # Arrange
    mock_chat.return_value = json.dumps({"title": " Coffee ", "body": "<p>Love it</p>"})

    # Act
    result = ai_service.suggest_post("coffee")

    # Assert
    assert result == {"title": "Coffee", "body": "<p>Love it</p>"}
    assert mock_chat.call_args.kwargs["json_mode"] is True


@patch("services.ai_service._chat")
def test_suggest_post_bad_json_raises_503(mock_chat):
    # Arrange
    mock_chat.return_value = "not json"

    # Act & Assert
    with pytest.raises(AIUnavailableError):
        ai_service.suggest_post("coffee")


@pytest.mark.parametrize("topic", ["", "x" * 201])
def test_suggest_post_invalid_topic(topic):
    # Act & Assert
    with pytest.raises(ValidationError):
        ai_service.suggest_post(topic)


# ---------------------------------------------------------------------------
# suggest_comment
# ---------------------------------------------------------------------------
@patch("services.ai_service._chat")
@patch("services.ai_service.get_comments_by_post")
@patch("services.ai_service.get_post_by_id")
def test_suggest_comment_uses_post_and_comments(mock_get_post, mock_comments, mock_chat):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Trip to Rome", "body": "<p>Amazing food</p>"}
    mock_comments.return_value = [{"authorName": "Dana", "body": "Jealous!"}]
    mock_chat.return_value = '"Which restaurant was your favourite?"'

    # Act
    result = ai_service.suggest_comment(1)

    # Assert
    assert result == "Which restaurant was your favourite?"
    prompt = mock_chat.call_args[0][1]
    assert "Trip to Rome" in prompt and "Amazing food" in prompt
    assert "Dana: Jealous!" in prompt


@patch("services.ai_service.get_post_by_id")
def test_suggest_comment_post_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        ai_service.suggest_comment(999)


# ---------------------------------------------------------------------------
# Agent writers
# ---------------------------------------------------------------------------
AGENT = {"name": "Gary Grumble", "personality": "The Grumpy Skeptic: sarcastic."}


@patch("services.ai_service._chat")
def test_write_agent_post_in_character(mock_chat):
    # Arrange
    mock_chat.return_value = json.dumps({"title": "Hype", "body": "<p>Meh.</p>"})

    # Act
    result = ai_service.write_agent_post(AGENT, ["Old title"])

    # Assert
    assert result == {"title": "Hype", "body": "<p>Meh.</p>"}
    system_prompt, user_prompt = mock_chat.call_args[0]
    assert "Gary Grumble" in system_prompt and "Grumpy Skeptic" in system_prompt
    assert "Old title" in user_prompt


@patch("services.ai_service._chat")
def test_write_agent_post_bad_json_raises_503(mock_chat):
    # Arrange
    mock_chat.return_value = "oops"

    # Act & Assert
    with pytest.raises(AIUnavailableError):
        ai_service.write_agent_post(AGENT, [])


@patch("services.ai_service._chat")
def test_write_agent_comment_reads_discussion(mock_chat):
    # Arrange
    mock_chat.return_value = '"@Dana Prove it."'
    post = {"title": "AI is magic", "body": "<p>Wow</p>", "authorName": "Tessa"}
    comments = [{"authorName": "Dana", "body": "Totally agree"}]

    # Act
    result = ai_service.write_agent_comment(AGENT, post, comments)

    # Assert
    assert result == "@Dana Prove it."
    user_prompt = mock_chat.call_args[0][1]
    assert "Tessa posted" in user_prompt and "Dana: Totally agree" in user_prompt
