from functools import lru_cache
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from motor.motor_asyncio import AsyncIOMotorDatabase
from starlette.concurrency import run_in_threadpool

from app.core.config import get_settings
from app.db.mongodb import get_database


class DocumentProcessingError(RuntimeError):
    """Raised when chunking or embedding generation fails."""


@lru_cache
def _get_embeddings() -> HuggingFaceEmbeddings:
    """Load the HuggingFace embedding model once per process."""

    settings = get_settings()
    return HuggingFaceEmbeddings(model_name=settings.embedding_model)


def _get_text_splitter() -> RecursiveCharacterTextSplitter:
    """Create the LangChain splitter from environment-backed settings."""

    settings = get_settings()
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )


async def _load_document(database: AsyncIOMotorDatabase, file_id: str) -> dict:
    """Fetch a processed upload record by file_id."""

    document = await database.documents.find_one({"file_id": file_id})
    if document is None:
        raise DocumentProcessingError(f"Document not found for file_id: {file_id}")

    if not document.get("text"):
        raise DocumentProcessingError("Document has no extracted text to process")

    return document


def _build_langchain_documents(file_id: str, document: dict) -> list[Document]:
    """Split extracted text into LangChain documents with chunk metadata."""

    segments = document.get("segments")
    if segments:
        return [
            Document(
                page_content=seg["text"].strip(),
                metadata={
                    "file_id": file_id,
                    "chunk_index": index,
                    "chunk_text": seg["text"].strip(),
                    "timestamps": {"start": seg["start"], "end": seg["end"]}
                }
            )
            for index, seg in enumerate(segments)
            if seg["text"].strip()
        ]

    splitter = _get_text_splitter()
    chunks = splitter.split_text(document["text"])

    return [
        Document(
            page_content=chunk,
            metadata={
                "file_id": file_id,
                "chunk_index": index,
                "chunk_text": chunk,
                "timestamps": None,
            },
        )
        for index, chunk in enumerate(chunks)
    ]


def _save_faiss_index(file_id: str, documents: list[Document]) -> Path:
    """Generate embeddings and save a FAISS index locally."""

    if not documents:
        raise DocumentProcessingError("No text chunks were generated")

    settings = get_settings()
    index_dir = Path(settings.vector_store_dir) / file_id
    index_dir.mkdir(parents=True, exist_ok=True)

    vector_store = FAISS.from_documents(documents, _get_embeddings())
    vector_store.save_local(str(index_dir))

    return index_dir


async def process_document(
    file_id: str,
    database: AsyncIOMotorDatabase | None = None,
) -> dict:
    """Split extracted text, embed chunks, store FAISS index, and save metadata."""

    database = database if database is not None else get_database()
    document = await _load_document(database, file_id)
    langchain_documents = _build_langchain_documents(file_id, document)
    index_dir = await run_in_threadpool(
        _save_faiss_index,
        file_id,
        langchain_documents,
    )

    chunk_metadata = [
        {
            "file_id": file_id,
            "chunk_index": item.metadata["chunk_index"],
            "chunk_text": item.page_content,
            "timestamps": item.metadata.get("timestamps"),
        }
        for item in langchain_documents
    ]

    if chunk_metadata:
        await database.document_chunks.delete_many({"file_id": file_id})
        await database.document_chunks.insert_many(chunk_metadata)

    chunk_objects = [
        {
            "text": item["chunk_text"],
            "start": item["timestamps"].get("start") if item.get("timestamps") else None,
            "end": item["timestamps"].get("end") if item.get("timestamps") else None,
        }
        for item in chunk_metadata
    ]
    await database.documents.update_one(
        {"file_id": file_id},
        {
            "$set": {
                "chunks": chunk_objects,
                "faiss_index_path": str(index_dir),
                "embedding_model": get_settings().embedding_model,
            }
        },
    )

    return {
        "file_id": file_id,
        "chunks": chunk_objects,
        "chunk_count": len(chunk_objects),
        "faiss_index_path": str(index_dir),
    }
