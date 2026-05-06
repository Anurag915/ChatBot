import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from mongomock_motor import AsyncMongoMockClient

from app.main import app
from app.core.config import Settings, get_settings
from app.db.mongodb import get_database, mongodb
from app.routes.auth import get_current_user

os.environ["GROQ_API_KEY"] = "fake-key"
os.environ["VECTOR_STORE_DIR"] = "/tmp/fake_vector_store"

@pytest.fixture(autouse=True)
def override_get_current_user():
    app.dependency_overrides[get_current_user] = lambda: {"username": "test_user"}
    yield
    app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def mock_settings():
    return Settings(
        app_name="Test App",
        app_env="testing",
        groq_api_key="fake-test-key",
        vector_store_dir="/tmp/fake_vector_store"
    )

@pytest.fixture
def override_get_settings(mock_settings):
    app.dependency_overrides[get_settings] = lambda: mock_settings
    yield mock_settings
    app.dependency_overrides.pop(get_settings, None)

@pytest_asyncio.fixture
async def mock_db():
    client = AsyncMongoMockClient()
    db = client.test_db
    mongodb.client = client
    mongodb.database = db
    
    app.dependency_overrides[get_database] = lambda: db
    yield db
    app.dependency_overrides.pop(get_database, None)

@pytest_asyncio.fixture
async def async_client(override_get_settings, mock_db):
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as client:
        yield client
