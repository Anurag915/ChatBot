import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_lifespan():
    from app.main import lifespan
    mock_app = MagicMock()
    with patch("app.main.connect_to_mongo", new_callable=AsyncMock) as mock_connect, \
         patch("app.main.close_mongo_connection", new_callable=AsyncMock) as mock_close:
        async with lifespan(mock_app):
            pass
        mock_connect.assert_called_once()
        mock_close.assert_called_once()
