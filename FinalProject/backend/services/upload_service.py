"""Upload service — file validation, naming, and persistence.

Handles the business rules around file uploads (allowed extensions, size
limits, unique filename generation) without any HTTP awareness.  The
controller is responsible for extracting the file object from the Flask
request and passing it here.

Images (posts, profile pictures) and videos (posts) share the same logic
and differ only in the allowed extensions and the size limit.
"""

import uuid

from core.config import (
    ALLOWED_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_VIDEO_SIZE,
    UPLOAD_FOLDER,
)
from core.exceptions import ValidationError
from utils.file_helpers import allowed_file


def _content_matches(header, ext):
    """Check the file's first bytes ("magic number") match its extension,
    so e.g. a renamed .exe or .html can't be uploaded as .png/.mp4."""
    if ext == 'png':
        return header.startswith(b'\x89PNG\r\n\x1a\n')
    if ext in ('jpg', 'jpeg'):
        return header.startswith(b'\xff\xd8\xff')
    if ext == 'gif':
        return header[:6] in (b'GIF87a', b'GIF89a')
    if ext == 'webp':
        return header[:4] == b'RIFF' and header[8:12] == b'WEBP'
    if ext == 'mp4':
        return header[4:8] == b'ftyp'
    if ext == 'webm':
        return header.startswith(b'\x1a\x45\xdf\xa3')
    return False


def _save_upload(file, subfolder, allowed_extensions, max_size):
    """Validate *file* against the rules and save it under a unique name.

    Returns:
        The URL path to the saved file (e.g. ``'/static/uploads/posts/abc.jpg'``).

    Raises:
        ValidationError: If the file is missing, has a disallowed extension,
                         its content doesn't match the extension, or it
                         exceeds the size limit.
    """
    if file is None or file.filename == '':
        raise ValidationError('No file provided.')

    if not allowed_file(file.filename, allowed_extensions):
        raise ValidationError(
            f'File type not allowed. Use {", ".join(sorted(allowed_extensions))}.')

    # Check file size
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > max_size:
        raise ValidationError(
            f'File too large. Maximum size is {max_size // (1024 * 1024)} MB.')

    ext = file.filename.rsplit('.', 1)[1].lower()
    header = file.read(16)
    file.seek(0)
    if not _content_matches(header, ext):
        raise ValidationError('The file content does not match its type.')

    # Generate unique filename
    filename = f'{uuid.uuid4().hex}.{ext}'
    filepath = UPLOAD_FOLDER / subfolder / filename
    file.save(str(filepath))

    return f'/static/uploads/{subfolder}/{filename}'


def upload_file(file, subfolder):
    """Validate and save an uploaded image (max 5 MB).

    Args:
        file:      A Werkzeug ``FileStorage`` object from the request.
        subfolder: Sub-directory under ``UPLOAD_FOLDER`` (``'profiles'``
                   or ``'posts'``).

    Returns:
        The URL path to the saved image.
    """
    return _save_upload(file, subfolder, ALLOWED_EXTENSIONS, MAX_FILE_SIZE)


def upload_video(file):
    """Validate and save an uploaded post video (mp4/webm, max 50 MB).

    Args:
        file: A Werkzeug ``FileStorage`` object from the request.

    Returns:
        The URL path to the saved video (``/static/uploads/videos/...``).
    """
    return _save_upload(file, 'videos', ALLOWED_VIDEO_EXTENSIONS, MAX_VIDEO_SIZE)
