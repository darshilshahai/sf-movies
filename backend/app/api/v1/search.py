from fastapi import APIRouter, Depends, Query

from app.api.v1.movies import get_movie_service
from app.schemas.search import SearchSuggestionsResponse
from app.services.movie_service import MovieService

router = APIRouter()


@router.get(
    "/suggestions",
    response_model=SearchSuggestionsResponse,
    summary="Get Autocomplete Suggestions",
    description="Get movie title and filming-location autocomplete suggestions based on search query.",
)
async def get_search_suggestions(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Search query string (minimum 2 characters).",
    ),
    limit: int = Query(
        8,
        ge=1,
        le=15,
        description="Maximum number of suggestions to return (1 to 15, default 8).",
    ),
    service: MovieService = Depends(get_movie_service),
) -> SearchSuggestionsResponse:

    query = q.strip()
    if len(query) < 2:
        return SearchSuggestionsResponse(data=[])

    suggestions = await service.get_search_suggestions(
        query=query,
        limit=limit,
    )
    return SearchSuggestionsResponse(data=suggestions)
