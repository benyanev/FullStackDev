"""Email service — sends transactional emails via the Resend HTTP API.

Uses only the standard library (``urllib`` + ``json``): one POST request to
``https://api.resend.com/emails`` with the API key as a Bearer token.
Settings come from :mod:`core.config` (loaded from ``.env``).

For development, emails are logged to the console instead of being sent
when ``RESEND_API_KEY`` is not configured.
"""

import json
import urllib.error
import urllib.request

from core.config import EMAIL_FROM, RESEND_API_KEY
from core.exceptions import AppError

RESEND_URL = 'https://api.resend.com/emails'


def send_email(to, subject, body_html):
    """Send an HTML email.

    If no Resend API key is configured (dev mode), the email content
    is printed to the console instead of being sent.

    Args:
        to:        Recipient email address.
        subject:   Email subject line.
        body_html: HTML body content.

    Raises:
        AppError (503): If Resend rejects the request or is unreachable.
    """
    if not RESEND_API_KEY:
        # Dev mode — just log it
        print(f'\n{"=" * 50}')
        print('EMAIL (dev mode — RESEND_API_KEY not set, not sent)')
        print(f'To:      {to}')
        print(f'Subject: {subject}')
        print(f'Body:    {body_html}')
        print(f'{"=" * 50}\n')
        return

    payload = json.dumps({
        'from': EMAIL_FROM,
        'to': [to],
        'subject': subject,
        'html': body_html,
    }).encode('utf-8')

    req = urllib.request.Request(
        RESEND_URL,
        data=payload,
        method='POST',
        headers={
            'Authorization': f'Bearer {RESEND_API_KEY}',
            'Content-Type': 'application/json',
            # Resend's firewall rejects Python's default User-Agent
            'User-Agent': 'SocialApp/1.0',
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
    except urllib.error.HTTPError as e:
        # Resend explains the problem in the response body (e.g. bad key,
        # or recipient not allowed with the onboarding@resend.dev sender)
        print(f'EMAIL SEND FAILED to {to}: HTTP {e.code} {e.read().decode(errors="replace")}')
        raise AppError('Could not send email right now. Please try again later.', 503)
    except (urllib.error.URLError, OSError) as e:
        print(f'EMAIL SEND FAILED to {to}: {e!r}')
        raise AppError('Could not send email right now. Please try again later.', 503)
