import pytest
from unittest.mock import patch, MagicMock
from app.services.chat_service import generate_answer, generate_summary, ChatProcessingError

@patch("app.services.chat_service.Path")
@patch("app.services.chat_service.FAISS")
@patch("app.services.chat_service.ChatGroq")
@patch("app.services.chat_service._get_embeddings")
def test_generate_answer(mock_get_emb, mock_chat_groq, mock_faiss, mock_path):
    mock_path.return_value.exists.return_value = True
    
    mock_doc = MagicMock()
    mock_doc.page_content = "Chunk content"
    mock_doc.metadata = {"timestamps": {"start": 0.0, "end": 1.0}}
    
    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = [mock_doc]
    mock_faiss.load_local.return_value = mock_vector_store
    
    mock_response = MagicMock()
    mock_response.content = "Generated answer"
    
    with patch("app.services.chat_service.ChatPromptTemplate") as mock_prompt:
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_response
        mock_prompt.from_template.return_value.__or__.return_value = mock_chain
        
        res = generate_answer("What is this?", "file-123")
        assert res["answer"] == "Generated answer"
        assert res["sources"] == ["Chunk content"]
        assert res["timestamps"] == [{"start": 0.0, "end": 1.0}]

@patch("app.services.chat_service.get_database")
@pytest.mark.asyncio
async def test_generate_summary_success(mock_get_db):
    mock_db = MagicMock()
    async def fake_find(*args, **kwargs): return {"text": "Document text"}
    mock_db.documents.find_one = fake_find
    mock_get_db.return_value = mock_db
    
    with patch("app.services.chat_service.ChatPromptTemplate") as mock_prompt, patch("app.services.chat_service.ChatGroq") as mock_groq:
        mock_chain = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Summary text"
        
        async def fake_ainvoke(*args, **kwargs): return mock_response
        mock_chain.ainvoke = fake_ainvoke
        
        mock_prompt.from_template.return_value.__or__.return_value = mock_chain
        
        summary = await generate_summary("file-123")
        assert summary == "Summary text"

@patch("app.services.chat_service.get_database")
@pytest.mark.asyncio
async def test_generate_summary_no_text(mock_get_db):
    mock_db = MagicMock()
    async def fake_find(*args, **kwargs): return None
    mock_db.documents.find_one = fake_find
    mock_get_db.return_value = mock_db
    
    with pytest.raises(ChatProcessingError):
        await generate_summary("file-123")

@patch("app.services.chat_service.get_settings")
def test_generate_answer_no_groq_key(mock_settings):
    mock_settings.return_value.groq_api_key = ""
    with pytest.raises(ChatProcessingError):
        generate_answer("query", "file-123")

@patch("app.services.chat_service.get_settings")
@patch("app.services.chat_service.Path")
def test_generate_answer_no_index(mock_path, mock_settings):
    mock_settings.return_value.groq_api_key = "fake-key"
    mock_path.return_value.exists.return_value = False
    with pytest.raises(ChatProcessingError):
        generate_answer("query", "file-123")

@patch("app.services.chat_service.get_settings")
@patch("app.services.chat_service.Path")
@patch("app.services.chat_service.FAISS")
@patch("app.services.chat_service._get_embeddings")
def test_generate_answer_exception(mock_get_emb, mock_faiss, mock_path, mock_settings):
    mock_settings.return_value.groq_api_key = "fake-key"
    mock_path.return_value.exists.return_value = True
    mock_faiss.load_local.side_effect = Exception("Load error")
    with pytest.raises(ChatProcessingError):
        generate_answer("query", "file-123")

@patch("app.services.chat_service.get_settings")
@pytest.mark.asyncio
async def test_generate_summary_no_groq_key(mock_settings):
    mock_settings.return_value.groq_api_key = ""
    with pytest.raises(ChatProcessingError):
        await generate_summary("file-123")

@patch("app.services.chat_service.get_settings")
@patch("app.services.chat_service.get_database")
@pytest.mark.asyncio
async def test_generate_summary_exception(mock_get_db, mock_settings):
    mock_settings.return_value.groq_api_key = "fake-key"
    mock_settings.return_value.groq_model = "llama-3-groq"
    mock_db = MagicMock()
    async def fake_find(*args): return {"text": "Hello"}
    mock_db.documents.find_one = fake_find
    mock_get_db.return_value = mock_db
    
    with patch("app.services.chat_service.ChatPromptTemplate") as mock_prompt:
        mock_chain = MagicMock()
        async def fake_ainvoke(*args, **kwargs): raise Exception("Invoke error")
        mock_chain.ainvoke = fake_ainvoke
        mock_prompt.from_template.return_value.__or__.return_value = mock_chain
        with pytest.raises(ChatProcessingError):
            await generate_summary("file-123")
