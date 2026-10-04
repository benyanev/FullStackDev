"""Unit tests for services.sentiment_service — strict black-box, AAA pattern.

urllib's ``urlopen`` is mocked so no real OpenAI request is made.
"""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from core.exceptions import ModerationError
from services.sentiment_service import ensure_not_toxic


def _openai_response(flagged, categories=None):
    """Build a fake Moderation API response body."""
    body = {"results": [{"flagged": flagged, "categories": categories or {}}]}
    return io.BytesIO(json.dumps(body).encode("utf-8"))


# ---------------------------------------------------------------------------
# Test 1: clean text passes
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-test")
def test_clean_text_passes(mock_urlopen):
    # Arrange
    mock_urlopen.return_value = _openai_response(False)

    # Act
    ensure_not_toxic("Have a lovely day!")

    # Assert
    req = mock_urlopen.call_args[0][0]
    assert req.full_url == "https://api.openai.com/v1/moderations"
    assert req.get_header("Authorization") == "Bearer sk-test"


# ---------------------------------------------------------------------------
# Test 2: toxic text is blocked with the main categories in the message
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-test")
def test_toxic_text_raises_422(mock_urlopen):
    # Arrange
    mock_urlopen.return_value = _openai_response(True, {
        "harassment": True,
        "harassment/threatening": True,
        "hate": False,
    })

    # Act & Assert
    with pytest.raises(ModerationError) as exc:
        ensure_not_toxic("some hateful text")
    assert exc.value.status_code == 422
    assert "(harassment)" in exc.value.message


# ---------------------------------------------------------------------------
# Test 3: HTML is stripped and several texts are checked in one call
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-test")
def test_html_stripped_and_texts_joined(mock_urlopen):
    # Arrange
    mock_urlopen.return_value = _openai_response(False)

    # Act
    ensure_not_toxic("Title", "<p><strong>Bold</strong> &amp; body</p>")

    # Assert
    sent = json.loads(mock_urlopen.call_args[0][0].data)["input"]
    assert "<" not in sent
    assert "Title" in sent and "Bold" in sent and "& body" in sent
    mock_urlopen.assert_called_once()


# ---------------------------------------------------------------------------
# Test 4: no API key → check skipped, content allowed
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
def test_no_api_key_skips_check(mock_urlopen):
    # Act (conftest blanks the key)
    ensure_not_toxic("anything")

    # Assert
    mock_urlopen.assert_not_called()


# ---------------------------------------------------------------------------
# Test 5: OpenAI unreachable → fail open, content allowed
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-test")
def test_api_error_fails_open(mock_urlopen):
    # Arrange
    mock_urlopen.side_effect = urllib.error.URLError("timeout")

    # Act & Assert — no exception
    ensure_not_toxic("anything")


# ---------------------------------------------------------------------------
# Test 6: OpenAI rejects the key → fail open, content allowed
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-bad")
def test_api_rejects_key_fails_open(mock_urlopen, capsys):
    # Arrange
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.openai.com/v1/moderations", 401, "Unauthorized", {},
        io.BytesIO(b'{"error": {"code": "invalid_organization"}}'))

    # Act — no exception
    ensure_not_toxic("anything")

    # Assert — the real reason is printed for debugging
    assert "invalid_organization" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Test 7: empty text → no API call
# ---------------------------------------------------------------------------
@patch("services.sentiment_service.urllib.request.urlopen")
@patch("services.sentiment_service.OPENAI_API_KEY", "sk-test")
def test_empty_text_skips_call(mock_urlopen):
    # Act
    ensure_not_toxic("", "<p></p>")

    # Assert
    mock_urlopen.assert_not_called()
