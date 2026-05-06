from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import get_settings


ALLOWED_FILE_TYPES = {
    "application/pdf": "pdf",
    "audio/mpeg": "audio",
    "audio/mp3": "audio",
    "audio/wav": "audio",
    "audio/x-wav": "audio",
    "audio/mp4": "audio",
    "audio/aac": "audio",
    "audio/ogg": "audio",
    "video/mp4": "video",
    "video/mpeg": "video",
    "video/quicktime": "video",
    "video/x-msvideo": "video",
    "video/x-matroska": "video",
    "video/webm": "video",
}

ALLOWED_EXTENSIONS = {
    ".pdf": "pdf",
    ".mp3": "audio",
    ".wav": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    ".ogg": "audio",
    ".mp4": "video",
    ".mpeg": "video",
    ".mpg": "video",
    ".mov": "video",
    ".avi": "video",
    ".mkv": "video",
    ".webm": "video",
}


class UnsupportedFileTypeError(ValueError):
    """Raised when an uploaded file does not match supported media types."""


@dataclass(frozen=True)
class StoredFile:
    file_id: str
    file_name: str
    file_type: str
    file_path: Path


def get_upload_file_type(file: UploadFile) -> str:
    """Validate content type and extension, returning the normalized file type."""

    suffix = Path(file.filename or "").suffix.lower()
    extension_type = ALLOWED_EXTENSIONS.get(suffix)
    content_type = ALLOWED_FILE_TYPES.get(file.content_type or "")

    if extension_type is None or content_type is None:
        raise UnsupportedFileTypeError("Only PDF, audio, and video files are supported")

    if extension_type != content_type:
        raise UnsupportedFileTypeError("File extension does not match the uploaded media type")

    return content_type


async def save_upload_file(file: UploadFile) -> StoredFile:
    """Persist an uploaded file locally and return metadata needed by services."""

    file_type = get_upload_file_type(file)
    file_id = str(uuid4())
    original_name = Path(file.filename or "uploaded_file").name
    suffix = Path(original_name).suffix.lower()

    settings = get_settings()
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    destination = upload_dir / f"{file_id}{suffix}"

    with destination.open("wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            buffer.write(chunk)

    await file.close()

    return StoredFile(
        file_id=file_id,
        file_name=original_name,
        file_type=file_type,
        file_path=destination,
    )
