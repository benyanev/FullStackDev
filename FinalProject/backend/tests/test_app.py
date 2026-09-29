"""Tests for the application factory settings — AAA pattern."""

from unittest.mock import patch

from flask import request

from app import create_app


def _client_ip(app, forwarded_for):
    """Return the client IP Flask sees for a request with X-Forwarded-For."""
    @app.route('/_ip')
    def _ip():
        return request.remote_addr

    response = app.test_client().get(
        '/_ip', headers={'X-Forwarded-For': forwarded_for},
        environ_base={'REMOTE_ADDR': '172.18.0.5'})  # e.g. the nginx container
    return response.get_data(as_text=True)


@patch("app.BEHIND_PROXY", True)
def test_behind_proxy_uses_forwarded_client_ip():
    # Act
    ip = _client_ip(create_app(), '203.0.113.7')

    # Assert — the real user's IP (rate limits apply per user, not per proxy)
    assert ip == '203.0.113.7'


@patch("app.BEHIND_PROXY", False)
def test_without_proxy_ignores_forwarded_header():
    # Act
    ip = _client_ip(create_app(), '203.0.113.7')

    # Assert — a client cannot fake its IP with the header
    assert ip == '172.18.0.5'
