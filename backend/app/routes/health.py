from fastapi import APIRouter

from app.models.health import HealthResponse
from app.services.health_service import get_health_status


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return a basic API health status."""

    return get_health_status()
