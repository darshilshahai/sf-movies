from fastapi import APIRouter, Depends, Query

from app.clients.datasf import DataSFClient
from app.schemas.movie import MovieListResponse, PaginationMeta
from app.services.movie_service import MovieService

router = APIRouter()


def get_movie_service() -> MovieService:
    """FastAPI dependency provider for MovieService instance."""
    client = DataSFClient()
    return MovieService(datasf_client=client)


@router.get(
    "",
    response_model=MovieListResponse,
    summary="List SF Movie Filming Locations",
    description=(
        "Retrieves a paginated list of normalized movie filming locations in San Francisco "
        "with optional search (title or location) and release year filtering."
    ),
)
async def list_movies(
    limit: int = Query(
        100,
        ge=1,
        le=500,
        description="Maximum number of location records to return (1 to 500).",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of location records to skip for pagination.",
    ),
    search: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Case-insensitive search query matching movie title or filming location name.",
    ),
    title: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Exact movie title filter.",
    ),
    location: str | None = Query(
        None,
        min_length=1,
        max_length=100,
        description="Exact filming location name filter.",
    ),
    year: int | None = Query(
        None,
        ge=1900,
        le=2100,
        description="Filter locations by film release year (1900 to 2100).",
    ),
    service: MovieService = Depends(get_movie_service),
) -> MovieListResponse:
    """Thin API route handler for GET /api/v1/movies."""
    normalized_locations = await service.get_movie_locations(
        search=search,
        title=title,
        location=location,
        year=year,
        limit=limit,
        offset=offset,
    )

    return MovieListResponse(
        data=normalized_locations,
        meta=PaginationMeta(
            count=len(normalized_locations),
            limit=limit,
            offset=offset,
        ),
    )
