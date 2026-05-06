import pytest
from httpx import AsyncClient
from unittest.mock import patch

@pytest.mark.asyncio
@patch("app.routes.upload.save_upload_file")
@patch("app.routes.upload.extract_text")
@patch("app.routes.upload.store_extracted_text")
@patch("app.routes.upload.process_document")
async def test_upload_api_success(mock_process, mock_store, mock_extract, mock_save, async_client: AsyncClient):
    class FakeStored:
        file_path = "/tmp/fake.pdf"
        file_id = "123"
        file_name = "test.pdf"
        file_type = "pdf"
    
    mock_save.return_value = FakeStored()
    
    from app.models.upload import ExtractedTextResponse
    mock_extract.return_value = ExtractedTextResponse(text="Hello", chunks=[])
    mock_process.return_value = {"chunks": []}
    
    response = await async_client.post("/upload", files={"file": ("test.pdf", b"fake content", "application/pdf")})
    assert response.status_code == 201
    assert response.json()["file_id"] == "123"

@pytest.mark.asyncio
@patch("app.routes.upload.save_upload_file", side_effect=Exception("Unexpected"))
async def test_upload_api_unexpected_error(mock_save, async_client: AsyncClient):
    response = await async_client.post("/upload", files={"file": ("test.pdf", b"fake content", "application/pdf")})
    assert response.status_code == 500
