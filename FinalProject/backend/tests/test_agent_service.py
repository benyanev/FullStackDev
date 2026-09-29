"""Unit tests for services.agent_service — strict black-box, AAA pattern.

Repositories, the AI writers, and the post/comment services are mocked;
``random.choice`` is patched where the test needs a predictable pick.
"""

from unittest.mock import patch

from core.exceptions import ModerationError
from services import agent_service

AGENT = {"id": 50, "name": "Gary Grumble", "personality": "The Grumpy Skeptic"}
HUMAN_POST = {"id": 1, "userId": 2, "title": "Hello", "body": "<p>Hi</p>", "authorName": "Dana"}
OWN_POST = {"id": 2, "userId": 50, "title": "Mine", "body": "<p>x</p>", "authorName": "Gary Grumble"}


# ---------------------------------------------------------------------------
# run_agent_tick
# ---------------------------------------------------------------------------
@patch("services.agent_service.get_active_agents")
def test_tick_without_agents(mock_agents):
    # Arrange
    mock_agents.return_value = []

    # Act
    result = agent_service.run_agent_tick()

    # Assert
    assert "no active agents" in result


@patch("services.agent_service.random.choices")
@patch("services.agent_service.add_like")
@patch("services.agent_service.get_posts_paginated")
@patch("services.agent_service.get_active_agents")
def test_tick_picks_weighted_action(mock_agents, mock_posts, mock_add_like, mock_choices):
    # Arrange
    mock_agents.return_value = [AGENT]
    mock_posts.return_value = [HUMAN_POST]
    mock_choices.return_value = ["like"]

    # Act
    result = agent_service.run_agent_tick()

    # Assert
    assert result == "Gary Grumble liked post 1"
    assert mock_choices.call_args.kwargs["weights"] == agent_service.WEIGHTS


@patch("services.agent_service.post_service.create_post")
@patch("services.agent_service.ai_service.write_agent_post")
@patch("services.agent_service.get_posts_paginated")
@patch("services.agent_service.get_active_agents")
def test_tick_blocked_content_is_reported_not_raised(mock_agents, mock_posts,
                                                     mock_write, mock_create):
    # Arrange
    mock_agents.return_value = [AGENT]
    mock_posts.return_value = []
    mock_write.return_value = {"title": "T", "body": "B"}
    mock_create.side_effect = ModerationError("offensive")

    # Act
    result = agent_service.run_agent_tick("post")

    # Assert
    assert "tried to post but failed: offensive" in result


# ---------------------------------------------------------------------------
# post
# ---------------------------------------------------------------------------
@patch("services.agent_service.post_service.create_post")
@patch("services.agent_service.ai_service.write_agent_post")
@patch("services.agent_service.get_posts_paginated")
def test_post_passes_recent_titles_and_saves(mock_posts, mock_write, mock_create):
    # Arrange
    mock_posts.return_value = [OWN_POST]
    mock_write.return_value = {"title": "Hype is overrated", "body": "<p>Prove it.</p>"}

    # Act
    result = agent_service._do_post(AGENT)

    # Assert
    mock_posts.assert_called_once_with(0, 10, 50)
    mock_write.assert_called_once_with(AGENT, ["Mine"])
    mock_create.assert_called_once_with(50, "Hype is overrated", "<p>Prove it.</p>", "")
    assert result == 'posted "Hype is overrated"'


# ---------------------------------------------------------------------------
# comment
# ---------------------------------------------------------------------------
@patch("services.agent_service.comment_service.add_comment")
@patch("services.agent_service.ai_service.write_agent_comment")
@patch("services.agent_service.get_comments_by_post")
@patch("services.agent_service.get_posts_paginated")
def test_comment_on_other_users_post(mock_posts, mock_comments, mock_write, mock_add):
    # Arrange — own post must be ignored
    mock_posts.return_value = [OWN_POST, HUMAN_POST]
    comments = [{"author_id": 2, "authorName": "Dana", "body": "Nice"}]
    mock_comments.return_value = comments
    mock_write.return_value = "@Dana Is it though?"

    # Act
    result = agent_service._do_comment(AGENT)

    # Assert
    mock_write.assert_called_once_with(AGENT, HUMAN_POST, comments)
    mock_add.assert_called_once_with(1, 50, "@Dana Is it though?")
    assert "commented on post 1" in result


@patch("services.agent_service.comment_service.add_comment")
@patch("services.agent_service.get_comments_by_post")
@patch("services.agent_service.get_posts_paginated")
def test_comment_skips_post_where_agent_spoke_last(mock_posts, mock_comments, mock_add):
    # Arrange
    mock_posts.return_value = [HUMAN_POST]
    mock_comments.return_value = [{"author_id": 50, "authorName": "Gary Grumble", "body": "Meh"}]

    # Act
    result = agent_service._do_comment(AGENT)

    # Assert
    assert result == "had nothing to comment on"
    mock_add.assert_not_called()


# ---------------------------------------------------------------------------
# like
# ---------------------------------------------------------------------------
@patch("services.agent_service.add_like")
@patch("services.agent_service.get_posts_paginated")
def test_like_nothing_available(mock_posts, mock_add_like):
    # Arrange — only the agent's own post exists
    mock_posts.return_value = [OWN_POST]

    # Act
    result = agent_service._do_like(AGENT)

    # Assert
    assert result == "had nothing to like"
    mock_add_like.assert_not_called()


# ---------------------------------------------------------------------------
# follow
# ---------------------------------------------------------------------------
@patch("services.agent_service.follow_user")
@patch("services.agent_service.is_following")
@patch("services.agent_service.get_users_paginated")
def test_follow_someone_new(mock_users, mock_is_following, mock_follow):
    # Arrange — self and already-followed users are skipped
    mock_users.return_value = [
        {"id": 50, "name": "Gary Grumble"},
        {"id": 2, "name": "Dana"},
        {"id": 3, "name": "Omer"},
    ]
    mock_is_following.side_effect = lambda follower, target: target == 2

    # Act
    result = agent_service._do_follow(AGENT)

    # Assert
    mock_follow.assert_called_once_with(50, 3)
    assert result == "followed Omer"


@patch("services.agent_service.follow_user")
@patch("services.agent_service.is_following")
@patch("services.agent_service.get_users_paginated")
def test_follow_nobody_left(mock_users, mock_is_following, mock_follow):
    # Arrange
    mock_users.return_value = [{"id": 2, "name": "Dana"}]
    mock_is_following.return_value = True

    # Act
    result = agent_service._do_follow(AGENT)

    # Assert
    assert result == "had nobody new to follow"
    mock_follow.assert_not_called()
