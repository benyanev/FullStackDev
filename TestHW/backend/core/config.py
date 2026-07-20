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

# Load .env from the project root (one level above backend/)
load_dotenv(_PROJECT_ROOT / '.env')

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

# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

SESSION_MAX_AGE = 24 * 60 * 60  # 24 hours in seconds

# ---------------------------------------------------------------------------
# File Uploads
# ---------------------------------------------------------------------------

UPLOAD_FOLDER = _BASE_DIR / 'static' / 'uploads'
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
(UPLOAD_FOLDER / 'profiles').mkdir(exist_ok=True)
(UPLOAD_FOLDER / 'posts').mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
