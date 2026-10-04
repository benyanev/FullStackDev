"""Unit tests for services.comment_service — strict black-box, AAA pattern.

Every external dependency (repositories) is mocked so that the
unit under test runs in complete isolation.
"""

import pytest
from unittest.mock import patch

from core.exceptions import ModerationError, NotFoundError, ValidationError
from services.comment_service import add_comment, get_comments


# ---------------------------------------------------------------------------
# Test 1: add_comment — success
# ---------------------------------------------------------------------------
@patch("services.comment_service.repo_create_comment")
@patch("services.comment_service.get_post_by_id")
def test_add_comment_success(mock_get_post, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_create.return_value = 42

    # Act
    result = add_comment(post_id=1, author_id=10, body="Nice post!")

    # Assert
    assert result == 42
    mock_create.assert_called_once_with(1, 10, "Nice post!", None)


# ---------------------------------------------------------------------------
# Test 2: add_comment — with parent_id (nested reply)
# ---------------------------------------------------------------------------
@patch("services.comment_service.repo_create_comment")
@patch("services.comment_service.get_post_by_id")
def test_add_comment_with_parent(mock_get_post, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_create.return_value = 43

    # Act
    result = add_comment(post_id=1, author_id=10, body="Reply!", parent_id=42)

    # Assert
    assert result == 43
    mock_create.assert_called_once_with(1, 10, "Reply!", 42)


# ---------------------------------------------------------------------------
# Test 3: add_comment — empty body
# ---------------------------------------------------------------------------
def test_add_comment_empty_body():
    # Act & Assert
    with pytest.raises(ValidationError):
        add_comment(post_id=1, author_id=10, body="")


# ---------------------------------------------------------------------------
# Test 4: add_comment — post not found
# ---------------------------------------------------------------------------
@patch("services.comment_service.get_post_by_id")
def test_add_comment_post_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        add_comment(post_id=999, author_id=10, body="Hello")


# ---------------------------------------------------------------------------
# Test 5: get_comments — success
# ---------------------------------------------------------------------------
@patch("services.comment_service.get_comments_by_post")
@patch("services.comment_service.get_post_by_id")
def test_get_comments_success(mock_get_post, mock_get_list):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_get_list.return_value = [
        {"id": 1, "body": "Great!", "authorName": "Alice"},
        {"id": 2, "body": "Thanks!", "authorName": "Bob"},
    ]

    # Act
    result = get_comments(post_id=1)

    # Assert
    assert result["count"] == 2
    assert len(result["comments"]) == 2
    assert result["comments"][0]["body"] == "Great!"


# ---------------------------------------------------------------------------
# Test 6: get_comments — post not found
# ---------------------------------------------------------------------------
@patch("services.comment_service.get_post_by_id")
def test_get_comments_post_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        get_comments(post_id=999)


# ---------------------------------------------------------------------------
# Test 7: add_comment — toxic comment is blocked and not saved
# ---------------------------------------------------------------------------
@patch("services.comment_service.repo_create_comment")
@patch("services.comment_service.ensure_not_toxic")
@patch("services.comment_service.get_post_by_id")
def test_add_comment_toxic_blocked(mock_get_post, mock_moderate, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "title": "Test"}
    mock_moderate.side_effect = ModerationError("offensive")

    # Act & Assert
    with pytest.raises(ModerationError):
        add_comment(post_id=1, author_id=10, body="nasty words")
    mock_create.assert_not_called()


# ---------------------------------------------------------------------------
# Test 8: add_comment — too long
# ---------------------------------------------------------------------------
def test_add_comment_too_long():
    # Act & Assert
    with pytest.raises(ValidationError, match="too long"):
        add_comment(post_id=1, author_id=10, body="x" * 2001)
