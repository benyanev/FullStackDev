"""Agent service — the "World Simulation" (Core requirement 2d).

Each call to :func:`run_agent_tick` makes ONE random agent (bot) do ONE
random action on the platform:

- post     — write a new post in its personality's voice
- comment  — react to a recent post (by a human or another agent),
             reading the existing comments so bots hold conversations
- like     — like a recent post
- follow   — follow another user

Agents go through the normal services (``post_service``,
``comment_service``), so their content passes the same validation and
toxicity check as a human's.  The loop that calls this repeatedly lives
in ``run_agents.py``.
"""

import random

from core.exceptions import AppError
from repositories.comment_repository import get_comments_by_post
from repositories.follow_repository import follow_user, is_following
from repositories.like_repository import add_like
from repositories.post_repository import get_posts_paginated
from repositories.user_repository import get_active_agents, get_users_paginated
from services import ai_service, comment_service, post_service

# Relative chance of each action (comments are most common → conversations)
ACTIONS = ['post', 'comment', 'like', 'follow']
WEIGHTS = [3, 4, 2, 1]

RECENT_POSTS = 20       # agents only interact with the newest posts


def _recent_posts_by_others(agent_id):
    """Newest posts on the site that the agent did not write."""
    return [p for p in get_posts_paginated(0, RECENT_POSTS) if p['userId'] != agent_id]


def _do_post(agent):
    own = get_posts_paginated(0, 10, agent['id'])
    post = ai_service.write_agent_post(agent, [p['title'] for p in own])
    post_service.create_post(agent['id'], post['title'], post['body'], '')
    return f'posted "{post["title"]}"'


def _do_comment(agent):
    # Skip posts where this agent wrote the latest comment (don't talk to itself)
    candidates = []
    for post in _recent_posts_by_others(agent['id']):
        comments = get_comments_by_post(post['id'])
        if not comments or comments[-1]['author_id'] != agent['id']:
            candidates.append((post, comments))
    if not candidates:
        return 'had nothing to comment on'

    post, comments = random.choice(candidates)
    text = ai_service.write_agent_comment(agent, post, comments)
    comment_service.add_comment(post['id'], agent['id'], text)
    return f'commented on post {post["id"]}: "{text}"'


def _do_like(agent):
    posts = _recent_posts_by_others(agent['id'])
    if not posts:
        return 'had nothing to like'
    post = random.choice(posts)
    add_like(agent['id'], post['id'])  # INSERT IGNORE — liking twice is harmless
    return f'liked post {post["id"]}'


def _do_follow(agent):
    users = [u for u in get_users_paginated(0, 100)
             if u['id'] != agent['id'] and not is_following(agent['id'], u['id'])]
    if not users:
        return 'had nobody new to follow'
    user = random.choice(users)
    follow_user(agent['id'], user['id'])
    return f'followed {user["name"]}'


HANDLERS = {'post': _do_post, 'comment': _do_comment, 'like': _do_like, 'follow': _do_follow}


def run_agent_tick(action=None):
    """Let one random agent perform one action.

    Args:
        action: Force a specific action ('post', 'comment', 'like', 'follow');
                picked at random (weighted) when None.

    Returns:
        A one-line description of what happened (for the console log).
    """
    agents = get_active_agents()
    if not agents:
        return 'no active agents — run seed_agents.py first'

    agent = random.choice(agents)
    action = action or random.choices(ACTIONS, weights=WEIGHTS)[0]

    try:
        result = HANDLERS[action](agent)
    except AppError as e:
        # e.g. the toxicity check blocked the text, or OpenAI is unavailable
        result = f'tried to {action} but failed: {e.message}'

    return f'{agent["name"]} {result}'
