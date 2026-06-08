"""Database helper module — provides CRUD functions for users, posts, and sessions."""

import os
import uuid
from pathlib import Path

from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env at the project root
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', ''),
    'database': os.environ.get('DB_NAME', 'social_app'),
}


def get_connection():
    """Return a new MySQL connection using the global config."""
    return mysql.connector.connect(**DB_CONFIG)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

def get_user_by_id(user_id):
    """Look up a user by primary key.

    Args:
        user_id: The user's integer ID.

    Returns:
        A dict with id, name, email, bio, profile_picture, and created_at,
        or None if not found. The password_hash column is intentionally excluded.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, created_at '
            'FROM users WHERE id = %s',
            (user_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_user_by_email(email):
    """Look up a user by email address.

    Unlike get_user_by_id, this returns all columns (including
    password_hash) because it is used during login verification.

    Args:
        email: The email address to search for.

    Returns:
        A full user dict, or None if no match exists.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_users_paginated(start=0, limit=10):
    """Return a paginated list of users, ordered by newest first.

    Args:
        start: Pagination offset (default 0).
        limit: Maximum number of users to return (default 10).

    Returns:
        A list of user dicts (id, name, email, bio, profile_picture, created_at).
        The password_hash column is excluded for safety.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, bio, profile_picture, created_at FROM users '
            'ORDER BY created_at DESC LIMIT %s OFFSET %s',
            (limit, start)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_user(name, email, password_hash):
    """Insert a new user into the database.

    Args:
        name:          Display name.
        email:         Email address (must be unique).
        password_hash: Bcrypt-hashed password string.

    Returns:
        The auto-generated integer ID of the new user.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)',
            (name, email, password_hash),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


def update_user_profile(user_id, name=None, bio=None, profile_picture=None):
    """Update a user's profile fields.

    Only updates the fields that are provided (not None).

    Args:
        user_id:         The user's integer ID.
        name:            New display name (optional).
        bio:             New bio text (optional).
        profile_picture: New profile picture path (optional).

    Returns:
        True if the update affected a row, False otherwise.
    """
    fields = []
    values = []
    if name is not None:
        fields.append('name = %s')
        values.append(name)
    if bio is not None:
        fields.append('bio = %s')
        values.append(bio)
    if profile_picture is not None:
        fields.append('profile_picture = %s')
        values.append(profile_picture)

    if not fields:
        return False

    values.append(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f'UPDATE users SET {", ".join(fields)} WHERE id = %s',
            tuple(values),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Post helpers
# ---------------------------------------------------------------------------

def get_posts_paginated(start=0, limit=10, user_id=None):
    """Return a paginated list of posts, joined with author info.

    Each post dict includes the author's email and name via an
    INNER JOIN on the users table.

    Args:
        start:   Pagination offset (default 0).
        limit:   Maximum number of posts to return (default 10).
        user_id: If provided, return only posts by this author.

    Returns:
        A list of post dicts ordered by created_at descending.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if user_id:
            cursor.execute(
                'SELECT posts.id, posts.author_id AS userId, posts.title, '
                'posts.body, posts.image_url, posts.created_at, '
                'users.email, users.name AS authorName '
                'FROM posts '
                'JOIN users ON posts.author_id = users.id '
                'WHERE posts.author_id = %s '
                'ORDER BY posts.created_at DESC '
                'LIMIT %s OFFSET %s',
                (user_id, limit, start)
            )
        else:
            cursor.execute(
                'SELECT posts.id, posts.author_id AS userId, posts.title, '
                'posts.body, posts.image_url, posts.created_at, '
                'users.email, users.name AS authorName '
                'FROM posts '
                'JOIN users ON posts.author_id = users.id '
                'ORDER BY posts.created_at DESC '
                'LIMIT %s OFFSET %s',
                (limit, start)
            )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def create_post(author_id, title, body, image_url=''):
    """Insert a new post into the database.

    Args:
        author_id: The ID of the user creating the post.
        title:     Post title.
        body:      Post body text.
        image_url: Optional URL/path to an attached image.

    Returns:
        The auto-generated integer ID of the new post.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO posts (author_id, title, body, image_url) VALUES (%s, %s, %s, %s)',
            (author_id, title, body, image_url),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def create_session(user_id, expires_at):
    """Create a new session for a user and return the session UUID.

    Args:
        user_id:    The user's integer ID.
        expires_at: A datetime marking when the session becomes invalid.

    Returns:
        A 36-character UUID string representing the session ID.
    """
    session_id = str(uuid.uuid4())
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO sessions (id, user_id, expires_at) VALUES (%s, %s, %s)',
            (session_id, user_id, expires_at),
        )
        conn.commit()
        return session_id
    finally:
        cursor.close()
        conn.close()


def get_session(session_id):
    """Look up a session by its UUID.

    Args:
        session_id: The 36-character UUID string.

    Returns:
        A dict with id, user_id, and expires_at, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, user_id, expires_at FROM sessions WHERE id = %s',
            (session_id,),
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def delete_session(session_id):
    """Delete a single session (used for logout).

    Args:
        session_id: The 36-character UUID string to remove.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE id = %s', (session_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def delete_user_sessions(user_id):
    """Delete all sessions for a user (called before creating a new login session).

    Args:
        user_id: The user's integer ID.

    Returns:
        The number of sessions that were deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE user_id = %s', (user_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


def delete_expired_sessions():
    """Remove all sessions whose expires_at is in the past.

    Call this periodically (e.g. on startup or via a scheduled task)
    to prevent the sessions table from growing unbounded.

    Returns:
        The number of expired sessions that were deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM sessions WHERE expires_at < NOW()')
        conn.commit()
        return cursor.rowcount
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------------------
# Follow helpers
# ---------------------------------------------------------------------------

def follow_user(follower_id, following_id):
    """Create a follow relationship.

    Uses INSERT IGNORE to silently skip if the relationship already exists
    (prevented by the composite primary key).

    Args:
        follower_id:  The user who is following.
        following_id: The user being followed.

    Returns:
        True if a new follow was created, False if it already existed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT IGNORE INTO follows (follower_id, following_id) VALUES (%s, %s)',
            (follower_id, following_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def unfollow_user(follower_id, following_id):
    """Remove a follow relationship.

    Args:
        follower_id:  The user who is unfollowing.
        following_id: The user being unfollowed.

    Returns:
        True if a follow was removed, False if it didn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'DELETE FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()


def is_following(follower_id, following_id):
    """Check if one user follows another.

    Args:
        follower_id:  The potential follower.
        following_id: The potentially followed user.

    Returns:
        True if follower_id follows following_id, False otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT 1 FROM follows WHERE follower_id = %s AND following_id = %s',
            (follower_id, following_id),
        )
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def get_followers_count(user_id):
    """Return the number of users who follow this user.

    Args:
        user_id: The user whose follower count to retrieve.

    Returns:
        Integer count of followers.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT COUNT(*) FROM follows WHERE following_id = %s',
            (user_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def get_following_count(user_id):
    """Return the number of users this user follows.

    Args:
        user_id: The user whose following count to retrieve.

    Returns:
        Integer count of users being followed.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT COUNT(*) FROM follows WHERE follower_id = %s',
            (user_id,),
        )
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def get_followers(user_id):
    """Return the list of users who follow this user.

    Args:
        user_id: The user whose followers to retrieve.

    Returns:
        A list of user dicts (id, name, email, created_at).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT users.id, users.name, users.email, users.created_at '
            'FROM follows '
            'JOIN users ON follows.follower_id = users.id '
            'WHERE follows.following_id = %s '
            'ORDER BY follows.created_at DESC',
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_following(user_id):
    """Return the list of users this user follows.

    Args:
        user_id: The user whose following list to retrieve.

    Returns:
        A list of user dicts (id, name, email, created_at).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT users.id, users.name, users.email, users.created_at '
            'FROM follows '
            'JOIN users ON follows.following_id = users.id '
            'WHERE follows.follower_id = %s '
            'ORDER BY follows.created_at DESC',
            (user_id,),
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_following_posts_paginated(user_id, start=0, limit=10):
    """Return a paginated list of posts from users that the given user follows.

    Uses a JOIN across posts, users, and follows to filter posts to only
    those authored by users the current user follows.

    Args:
        user_id: The ID of the user whose following-feed to retrieve.
        start:   Pagination offset (default 0).
        limit:   Maximum number of posts to return (default 10).

    Returns:
        A list of post dicts ordered by created_at descending.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT posts.id, posts.author_id AS userId, posts.title, '
            'posts.body, posts.image_url, posts.created_at, '
            'users.email, users.name AS authorName '
            'FROM posts '
            'JOIN users ON posts.author_id = users.id '
            'JOIN follows ON posts.author_id = follows.following_id '
            'WHERE follows.follower_id = %s '
            'ORDER BY posts.created_at DESC '
            'LIMIT %s OFFSET %s',
            (user_id, limit, start)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

