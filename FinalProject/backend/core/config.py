"""Application configuration — environment variables, constants, and paths.

All environment-dependent settings are centralised here so that every
other module can import what it needs without calling load_dotenv itself.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

# backend/core/config.py  →  .parent = core/  →  .parent.parent = backend/
_BASE_DIR = Path(__file__).resolve().parent.parent        # backend/
_PROJECT_ROOT = _BASE_DIR.parent                          # myReact/

# Load .env from the project root (one level above backend/).
# override=True: the project's .env wins over variables already set in
# Windows (e.g. an old OPENAI_API_KEY saved in the system environment).
load_dotenv(_PROJECT_ROOT / '.env', override=True)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
DB_NAME = os.environ.get('DB_NAME', 'social_app')

# ---------------------------------------------------------------------------
# Flask / Security
# ---------------------------------------------------------------------------

SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'

# Set to 1 when running behind a reverse proxy (nginx in Docker/AWS) so Flask
# uses the real client IP from X-Forwarded-For (needed by the rate limiter).
# Keep 0 otherwise, or clients could fake their IP with that header.
BEHIND_PROXY = os.environ.get('BEHIND_PROXY', '0') == '1'

# Rate limiting on/off (always on in real use; the test suite switches it off)
RATELIMIT_ENABLED = os.environ.get('RATELIMIT_ENABLED', '1') == '1'

# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

SESSION_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds

# ---------------------------------------------------------------------------
# Email (Resend — https://resend.com) — leave RESEND_API_KEY empty to print
# emails to the console instead of sending them (dev mode).
# The test sender 'onboarding@resend.dev' can only deliver to the email
# address the Resend account was registered with.
# ---------------------------------------------------------------------------

RESEND_API_KEY = os.environ.get('RESEND_API_KEY', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'SocialApp <onboarding@resend.dev>')

# ---------------------------------------------------------------------------
# OpenAI — used for toxic-content moderation (and later AI features).
# Leave empty to skip moderation (content is allowed, a warning is printed).
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
# Chat model used by the AI Assist features (cheap + fast by default)
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4.1-mini')

# Agents (bots): seconds between two agent actions in run_agents.py.
# Each action costs at most one small OpenAI request.
AGENT_INTERVAL_SECONDS = int(os.environ.get('AGENT_INTERVAL_SECONDS', '60'))

# Browser origins allowed to call the API with cookies (comma-separated).
# Only needed when the frontend runs on a different origin (Vite dev server);
# in Docker/production nginx serves frontend + API from the same origin.
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:5173').split(',')

# Frontend URL used to build links inside emails (e.g. password reset)
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

# ---------------------------------------------------------------------------
# File Uploads
# ---------------------------------------------------------------------------

UPLOAD_FOLDER = _BASE_DIR / 'static' / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
(UPLOAD_FOLDER / 'profiles').mkdir(exist_ok=True)
(UPLOAD_FOLDER / 'posts').mkdir(exist_ok=True)
(UPLOAD_FOLDER / 'videos').mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB (images)

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm'}
MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB

# Flask rejects any request body bigger than this with 413 before reading it
MAX_CONTENT_LENGTH = MAX_VIDEO_SIZE + 1024 * 1024
