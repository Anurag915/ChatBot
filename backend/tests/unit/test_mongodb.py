import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.db.mongodb import connect_to_mongo, close_mongo_connection, mongodb, get_database

@patch("app.db.mongodb.AsyncIOMotorClient")
@patch("app.db.mongodb.get_settings")
@pytest.mark.asyncio
async def test_connect_to_mongo(mock_settings, mock_client):
    mock_settings.return_value.mongo_uri = "mongodb://localhost:27017"
    mock_settings.return_value.mongo_db_name = "test_db"
    
    mock_client_instance = MagicMock()
    mock_client_instance.admin.command = AsyncMock()
    mock_client.return_value = mock_client_instance
    
    await connect_to_mongo()
    
    assert mongodb.client is not None
    assert mongodb.database is not None

@pytest.mark.asyncio
async def test_close_mongo_connection():
    mongodb.client = MagicMock()
    await close_mongo_connection()
    assert mongodb.client is None
    assert mongodb.database is None

def test_get_database_error():
    mongodb.database = None
    with pytest.raises(RuntimeError):
        get_database()
