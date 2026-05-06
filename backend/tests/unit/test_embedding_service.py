import pytest
from unittest.mock import patch, MagicMock
from app.services.embedding_service import _build_langchain_documents, process_document, DocumentProcessingError

def test_build_langchain_documents_with_segments():
    document = {
        "text": "Hello world.",
        "segments": [{"text": "Hello world.", "start": 0.0, "end": 1.0}]
    }
    docs = _build_langchain_documents("file-123", document)
    assert len(docs) == 1
    assert docs[0].page_content == "Hello world."
    assert docs[0].metadata["timestamps"]["start"] == 0.0

@patch("app.services.embedding_service._get_text_splitter")
def test_build_langchain_documents_without_segments(mock_get_splitter):
    mock_splitter = MagicMock()
    mock_splitter.split_text.return_value = ["Hello", "world."]
    mock_get_splitter.return_value = mock_splitter

    document = {"text": "Hello world."}
    docs = _build_langchain_documents("file-123", document)
    assert len(docs) == 2
    assert docs[0].page_content == "Hello"
    assert docs[0].metadata["timestamps"] is None

@patch("app.services.embedding_service._load_document")
@patch("app.services.embedding_service._build_langchain_documents")
@patch("app.services.embedding_service.run_in_threadpool")
@patch("app.services.embedding_service.get_settings")
@pytest.mark.asyncio
async def test_process_document(mock_settings, mock_run, mock_build, mock_load):
    mock_settings.return_value.embedding_model = "fake-model"
    mock_load.return_value = {"text": "Hello"}
    mock_doc = MagicMock()
    mock_doc.page_content = "Hello"
    mock_doc.metadata = {"chunk_index": 0, "timestamps": {"start": 0.0, "end": 1.0}}
    mock_build.return_value = [mock_doc]
    mock_run.return_value = "/tmp/index"
    
    mock_db = MagicMock()
    
    async def fake_delete(*args, **kwargs): pass
    async def fake_insert(*args, **kwargs): pass
    async def fake_update(*args, **kwargs): pass
    
    mock_db.document_chunks.delete_many = fake_delete
    mock_db.document_chunks.insert_many = fake_insert
    mock_db.documents.update_one = fake_update

    res = await process_document("file-123", mock_db)
    assert res["file_id"] == "file-123"
    assert res["chunk_count"] == 1
    assert res["chunks"][0]["start"] == 0.0

@patch("app.services.embedding_service.HuggingFaceEmbeddings")
def test_get_embeddings(mock_hfe):
    from app.services.embedding_service import _get_embeddings
    _get_embeddings.cache_clear()
    _get_embeddings()
    mock_hfe.assert_called_once()

def test_get_text_splitter():
    from app.services.embedding_service import _get_text_splitter
    splitter = _get_text_splitter()
    assert splitter is not None

@patch("app.services.embedding_service.FAISS")
@patch("app.services.embedding_service._get_embeddings")
def test_save_faiss_index(mock_get_emb, mock_faiss, tmp_path):
    from app.services.embedding_service import _save_faiss_index
    from langchain_core.documents import Document
    
    mock_emb = MagicMock()
    mock_get_emb.return_value = mock_emb
    
    mock_vs = MagicMock()
    mock_faiss.from_documents.return_value = mock_vs
    
    docs = [Document(page_content="test")]
    with patch("app.services.embedding_service.get_settings") as mock_settings:
        mock_settings.return_value.vector_store_dir = str(tmp_path)
        res = _save_faiss_index("file-123", docs)
        assert res == tmp_path / "file-123"
        mock_vs.save_local.assert_called_once()

def test_save_faiss_index_empty():
    from app.services.embedding_service import _save_faiss_index, DocumentProcessingError
    with pytest.raises(DocumentProcessingError):
        _save_faiss_index("file-123", [])

@pytest.mark.asyncio
async def test_load_document_not_found():
    from app.services.embedding_service import _load_document, DocumentProcessingError
    mock_db = MagicMock()
    async def fake_find(*args): return None
    mock_db.documents.find_one = fake_find
    with pytest.raises(DocumentProcessingError):
        await _load_document(mock_db, "file-123")

@pytest.mark.asyncio
async def test_load_document_no_text():
    from app.services.embedding_service import _load_document, DocumentProcessingError
    mock_db = MagicMock()
    async def fake_find(*args): return {"text": ""}
    mock_db.documents.find_one = fake_find
    with pytest.raises(DocumentProcessingError):
        await _load_document(mock_db, "file-123")
