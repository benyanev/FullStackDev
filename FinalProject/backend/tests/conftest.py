"""Shared pytest fixtures.

Safety net: blank out every external API key for all tests, so a test that
forgets to mock something can never send a real email or call OpenAI.
Individual tests can still patch a key back on to test the sending code.
"""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def no_external_apis():
    """Disable Resend and OpenAI (moderation + AI Assist) for every test."""
    with patch("services.email_service.RESEND_API_KEY", ""), \
            patch("services.sentiment_service.OPENAI_API_KEY", ""), \
            patch("services.ai_service.OPENAI_API_KEY", ""):
        yield


@pytest.fixture(autouse=True)
def no_rate_limits():
    """Rate-limit counters are shared by the whole test run; switch them off
    so tests don't fail randomly. test_rate_limits.py turns them back on."""
    with patch("app.RATELIMIT_ENABLED", False):
        yield


@pytest.fixture(autouse=True)
def no_real_database():
    """Safety net: a test that forgets to mock a repository must FAIL,
    not silently read or change the real local database."""
    def refuse(*args, **kwargs):
        raise RuntimeError("Tests must not connect to the real database - mock the repository.")

    with patch("mysql.connector.connect", side_effect=refuse):
        yield
