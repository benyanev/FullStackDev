"""Rate limiting works (limits are switched off in all other tests by conftest)."""

from unittest.mock import patch

from app import create_app
from core.extensions import limiter


@patch("app.RATELIMIT_ENABLED", True)
def test_reset_request_is_rate_limited():
    # Arrange
    client = create_app().test_client()
    limiter.reset()

    # Act — empty email: rejected with 400 before any DB access or email
    codes = [client.post("/api/reset-request", json={"email": ""}).status_code
             for _ in range(4)]

    # Assert — 3 per minute are allowed, the 4th is refused
    assert codes == [400, 400, 400, 429]
