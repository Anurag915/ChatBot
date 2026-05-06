from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings
from app.models.upload import ExtractedTextResponse
from app.services.file_storage_service import ALLOWED_EXTENSIONS


class TextExtractionError(RuntimeError):
    """Raised when text extraction fails for a supported file."""


def _extract_pdf_text(file_path: Path) -> str:
    """Extract readable text from a PDF using PyMuPDF."""

    try:
        import fitz
    except ImportError as exc:
        raise TextExtractionError("PyMuPDF is not installed") from exc

    text_parts: list[str] = []

    try:
        with fitz.open(file_path) as document:
            for page in document:
                page_text = page.get_text("text").strip()
                if page_text:
                    text_parts.append(page_text)
    except Exception as exc:
        raise TextExtractionError("Failed to extract text from PDF") from exc

    return "\n\n".join(text_parts)


@lru_cache
def _get_whisper_model():
    """Load the local Whisper model once and reuse it across requests."""

    try:
        import whisper
    except ImportError as exc:
        raise TextExtractionError("Whisper is not installed") from exc

    settings = get_settings()
    return whisper.load_model(settings.whisper_model)


def _transcribe_media(file_path: Path) -> tuple[str, list[dict]]:
    """Transcribe audio or video locally using Whisper."""

    try:
        model = _get_whisper_model()
        result = model.transcribe(str(file_path))
    except Exception as exc:
        raise TextExtractionError("Failed to transcribe media with Whisper") from exc

    text = str(result.get("text", "")).strip()
    segments = result.get("segments", [])
    clean_segments = [
        {"text": s["text"], "start": s["start"], "end": s["end"]}
        for s in segments
    ]
    return text, clean_segments


def extract_text(file_path: str | Path) -> ExtractedTextResponse:
    """Extract text from a PDF, audio file, or video file.

    Chunking is intentionally left empty until embeddings are implemented.
    """

    path = Path(file_path)
    suffix = path.suffix.lower()
    file_type = ALLOWED_EXTENSIONS.get(suffix)

    segments = None

    if file_type == "pdf":
        text = _extract_pdf_text(path)
    elif file_type in {"audio", "video"}:
        text, segments = _transcribe_media(path)
    else:
        raise TextExtractionError("Unsupported file type for text extraction")

    return ExtractedTextResponse(text=text, chunks=[], segments=segments)
