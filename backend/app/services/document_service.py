from datetime import datetime, timezone
from pathlib import Path

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.upload import ExtractedTextResponse
from app.services.file_storage_service import StoredFile


async def store_extracted_text(
    database: AsyncIOMotorDatabase,
    stored_file: StoredFile,
    extraction: ExtractedTextResponse,
) -> None:
    """Persist uploaded file metadata and extracted text for later retrieval."""

    await database.documents.insert_one(
        {
            "file_id": stored_file.file_id,
            "file_name": stored_file.file_name,
            "file_type": stored_file.file_type,
            "file_path": str(Path(stored_file.file_path)),
            "text": extraction.text,
            "chunks": extraction.chunks,
            "segments": extraction.segments,
            "created_at": datetime.now(timezone.utc),
        }
    )
