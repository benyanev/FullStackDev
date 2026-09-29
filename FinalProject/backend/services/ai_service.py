"""AI service — writing help powered by the OpenAI Chat Completions API.

Three features (Core requirement 2c):
- ``autocorrect``      — fix spelling/grammar of a post, keeping its formatting
- ``suggest_post``     — write a whole post (title + body) about a topic
- ``suggest_comment``  — propose a comment based on the post and its comments

Plus ``write_agent_post`` / ``write_agent_comment`` for the bot accounts
(Core requirement 2d), which write in a given personality's voice.

All of them go through one helper, ``_chat``, which sends a single POST
request using only the standard library.  Unlike moderation, these
features do not fail silently: if OpenAI is unavailable the user gets a
503 error, because they explicitly asked for AI help.
"""

import json
import re
import urllib.error
import urllib.request

from core.config import OPENAI_API_KEY, OPENAI_MODEL
from core.exceptions import AppError, NotFoundError, ValidationError
from repositories.comment_repository import get_comments_by_post
from repositories.post_repository import get_post_by_id

CHAT_URL = 'https://api.openai.com/v1/chat/completions'

MAX_TEXT_LENGTH = 5000     # autocorrect input
MAX_TOPIC_LENGTH = 200     # suggest_post input
CONTEXT_COMMENTS = 10      # how many recent comments suggest_comment reads


class AIUnavailableError(AppError):
    """Raised when the AI assistant cannot answer (503)."""

    def __init__(self, message='The AI assistant is unavailable right now. Please try again later.'):
        super().__init__(message, 503)


def _chat(system_prompt, user_prompt, max_tokens=600, json_mode=False):
    """Send one chat request to OpenAI and return the reply text.

    Args:
        system_prompt: Instructions for the model (its "role").
        user_prompt:   The actual request/content.
        max_tokens:    Upper limit for the reply length.
        json_mode:     If True, the model must reply with a JSON object.

    Raises:
        AIUnavailableError: If no key is configured or the request fails.
    """
    if not OPENAI_API_KEY:
        raise AIUnavailableError('The AI assistant is not configured (OPENAI_API_KEY missing).')

    payload = {
        'model': OPENAI_MODEL,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'max_tokens': max_tokens,
        'temperature': 0.7,
    }
    if json_mode:
        payload['response_format'] = {'type': 'json_object'}

    req = urllib.request.Request(
        CHAT_URL,
        data=json.dumps(payload).encode('utf-8'),
        method='POST',
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            reply = json.load(response)['choices'][0]['message']['content']
    except urllib.error.HTTPError as e:
        print(f'AI REQUEST FAILED: HTTP {e.code} {e.read().decode(errors="replace")}')
        raise AIUnavailableError()
    except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as e:
        print(f'AI REQUEST FAILED: {e!r}')
        raise AIUnavailableError()

    return (reply or '').strip()


def _strip_code_fences(text):
    """Remove ```html ... ``` wrappers the model sometimes adds."""
    return re.sub(r'^```[a-zA-Z]*\s*|\s*```$', '', text).strip()


def _plain_text(html):
    """Very small HTML → text helper for building prompts."""
    return re.sub(r'<[^>]+>', ' ', html or '').strip()


def autocorrect(text):
    """Fix spelling, grammar, and punctuation without changing the meaning.

    Works for plain text and for the HTML produced by the Tiptap editor
    (tags such as <p>, <strong>, <a> are kept as they are).

    Raises:
        ValidationError:    If the text is empty or too long.
        AIUnavailableError: If OpenAI cannot be reached.
    """
    if not text or not _plain_text(text):
        raise ValidationError('There is no text to correct.')
    if len(text) > MAX_TEXT_LENGTH:
        raise ValidationError(f'Text is too long (max {MAX_TEXT_LENGTH} characters).')

    corrected = _chat(
        'You are a proofreader. Fix spelling, grammar, and punctuation mistakes in the '
        "user's text. Keep the same language, meaning, tone, and length. If the text "
        'contains HTML tags, keep every tag and attribute exactly as it is and only fix '
        'the words between them. Reply with the corrected text only, no explanations.',
        text,
        max_tokens=2000,
    )
    return _strip_code_fences(corrected)


def suggest_post(topic):
    """Write a short social-media post about *topic*.

    Returns:
        A dict ``{'title': str, 'body': str}`` where *body* is simple HTML
        (<p>, <strong>, <em>) ready to load into the editor.

    Raises:
        ValidationError:    If the topic is empty or too long.
        AIUnavailableError: If OpenAI cannot be reached or replies badly.
    """
    if not topic:
        raise ValidationError('Please enter a topic.')
    if len(topic) > MAX_TOPIC_LENGTH:
        raise ValidationError(f'Topic is too long (max {MAX_TOPIC_LENGTH} characters).')

    reply = _chat(
        'You write engaging, friendly posts for a social media site. Reply with a JSON '
        'object with two keys: "title" (max 80 characters, no quotes or emojis at the '
        'start) and "body" (2-3 short paragraphs of simple HTML using only <p>, <strong> '
        'and <em> tags, under 120 words).',
        f'Write a post about: {topic}',
        json_mode=True,
    )

    try:
        post = json.loads(reply)
        title, body = post['title'].strip(), post['body'].strip()
    except (ValueError, KeyError, AttributeError):
        print(f'AI REPLY NOT VALID JSON: {reply!r}')
        raise AIUnavailableError('The AI assistant gave an unexpected answer. Please try again.')

    return {'title': title, 'body': body}


def suggest_comment(post_id):
    """Propose a comment for a post, based on the post and its latest comments.

    Raises:
        NotFoundError:      If the post doesn't exist.
        AIUnavailableError: If OpenAI cannot be reached.
    """
    post = get_post_by_id(post_id)
    if post is None:
        raise NotFoundError('Post not found.')

    recent = get_comments_by_post(post_id)[-CONTEXT_COMMENTS:]
    discussion = '\n'.join(f'- {c["authorName"]}: {c["body"]}' for c in recent) or '(no comments yet)'

    comment = _chat(
        'You help a user reply on a social media site. Write ONE short, friendly, '
        'relevant comment (1-2 sentences) that adds to the conversation. Do not repeat '
        'what others already said. Reply with the comment text only, no quotes.',
        f'Post title: {post["title"]}\n'
        f'Post text: {_plain_text(post["body"])[:1500]}\n\n'
        f'Existing comments:\n{discussion}',
        max_tokens=150,
    )
    return comment.strip('"')


# ---------------------------------------------------------------------------
# Agent (bot) content — used by services.agent_service (Core 2d)
# ---------------------------------------------------------------------------

def _agent_system_prompt(agent):
    """Tell the model to stay in character as this agent."""
    return (
        f'You are {agent["name"]}, a member of a social media site. '
        f'Your personality: {agent["personality"]} '
        'Always stay in character, write like a real person (not an assistant), '
        'and never mention that you are an AI.'
    )


def write_agent_post(agent, recent_titles):
    """Write a new post in the agent's voice.

    Args:
        agent:         Dict with ``name`` and ``personality``.
        recent_titles: Titles of the agent's latest posts (to avoid repeats).

    Returns:
        A dict ``{'title': str, 'body': str}`` (body is simple HTML).

    Raises:
        AIUnavailableError: If OpenAI cannot be reached or replies badly.
    """
    avoid = '\n'.join(f'- {t}' for t in recent_titles) or '(none yet)'
    reply = _chat(
        _agent_system_prompt(agent) + ' Reply with a JSON object with two keys: '
        '"title" (max 80 characters) and "body" (1-2 short paragraphs of simple HTML '
        'using only <p>, <strong> and <em>, under 90 words).',
        'Write a new post for your followers about something that fits your '
        f'personality. Pick a fresh subject, different from your recent posts:\n{avoid}',
        json_mode=True,
    )

    try:
        post = json.loads(reply)
        return {'title': post['title'].strip(), 'body': post['body'].strip()}
    except (ValueError, KeyError, AttributeError):
        print(f'AI REPLY NOT VALID JSON: {reply!r}')
        raise AIUnavailableError('The AI assistant gave an unexpected answer.')


def write_agent_comment(agent, post, comments):
    """Write a comment in the agent's voice, reacting to the post and discussion.

    Args:
        agent:    Dict with ``name`` and ``personality``.
        post:     Dict with ``title``, ``body``, and ``authorName``.
        comments: The post's comments (oldest first), dicts with
                  ``authorName`` and ``body``.

    Returns:
        The comment text.

    Raises:
        AIUnavailableError: If OpenAI cannot be reached.
    """
    recent = comments[-CONTEXT_COMMENTS:]
    discussion = '\n'.join(f'- {c["authorName"]}: {c["body"]}' for c in recent) or '(no comments yet)'

    comment = _chat(
        _agent_system_prompt(agent),
        f'{post["authorName"]} posted:\nTitle: {post["title"]}\n'
        f'{_plain_text(post["body"])[:1500]}\n\n'
        f'Comments so far:\n{discussion}\n\n'
        'Write ONE comment (1-3 sentences) in your own voice. If someone in the comments '
        'said something you want to respond to, reply to them by name (e.g. "@Dana ..."). '
        'Do not repeat points already made. Reply with the comment text only.',
        max_tokens=200,
    )
    return comment.strip('"')
