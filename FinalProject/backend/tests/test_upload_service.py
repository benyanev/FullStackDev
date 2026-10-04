"""Unit tests for services.upload_service — AAA pattern.

Uses Werkzeug's real ``FileStorage`` with in-memory bytes, and pytest's
``tmp_path`` as the upload folder, so nothing is written to static/uploads.
"""

import io
from unittest.mock import patch

import pytest
from werkzeug.datastructures import FileStorage

from core.exceptions import ValidationError
from services.upload_service import upload_file, upload_video

# Real first bytes ("magic numbers") for each allowed type
HEADERS = {
    "png": b"\x89PNG\r\n\x1a\n",
    "jpg": b"\xff\xd8\xff\xe0",
    "gif": b"GIF89a",
    "webp": b"RIFF\x00\x00\x00\x00WEBP",
    "mp4": b"\x00\x00\x00\x18ftypmp42",
    "webm": b"\x1a\x45\xdf\xa3",
}


def _file(name, size=10, content=None):
    """A FileStorage whose bytes start like a real file of that extension."""
    if content is None:
        header = HEADERS.get(name.rsplit(".", 1)[-1].lower(), b"")
        content = header + b"x" * max(0, size - len(header))
    return FileStorage(stream=io.BytesIO(content), filename=name)


def test_upload_saves_file_with_unique_name(tmp_path):
    # Arrange
    (tmp_path / "posts").mkdir()

    # Act
    with patch("services.upload_service.UPLOAD_FOLDER", tmp_path):
        url = upload_file(_file("Photo.JPG"), "posts")

    # Assert
    assert url.startswith("/static/uploads/posts/") and url.endswith(".jpg")
    saved = list((tmp_path / "posts").iterdir())
    assert len(saved) == 1 and saved[0].name == url.rsplit("/", 1)[1]


@pytest.mark.parametrize("file", [None, FileStorage(stream=io.BytesIO(b""), filename="")])
def test_upload_missing_file(file):
    # Act & Assert
    with pytest.raises(ValidationError, match="No file"):
        upload_file(file, "posts")


def test_upload_wrong_extension():
    # Act & Assert
    with pytest.raises(ValidationError, match="not allowed"):
        upload_file(_file("script.exe"), "posts")


def test_upload_too_large():
    # Act & Assert
    with patch("services.upload_service.MAX_FILE_SIZE", 5):
        with pytest.raises(ValidationError, match="too large"):
            upload_file(_file("big.png", size=20), "posts")


@pytest.mark.parametrize("ext", ["png", "jpg", "gif", "webp"])
def test_upload_accepts_real_images(tmp_path, ext):
    # Arrange
    (tmp_path / "posts").mkdir()

    # Act
    with patch("services.upload_service.UPLOAD_FOLDER", tmp_path):
        url = upload_file(_file(f"pic.{ext}"), "posts")

    # Assert
    assert url.endswith(f".{ext}")


@pytest.mark.parametrize("name, content", [
    ("fake.png", b"<html><script>alert(1)</script>"),   # HTML renamed to .png
    ("fake.jpg", b"MZ\x90\x00 a windows program"),       # program renamed to .jpg
])
def test_upload_rejects_content_that_does_not_match(name, content):
    # Act & Assert
    with pytest.raises(ValidationError, match="does not match"):
        upload_file(_file(name, content=content), "posts")


def test_upload_video_saved_in_videos_folder(tmp_path):
    # Arrange
    (tmp_path / "videos").mkdir()

    # Act
    with patch("services.upload_service.UPLOAD_FOLDER", tmp_path):
        url = upload_video(_file("clip.MP4", size=30))

    # Assert
    assert url.startswith("/static/uploads/videos/") and url.endswith(".mp4")
    assert len(list((tmp_path / "videos").iterdir())) == 1


def test_upload_video_rejects_images():
    # Act & Assert — the video endpoint only takes mp4/webm
    with pytest.raises(ValidationError, match="mp4, webm"):
        upload_video(_file("photo.jpg"))


def test_upload_video_has_its_own_size_limit():
    # Act & Assert
    with patch("services.upload_service.MAX_VIDEO_SIZE", 5):
        with pytest.raises(ValidationError, match="too large"):
            upload_video(_file("clip.webm", size=20))


def test_upload_video_rejects_fake_mp4():
    # Act & Assert
    with pytest.raises(ValidationError, match="does not match"):
        upload_video(_file("clip.mp4", content=b"just some text, not a video"))
