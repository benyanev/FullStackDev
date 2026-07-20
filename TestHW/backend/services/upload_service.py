"""Upload service — file validation, naming, and persistence.

Handles the business rules around file uploads (allowed extensions, size
limits, unique filename generation) without any HTTP awareness.  The
controller is responsible for extracting the file object from the Flask
request and passing it here.
"""

import uuid

from core.config import MAX_FILE_SIZE, UPLOAD_FOLDER
from core.exceptions import ValidationError
from utils.file_helpers import allowed_file


def upload_file(file, subfolder):
    """Validate and save an uploaded file.

    Args:
        file:      A Werkzeug ``FileStorage`` object from the request.
        subfolder: Sub-directory under ``UPLOAD_FOLDER`` (e.g. ``'profiles'``
                   or ``'posts'``).

    Returns:
        The URL path to the saved file (e.g.
        ``'/static/uploads/profiles/abc123.jpg'``).

    Raises:
        ValidationError: If the file is missing, has a disallowed extension,
                         or exceeds the size limit.
    """
    if file is None or file.filename == '':
        raise ValidationError('No file provided.')

    if not allowed_file(file.filename):
        raise ValidationError(
            'File type not allowed. Use png, jpg, gif, or webp.')

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        raise ValidationError('File too large. Maximum size is 5 MB.')

    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'{uuid.uuid4().hex}.{ext}'
    filepath = UPLOAD_FOLDER / subfolder / filename
    file.save(str(filepath))

    return f'/static/uploads/{subfolder}/{filename}'
