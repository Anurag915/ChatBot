import pytest
from unittest.mock import patch, MagicMock
from app.services.health_service import get_health_status

@patch("app.services.health_service.get_settings")
def test_get_health_status(mock_get_settings):
    mock_get_settings.return_value.app_name = "Test App"
    response = get_health_status()
    assert response.status == "ok"
    assert response.service == "Test App"
