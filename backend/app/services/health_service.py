from app.core.config import get_settings
from app.models.health import HealthResponse


def get_health_status() -> HealthResponse:
    """Keep route handlers thin by placing response construction in a service."""

    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name)
