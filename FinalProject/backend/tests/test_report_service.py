"""Unit tests for services.report_service — strict black-box, AAA pattern.

Repositories are mocked so the service runs in isolation.
"""

import pytest
from unittest.mock import patch

from core.exceptions import ConflictError, NotFoundError, ValidationError
from services.report_service import create_report


# ---------------------------------------------------------------------------
# Test 1: create_report — success
# ---------------------------------------------------------------------------
@patch("services.report_service.repo_create_report")
@patch("services.report_service.get_post_by_id")
def test_create_report_success(mock_get_post, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "author_id": 2}
    mock_create.return_value = True

    # Act
    create_report(reporter_id=10, post_id=1, reason="Spam")

    # Assert
    mock_create.assert_called_once_with(10, 1, "Spam")


# ---------------------------------------------------------------------------
# Test 2: create_report — empty reason
# ---------------------------------------------------------------------------
def test_create_report_empty_reason():
    # Act & Assert
    with pytest.raises(ValidationError):
        create_report(reporter_id=10, post_id=1, reason="")


# ---------------------------------------------------------------------------
# Test 3: create_report — reason too long
# ---------------------------------------------------------------------------
def test_create_report_reason_too_long():
    # Act & Assert
    with pytest.raises(ValidationError):
        create_report(reporter_id=10, post_id=1, reason="x" * 501)


# ---------------------------------------------------------------------------
# Test 4: create_report — post not found
# ---------------------------------------------------------------------------
@patch("services.report_service.get_post_by_id")
def test_create_report_post_not_found(mock_get_post):
    # Arrange
    mock_get_post.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        create_report(reporter_id=10, post_id=999, reason="Spam")


# ---------------------------------------------------------------------------
# Test 5: create_report — cannot report own post
# ---------------------------------------------------------------------------
@patch("services.report_service.repo_create_report")
@patch("services.report_service.get_post_by_id")
def test_create_report_own_post(mock_get_post, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "author_id": 10}

    # Act & Assert
    with pytest.raises(ValidationError):
        create_report(reporter_id=10, post_id=1, reason="Spam")
    mock_create.assert_not_called()


# ---------------------------------------------------------------------------
# Test 6: create_report — already reported
# ---------------------------------------------------------------------------
@patch("services.report_service.repo_create_report")
@patch("services.report_service.get_post_by_id")
def test_create_report_duplicate(mock_get_post, mock_create):
    # Arrange
    mock_get_post.return_value = {"id": 1, "author_id": 2}
    mock_create.return_value = False

    # Act & Assert
    with pytest.raises(ConflictError):
        create_report(reporter_id=10, post_id=1, reason="Spam")
