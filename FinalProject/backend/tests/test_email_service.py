"""Unit tests for email_service — strict black-box, AAA pattern.

The API key is patched at the module level; urllib's ``urlopen`` is mocked
so no real HTTP request is made.
"""

import io
import json
import urllib.error
from unittest.mock import patch

import pytest

from core.exceptions import AppError
from services import email_service


# ---------------------------------------------------------------------------
# Test 1: No API key → dev mode prints the email, never calls Resend
# ---------------------------------------------------------------------------
@patch("services.email_service.urllib.request.urlopen")
@patch("services.email_service.RESEND_API_KEY", "")
def test_send_email_dev_mode_prints_instead_of_sending(mock_urlopen, capsys):
    # Act
    email_service.send_email("a@test.com", "Subject", "<p>Hi</p>")

    # Assert
    mock_urlopen.assert_not_called()
    assert "a@test.com" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Test 2: API key set → POSTs the email to Resend with the Bearer token
# ---------------------------------------------------------------------------
@patch("services.email_service.urllib.request.urlopen")
@patch("services.email_service.RESEND_API_KEY", "re_test_key")
def test_send_email_posts_to_resend(mock_urlopen):
    # Act
    email_service.send_email("a@test.com", "Subject", "<p>Hi</p>")

    # Assert
    req = mock_urlopen.call_args[0][0]
    body = json.loads(req.data)
    assert req.full_url == "https://api.resend.com/emails"
    assert req.get_header("Authorization") == "Bearer re_test_key"
    assert body["to"] == ["a@test.com"]
    assert body["subject"] == "Subject"


# ---------------------------------------------------------------------------
# Test 3: Resend rejects the request → AppError 503
# ---------------------------------------------------------------------------
@patch("services.email_service.urllib.request.urlopen")
@patch("services.email_service.RESEND_API_KEY", "re_bad_key")
def test_send_email_resend_error_raises_503(mock_urlopen):
    # Arrange
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.resend.com/emails", 401, "Unauthorized", {},
        io.BytesIO(b'{"message": "API key is invalid"}'))

    # Act / Assert
    with pytest.raises(AppError) as exc:
        email_service.send_email("a@test.com", "Subject", "<p>Hi</p>")
    assert exc.value.status_code == 503


# ---------------------------------------------------------------------------
# Test 4: Network down → AppError 503
# ---------------------------------------------------------------------------
@patch("services.email_service.urllib.request.urlopen")
@patch("services.email_service.RESEND_API_KEY", "re_test_key")
def test_send_email_network_error_raises_503(mock_urlopen):
    # Arrange
    mock_urlopen.side_effect = urllib.error.URLError("no route to host")

    # Act / Assert
    with pytest.raises(AppError) as exc:
        email_service.send_email("a@test.com", "Subject", "<p>Hi</p>")
    assert exc.value.status_code == 503
