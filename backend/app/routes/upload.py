from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.concurrency import run_in_threadpool

from app.db.mongodb import get_database
from app.models.upload import UploadResponse
from app.routes.auth import get_current_user
from app.services.document_service import store_extracted_text
from app.services.file_storage_service import (
    UnsupportedFileTypeError,
    save_upload_file,
)
from app.services.embedding_service import DocumentProcessingError, process_document
from app.services.text_extraction_service import TextExtractionError, extract_text


router = APIRouter(tags=["Upload"])


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    database: AsyncIOMotorDatabase = Depends(get_database),
    current_user: dict = Depends(get_current_user),
) -> UploadResponse:
    """Validate, store, extract text from, and persist an uploaded file."""

    try:
        stored_file = await save_upload_file(file)
        extraction = await run_in_threadpool(extract_text, stored_file.file_path)
        await store_extracted_text(database, stored_file, extraction)
        processing_result = await process_document(stored_file.file_id, database)
        extraction.chunks = processing_result["chunks"]

        return UploadResponse(
            file_id=stored_file.file_id,
            file_name=stored_file.file_name,
            file_type=stored_file.file_type,
            extraction=extraction,
        )
    except UnsupportedFileTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except TextExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
