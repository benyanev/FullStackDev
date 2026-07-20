"""File upload helpers — extension validation and constants.

Extracted from the old monolithic ``app.py`` so that both the upload
service and any future file-handling code can share the same logic.
"""

from core.config import ALLOWED_EXTENSIONS


def allowed_file(filename):
    """Return ``True`` if *filename* has an allowed image extension.

    Checks for a dot in the name and verifies the lowercased extension
    against :data:`core.config.ALLOWED_EXTENSIONS`.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
