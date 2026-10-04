"""Unit tests for services.post_service.create_post — strict black-box, AAA pattern.

Repositories and the sentiment check are mocked.
"""

import pytest
from unittest.mock import patch

from core.exceptions import ModerationError, ValidationError
from services.post_service import create_post


# ---------------------------------------------------------------------------
# Test 1: create_post — success (title + body are moderated together)
# ---------------------------------------------------------------------------
@patch("services.post_service.repo_create_post")
@patch("services.post_service.ensure_not_toxic")
def test_create_post_success(mock_moderate, mock_create):
    # Arrange
    mock_create.return_value = 7

    # Act
    result = create_post(1, "Title", "<p>Body</p>", "")

    # Assert
    assert result == 7
    mock_moderate.assert_called_once_with("Title", "<p>Body</p>")
    mock_create.assert_called_once_with(1, "Title", "<p>Body</p>", "", "")


# ---------------------------------------------------------------------------
# Test 2: create_post — missing title
# ---------------------------------------------------------------------------
def test_create_post_missing_title():
    # Act & Assert
    with pytest.raises(ValidationError):
        create_post(1, "", "<p>Body</p>", "")


# ---------------------------------------------------------------------------
# Test 3: create_post — toxic content is not saved
# ---------------------------------------------------------------------------
@patch("services.post_service.repo_create_post")
@patch("services.post_service.ensure_not_toxic")
def test_create_post_toxic_blocked(mock_moderate, mock_create):
    # Arrange
    mock_moderate.side_effect = ModerationError("offensive")

    # Act & Assert
    with pytest.raises(ModerationError):
        create_post(1, "Title", "<p>nasty</p>", "")
    mock_create.assert_not_called()


# ---------------------------------------------------------------------------
# Test 4: create_post — with a video
# ---------------------------------------------------------------------------
@patch("services.post_service.repo_create_post")
@patch("services.post_service.ensure_not_toxic")
def test_create_post_with_video(mock_moderate, mock_create):
    # Arrange
    mock_create.return_value = 8

    # Act
    create_post(1, "Title", "<p>Body</p>", "", "/static/uploads/videos/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp4")

    # Assert
    mock_create.assert_called_once_with(
        1, "Title", "<p>Body</p>", "", "/static/uploads/videos/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.mp4")


# ---------------------------------------------------------------------------
# Test 5: create_post — image AND video is rejected
# ---------------------------------------------------------------------------
def test_create_post_image_and_video_rejected():
    # Act & Assert
    with pytest.raises(ValidationError, match="either an image or a video"):
        create_post(1, "Title", "<p>Body</p>", "/i.jpg", "/v.mp4")


# ---------------------------------------------------------------------------
# Test 6: create_post — length limits and media must be our own uploads
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("title, body, image_url, video_url, message", [
    ("x" * 256, "<p>B</p>", "", "", "Title is too long"),
    ("T", "x" * 20001, "", "", "Post is too long"),
    ("T", "<p>B</p>", "https://evil.example/track.gif", "", "Invalid media"),
    ("T", "<p>B</p>", "", "/static/uploads/posts/../../app.py", "Invalid media"),
])
def test_create_post_rejects_bad_input(title, body, image_url, video_url, message):
    # Act & Assert
    with pytest.raises(ValidationError, match=message):
        create_post(1, title, body, image_url, video_url)
