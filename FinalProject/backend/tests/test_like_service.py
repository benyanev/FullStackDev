"""Unit tests for services.like_service — strict black-box, AAA pattern.

Every external dependency (repositories) is mocked so that the
unit under test runs in complete isolation.
"""

import pytest
from unittest.mock import patch

from core.exceptions import NotFoundError
from services.like_service import toggle_like, get_post_likes


# ---------------------------------------------------------------------------
# Test 1: toggle_like — like a post (not yet liked)
# ---------------------------------------------------------------------------
@patch("services.like_service.get_like_count")
@patch("services.like_service.add_like")
@patch("services.like_service.has_user_liked")
@patch("services.like_service.get_post_by_id")
def test_toggle_like_adds_like(mock_get_post, mock_has_liked, mock_add, mock_count):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_has_liked.return_value = False
    mock_count.return_value = 1

    # Act
    result = toggle_like(user_id=10, post_id=1)

    # Assert
    assert result["liked"] is True
    assert result["likeCount"] == 1
    mock_add.assert_called_once_with(10, 1)


# ---------------------------------------------------------------------------
# Test 2: toggle_like — unlike a post (already liked)
# ---------------------------------------------------------------------------
@patch("services.like_service.get_like_count")
@patch("services.like_service.remove_like")
@patch("services.like_service.has_user_liked")
@patch("services.like_service.get_post_by_id")
def test_toggle_like_removes_like(mock_get_post, mock_has_liked, mock_remove, mock_count):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_has_liked.return_value = True
    mock_count.return_value = 0

    # Act
    result = toggle_like(user_id=10, post_id=1)

    # Assert
    assert result["liked"] is False
    assert result["likeCount"] == 0
    mock_remove.assert_called_once_with(10, 1)


# ---------------------------------------------------------------------------
# Test 3: toggle_like — post not found
# ---------------------------------------------------------------------------
@patch("services.like_service.get_post_by_id")
def test_toggle_like_post_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        toggle_like(user_id=10, post_id=999)


# ---------------------------------------------------------------------------
# Test 4: get_post_likes — logged-in user who has liked
# ---------------------------------------------------------------------------
@patch("services.like_service.has_user_liked")
@patch("services.like_service.get_like_count")
@patch("services.like_service.get_post_by_id")
def test_get_post_likes_user_liked(mock_get_post, mock_count, mock_has_liked):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_count.return_value = 5
    mock_has_liked.return_value = True

    # Act
    result = get_post_likes(user_id=10, post_id=1)

    # Assert
    assert result["liked"] is True
    assert result["likeCount"] == 5


# ---------------------------------------------------------------------------
# Test 5: get_post_likes — anonymous user (user_id is None)
# ---------------------------------------------------------------------------
@patch("services.like_service.get_like_count")
@patch("services.like_service.get_post_by_id")
def test_get_post_likes_anonymous(mock_get_post, mock_count):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_count.return_value = 3

    # Act
    result = get_post_likes(user_id=None, post_id=1)

    # Assert
    assert result["liked"] is False
    assert result["likeCount"] == 3


# ---------------------------------------------------------------------------
# Test 6: get_post_likes — post not found
# ---------------------------------------------------------------------------
@patch("services.like_service.get_post_by_id")
def test_get_post_likes_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        get_post_likes(user_id=10, post_id=999)
