"""Authentication service — signup, login, logout, and session management.

All functions are HTTP-agnostic: they accept plain Python values, perform
business logic, and either return results or raise :mod:`core.exceptions`
subclasses.  Cookie handling is the controller's responsibility.
"""

from datetime import datetime, timedelta, timezone

import bcrypt

from core.config import SESSION_MAX_AGE
from core.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationError,
)
from repositories.session_repository import (
    create_session,
    delete_session,
    delete_expired_sessions,
    delete_user_sessions,
)
from repositories.user_repository import create_user, get_user_by_email, get_user_by_id


MAX_NAME_LENGTH = 100      # users.name is VARCHAR(100)
MAX_EMAIL_LENGTH = 255
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_BYTES = 72    # bcrypt only uses the first 72 bytes


def validate_password(password):
    """Raise ValidationError if the password is too short or too long."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f'Password must be at least {MIN_PASSWORD_LENGTH} characters.')
    if len(password.encode('utf-8')) > MAX_PASSWORD_BYTES:
        raise ValidationError('Password is too long (max 72 characters).')


def _create_session_for_user(user_id):
    """Create a DB session and return the session ID string."""
    expires_at = datetime.now(timezone.utc) + \
        timedelta(seconds=SESSION_MAX_AGE)
    return create_session(user_id, expires_at)


def signup(name, email, password):
    """Register a new user and create a session.

    Args:
        name:     Display name (already stripped by the controller).
        email:    Email address (already stripped and lowercased).
        password: Plain-text password.

    Returns:
        A tuple ``(user_dict, session_id)`` where *user_dict* contains
        ``id``, ``name``, and ``email``.

    Raises:
        ValidationError: If required fields are missing or password is too short.
        ConflictError:   If the email is already registered.
    """
    if not name or not email or not password:
        raise ValidationError('Name, email, and password are required.')
    if len(name) > MAX_NAME_LENGTH or len(email) > MAX_EMAIL_LENGTH:
        raise ValidationError('Name or email is too long.')
    validate_password(password)

    if get_user_by_email(email) is not None:
        raise ConflictError('An account with this email already exists.')

    # Hash password with bcrypt
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    user_id = create_user(name, email, password_hash.decode('utf-8'))

    session_id = _create_session_for_user(user_id)

    user = {'id': user_id, 'name': name, 'email': email, 'role': 'user'}
    return user, session_id


def login(email, password):
    """Authenticate a user and create a new session.

    Invalidates all existing sessions for the user before creating a
    new one (single-session enforcement).

    Args:
        email:    Email address (already stripped and lowercased).
        password: Plain-text password.

    Returns:
        A tuple ``(user_dict, session_id)``.

    Raises:
        ValidationError:    If required fields are missing.
        AuthenticationError: If credentials are invalid.
        ForbiddenError:     If the account has been banned.
    """
    if not email or not password:
        raise ValidationError('Email and password are required.')

    user = get_user_by_email(email)
    if user is None:
        raise AuthenticationError('Invalid email or password.')

    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise AuthenticationError('Invalid email or password.')

    # Checked after the password so a ban doesn't reveal which emails exist
    if user.get('is_banned'):
        raise ForbiddenError('This account has been banned.')

    # Invalidate any existing sessions (single-session enforcement), and
    # tidy up everyone's expired sessions while we're at it
    delete_user_sessions(user['id'])
    delete_expired_sessions()

    session_id = _create_session_for_user(user['id'])

    user_dict = {'id': user['id'], 'name': user['name'],
                 'email': user['email'], 'role': user.get('role', 'user')}
    return user_dict, session_id


def logout(session_id):
    """Destroy a session.

    Args:
        session_id: The session UUID to delete, or ``None``.
    """
    if session_id:
        delete_session(session_id)


def get_current_user(user_id):
    """Return the currently authenticated user's info.

    Args:
        user_id: The user's integer ID (from the session).

    Returns:
        A user dict (without password_hash).

    Raises:
        NotFoundError: If the user no longer exists.
    """
    user = get_user_by_id(user_id)
    if user is None:
        raise NotFoundError('User not found.')
    return user
