from fastapi import APIRouter
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns application health status."""
    return HealthResponse(
        status="healthy",
        service="sf-movies-api"
    )
