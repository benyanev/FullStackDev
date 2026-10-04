"""Reset service — password reset request and confirmation logic.

Generates a secure random token, sends a reset link via email,
and validates/consumes the token to update the user's password.
"""

import html
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt

from core.config import FRONTEND_URL
from core.exceptions import AppError, NotFoundError, ValidationError
from repositories.reset_repository import (
    create_reset_token,
    get_reset_by_token,
    invalidate_user_tokens,
    mark_token_used,
)
from repositories.session_repository import delete_user_sessions
from repositories.user_repository import get_user_by_email, update_password_hash
from services.auth_service import validate_password
from services.email_service import send_email

# Reset tokens expire after 1 hour
TOKEN_EXPIRY_SECONDS = 3600


def request_reset(email):
    """Generate a reset token and send a reset email.

    If the email doesn't exist, we silently return (no user enumeration).

    Args:
        email: The email address to send the reset link to.

    Returns:
        True (always, to prevent user enumeration).
    """
    if not email:
        raise ValidationError('Email is required.')

    user = get_user_by_email(email)
    if user is None:
        # Don't reveal whether the email exists — silently succeed
        return True

    # Invalidate any previous unused tokens for this user
    invalidate_user_tokens(user['id'])

    # Generate a cryptographically secure random token
    token = secrets.token_hex(32)  # 64-character hex string
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=TOKEN_EXPIRY_SECONDS)

    create_reset_token(user['id'], token, expires_at)

    # Build the reset link pointing to the frontend page
    reset_link = f'{FRONTEND_URL}/reset-password?token={token}'

    try:
        send_email(
            to=email,
            subject='SocialApp — Password Reset',
            body_html=(
                f'<h2>Password Reset Request</h2>'
                # Escaped: the name is user input and must not inject HTML
                f'<p>Hi {html.escape(user["name"])},</p>'
                f'<p>Click the link below to reset your password. '
                f'This link expires in 1 hour.</p>'
                f'<p><a href="{reset_link}">{reset_link}</a></p>'
                f'<p>If you did not request this, you can safely ignore this email.</p>'
            ),
        )
    except AppError:
        # The reason is already printed by email_service. Answer the same way
        # as for unknown emails, so failures don't reveal which emails exist.
        pass

    return True


def confirm_reset(token, new_password):
    """Validate a reset token and update the user's password.

    Args:
        token:        The 64-character hex token from the reset email.
        new_password: The new plain-text password.

    Returns:
        True on success.

    Raises:
        ValidationError: If the token or password is missing/invalid.
        NotFoundError:   If the token doesn't exist or has expired/been used.
    """
    if not token:
        raise ValidationError('Reset token is required.')
    validate_password(new_password or '')

    reset = get_reset_by_token(token)
    if reset is None:
        raise NotFoundError('Invalid or expired reset link.')

    if reset['used']:
        raise ValidationError('This reset link has already been used.')

    # Check expiry
    expires_at = reset['expires_at']
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if expires_at < datetime.now(timezone.utc):
        mark_token_used(token)
        raise ValidationError('This reset link has expired. Please request a new one.')

    # Hash the new password and update the user
    new_hash = bcrypt.hashpw(
        new_password.encode('utf-8'), bcrypt.gensalt()
    ).decode('utf-8')

    update_password_hash(reset['user_id'], new_hash)
    mark_token_used(token)

    # Log out every device: a stolen session must not survive a password reset
    delete_user_sessions(reset['user_id'])

    return True
