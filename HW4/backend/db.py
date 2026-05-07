"""Database helper module — provides CRUD functions for the users and posts tables."""

import os
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
        A dict with id, name, email, and created_at, or None if not found.
        The password_hash column is intentionally excluded.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, created_at FROM users WHERE id = %s',
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
        A list of user dicts (id, name, email, created_at).
        The password_hash column is excluded for safety.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            'SELECT id, name, email, created_at FROM users '
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
                'posts.body, posts.created_at, users.email, users.name AS authorName '
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
                'posts.body, posts.created_at, users.email, users.name AS authorName '
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


def create_post(author_id, title, body):
    """Insert a new post into the database.

    Args:
        author_id: The ID of the user creating the post.
        title:     Post title.
        body:      Post body text.

    Returns:
        The auto-generated integer ID of the new post.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO posts (author_id, title, body) VALUES (%s, %s, %s)',
            (author_id, title, body),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()
