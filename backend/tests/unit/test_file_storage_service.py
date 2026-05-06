import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.file_storage_service import get_upload_file_type, save_upload_file, UnsupportedFileTypeError
from fastapi import UploadFile

def test_get_upload_file_type_success():
    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.content_type = "application/pdf"
    file_type = get_upload_file_type(file)
    assert file_type == "pdf"

def test_get_upload_file_type_unsupported():
    file = MagicMock(spec=UploadFile)
    file.filename = "test.txt"
    file.content_type = "text/plain"
    with pytest.raises(UnsupportedFileTypeError):
        get_upload_file_type(file)

def test_get_upload_file_type_mismatch():
    file = MagicMock(spec=UploadFile)
    file.filename = "test.pdf"
    file.content_type = "audio/mpeg"
    with pytest.raises(UnsupportedFileTypeError):
        get_upload_file_type(file)

@patch("app.services.file_storage_service.get_settings")
@pytest.mark.asyncio
async def test_save_upload_file(mock_settings, tmp_path):
    mock_settings.return_value.upload_dir = str(tmp_path)
    
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.pdf"
    mock_file.content_type = "application/pdf"
    mock_file.read = AsyncMock(side_effect=[b"chunk", b""])
    mock_file.close = AsyncMock()
    
    stored = await save_upload_file(mock_file)
    
    assert stored.file_name == "test.pdf"
    assert stored.file_type == "pdf"
    assert stored.file_path.parent == tmp_path
    assert stored.file_path.exists()
    assert stored.file_path.read_text() == "chunk"
