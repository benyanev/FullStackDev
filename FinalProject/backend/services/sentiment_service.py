"""Sentiment service — blocks toxic or hateful content before it is published.

Sends the text to the OpenAI Moderation API (free to use) with one POST
request using only the standard library.  If the text is flagged, a
:class:`core.exceptions.ModerationError` (422) is raised and the caller
does not save the content.

If no API key is configured or OpenAI is unreachable, the check is skipped
("fail open") and a warning is printed, so the site keeps working.
"""

import html
import json
import re
import urllib.error
import urllib.request

from core.config import OPENAI_API_KEY
from core.exceptions import ModerationError

MODERATION_URL = 'https://api.openai.com/v1/moderations'
MODERATION_MODEL = 'omni-moderation-latest'


def _strip_html(text):
    """Turn rich-text HTML (from the Tiptap editor) into plain text."""
    return html.unescape(re.sub(r'<[^>]+>', ' ', text or '')).strip()


def _get_flagged_categories(text):
    """Ask OpenAI whether *text* is harmful.

    Returns:
        A list of flagged category names (e.g. ``['harassment']``), an empty
        list if the text is fine, or ``None`` if the check could not run.
    """
    if not OPENAI_API_KEY:
        print('MODERATION SKIPPED: OPENAI_API_KEY not set')
        return None

    req = urllib.request.Request(
        MODERATION_URL,
        data=json.dumps({'model': MODERATION_MODEL, 'input': text}).encode('utf-8'),
        method='POST',
        headers={
            'Authorization': f'Bearer {OPENAI_API_KEY}',
            'Content-Type': 'application/json',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.load(response)['results'][0]
    except urllib.error.HTTPError as e:
        # OpenAI explains the problem in the body (bad key, no access, quota...)
        print(f'MODERATION SKIPPED: HTTP {e.code} {e.read().decode(errors="replace")}')
        return None
    except (urllib.error.URLError, OSError, KeyError, ValueError) as e:
        print(f'MODERATION SKIPPED: {e!r}')
        return None

    if not result.get('flagged'):
        return []
    return [name for name, hit in result.get('categories', {}).items() if hit]


def ensure_not_toxic(*texts):
    """Raise if any of the given texts is toxic or hateful.

    HTML tags are stripped first, and all texts are checked together in a
    single API call (e.g. a post's title and body).

    Args:
        *texts: One or more strings (plain text or HTML).

    Raises:
        ModerationError: If OpenAI flags the content.
    """
    text = '\n'.join(_strip_html(t) for t in texts if t)
    if not text:
        return

    categories = _get_flagged_categories(text)
    if categories:
        # Keep only the main category: 'hate/threatening' -> 'hate'
        reasons = ', '.join(sorted({c.split('/')[0] for c in categories}))
        raise ModerationError(
            f'This looks offensive ({reasons}). Please rewrite it before publishing.')
