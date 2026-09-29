"""Unit tests for follow_service, user_service and post_service feeds —
strict black-box, AAA pattern.  Repositories are mocked.
"""

import pytest
from unittest.mock import patch

from core.exceptions import ForbiddenError, NotFoundError, ValidationError
from services import follow_service, post_service, user_service


# ---------------------------------------------------------------------------
# follow_service
# ---------------------------------------------------------------------------
@patch("services.follow_service.follow_user")
@patch("services.follow_service.get_user_by_id")
def test_follow_success(mock_get_user, mock_follow):
    # Arrange
    mock_get_user.return_value = {"id": 2}
    mock_follow.return_value = True

    # Act
    result = follow_service.follow(1, 2)

    # Assert
    assert result == ("Followed.", True)
    mock_follow.assert_called_once_with(1, 2)


@patch("services.follow_service.follow_user")
@patch("services.follow_service.get_user_by_id")
def test_follow_already_following(mock_get_user, mock_follow):
    # Arrange
    mock_get_user.return_value = {"id": 2}
    mock_follow.return_value = False

    # Act / Assert
    assert follow_service.follow(1, 2) == ("Already following.", True)


def test_follow_yourself_rejected():
    # Act & Assert
    with pytest.raises(ValidationError):
        follow_service.follow(1, 1)


@patch("services.follow_service.get_user_by_id")
def test_follow_unknown_user(mock_get_user):
    # Arrange
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        follow_service.follow(1, 999)


@pytest.mark.parametrize("removed, message", [(True, "Unfollowed."), (False, "Was not following.")])
@patch("services.follow_service.unfollow_user")
def test_unfollow(mock_unfollow, removed, message):
    # Arrange
    mock_unfollow.return_value = removed

    # Act / Assert
    assert follow_service.unfollow(1, 2) == (message, False)


@patch("services.follow_service.get_followers")
@patch("services.follow_service.get_user_by_id")
def test_get_user_followers(mock_get_user, mock_followers):
    # Arrange
    mock_get_user.return_value = {"id": 2}
    mock_followers.return_value = [{"id": 5}]

    # Act / Assert
    assert follow_service.get_user_followers(2) == [{"id": 5}]


@patch("services.follow_service.get_following")
@patch("services.follow_service.get_user_by_id")
def test_get_user_following(mock_get_user, mock_following):
    # Arrange
    mock_get_user.return_value = {"id": 2}
    mock_following.return_value = [{"id": 6}]

    # Act / Assert
    assert follow_service.get_user_following(2) == [{"id": 6}]


@pytest.mark.parametrize("func", ["get_user_followers", "get_user_following"])
@patch("services.follow_service.get_user_by_id")
def test_follow_lists_unknown_user(mock_get_user, func):
    # Arrange
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        getattr(follow_service, func)(999)


@patch("services.follow_service.is_following")
def test_check_is_following(mock_is_following):
    # Arrange
    mock_is_following.return_value = True

    # Act / Assert
    assert follow_service.check_is_following(1, 2) is True


# ---------------------------------------------------------------------------
# user_service
# ---------------------------------------------------------------------------
@patch("services.user_service.get_users_paginated")
def test_get_users_hides_private_fields(mock_users):
    # Arrange — the repository returns everything (admins need it)
    mock_users.return_value = [
        {"id": 1, "name": "Ann", "email": "ann@x.com", "role": "admin", "is_banned": 0,
         "followers_count": 3, "following_count": 4},
    ]

    # Act
    users = user_service.get_users(0, 10)

    # Assert — public list: counts yes, email / role / ban status no
    assert users == [{"id": 1, "name": "Ann", "followers_count": 3, "following_count": 4}]


@patch("services.user_service.get_following_count")
@patch("services.user_service.get_followers_count")
@patch("services.user_service.get_user_by_id")
def test_get_single_user(mock_get_user, mock_followers, mock_following):
    # Arrange
    mock_get_user.return_value = {"id": 1}
    mock_followers.return_value = 0
    mock_following.return_value = 2

    # Act
    user = user_service.get_single_user(1)

    # Assert
    assert user["following_count"] == 2


@patch("services.user_service.get_user_by_id")
def test_get_single_user_not_found(mock_get_user):
    # Arrange
    mock_get_user.return_value = None

    # Act & Assert
    with pytest.raises(NotFoundError):
        user_service.get_single_user(999)


@patch("services.user_service.get_following_count")
@patch("services.user_service.get_followers_count")
@patch("services.user_service.get_user_by_id")
@patch("services.user_service.update_user_profile")
def test_update_profile_success(mock_update, mock_get_user, mock_followers, mock_following):
    # Arrange
    mock_update.return_value = True
    mock_get_user.return_value = {"id": 1, "name": "New"}
    mock_followers.return_value = 0
    mock_following.return_value = 0

    # Act
    user = user_service.update_profile(1, 1, name="  New  ", bio="Hi")

    # Assert
    assert user["name"] == "New"
    mock_update.assert_called_once_with(1, name="New", bio="Hi", profile_picture=None)


def test_update_profile_of_someone_else_forbidden():
    # Act & Assert
    with pytest.raises(ForbiddenError):
        user_service.update_profile(1, 2, name="Hacker")


def test_update_profile_empty_name():
    # Act & Assert
    with pytest.raises(ValidationError):
        user_service.update_profile(1, 1, name="   ")


@patch("services.user_service.get_following_count", return_value=0)
@patch("services.user_service.get_followers_count", return_value=0)
@patch("services.user_service.get_user_by_id", return_value={"id": 1, "bio": "same"})
@patch("services.user_service.update_user_profile")
def test_update_profile_unchanged_values_is_ok(mock_update, *_):
    # Arrange — MySQL reports 0 changed rows when the values are the same
    mock_update.return_value = False

    # Act
    user = user_service.update_profile(1, 1, bio="same")

    # Assert — saving without changes is not an error
    assert user["bio"] == "same"


def test_update_profile_nothing_given():
    # Act & Assert
    with pytest.raises(ValidationError, match="Nothing to update"):
        user_service.update_profile(1, 1)


@pytest.mark.parametrize("kwargs, message", [
    ({"name": "x" * 101}, "Name is too long"),
    ({"bio": "x" * 501}, "Bio is too long"),
    ({"profile_picture": "https://evil.example/track.gif"}, "Invalid profile picture"),
])
def test_update_profile_rejects_bad_values(kwargs, message):
    # Act & Assert
    with pytest.raises(ValidationError, match=message):
        user_service.update_profile(1, 1, **kwargs)


# ---------------------------------------------------------------------------
# post_service feeds
# ---------------------------------------------------------------------------
@patch("services.post_service.get_posts_paginated")
def test_get_posts_passes_filter(mock_posts):
    # Arrange
    mock_posts.return_value = [{"id": 1}]

    # Act
    result = post_service.get_posts(0, 10, 5)

    # Assert
    assert result == [{"id": 1}]
    mock_posts.assert_called_once_with(0, 10, 5)


@patch("services.post_service.get_following_posts_paginated")
def test_get_following_posts(mock_posts):
    # Arrange
    mock_posts.return_value = [{"id": 2}]

    # Act / Assert
    assert post_service.get_following_posts(1, 0, 10) == [{"id": 2}]
    mock_posts.assert_called_once_with(1, 0, 10)
