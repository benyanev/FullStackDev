"""File upload helpers — extension validation and constants.

Extracted from the old monolithic ``app.py`` so that both the upload
service and any future file-handling code can share the same logic.
"""

import re

from core.config import ALLOWED_EXTENSIONS


def allowed_file(filename, allowed_extensions=ALLOWED_EXTENSIONS):
    """Return ``True`` if *filename* has one of the allowed extensions.

    Checks for a dot in the name and verifies the lowercased extension
    against *allowed_extensions* (images by default:
    :data:`core.config.ALLOWED_EXTENSIONS`).
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def is_upload_url(url, subfolder):
    """Return ``True`` if *url* is a file this app saved in *subfolder*.

    Upload URLs always look like ``/static/uploads/<subfolder>/<32 hex>.<ext>``
    (see :mod:`services.upload_service`). Anything else — e.g. an external
    tracking image — is rejected.
    """
    return re.fullmatch(
        rf'/static/uploads/{subfolder}/[0-9a-f]{{32}}\.[a-z0-9]{{3,4}}', url) is not None
