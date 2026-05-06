import pytest
from unittest.mock import patch, MagicMock
from app.services.document_service import store_extracted_text

@pytest.mark.asyncio
async def test_store_extracted_text():
    mock_db = MagicMock()
    async def fake_insert(*args, **kwargs): pass
    mock_db.documents.insert_one = fake_insert
    
    mock_stored = MagicMock()
    mock_stored.file_id = "123"
    mock_stored.file_name = "test.pdf"
    mock_stored.file_path = "/tmp/test.pdf"
    
    mock_extraction = MagicMock()
    mock_extraction.text = "Hello"
    mock_extraction.chunks = []
    mock_extraction.segments = None
    
    res = await store_extracted_text(mock_db, mock_stored, mock_extraction)
    assert res is None
