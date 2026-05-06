import pytest
from httpx import AsyncClient
from unittest.mock import patch
from app.services.chat_service import ChatProcessingError

@pytest.mark.asyncio
@patch("app.routes.chat.generate_answer")
async def test_chat_api_success(mock_generate, async_client: AsyncClient):
    mock_generate.return_value = {"answer": "Hi", "sources": [], "timestamps": []}
    
    response = await async_client.post("/chat", json={"query": "Hello", "file_id": "123"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Hi"

@pytest.mark.asyncio
@patch("app.routes.chat.generate_summary")
async def test_summarize_api_success(mock_generate, async_client: AsyncClient):
    mock_generate.return_value = "Summary text"
    
    response = await async_client.post("/summarize", json={"file_id": "123"})
    assert response.status_code == 200
    assert response.json()["summary"] == "Summary text"

@pytest.mark.asyncio
@patch("app.routes.chat.generate_answer", side_effect=ChatProcessingError("Error processing"))
async def test_chat_api_processing_error(mock_generate, async_client: AsyncClient):
    response = await async_client.post("/chat", json={"query": "Hello", "file_id": "123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Error processing"

@pytest.mark.asyncio
@patch("app.routes.chat.generate_answer", side_effect=Exception("Unexpected"))
async def test_chat_api_unexpected_error(mock_generate, async_client: AsyncClient):
    response = await async_client.post("/chat", json={"query": "Hello", "file_id": "123"})
    assert response.status_code == 500

@pytest.mark.asyncio
@patch("app.routes.chat.generate_summary", side_effect=ChatProcessingError("Error processing"))
async def test_summarize_api_processing_error(mock_generate, async_client: AsyncClient):
    response = await async_client.post("/summarize", json={"file_id": "123"})
    assert response.status_code == 400

@pytest.mark.asyncio
@patch("app.routes.chat.generate_summary", side_effect=Exception("Unexpected"))
async def test_summarize_api_unexpected_error(mock_generate, async_client: AsyncClient):
    response = await async_client.post("/summarize", json={"file_id": "123"})
    assert response.status_code == 500
