from fastapi.testclient import TestClient
from app.api.v1.movies import get_movie_service
from app.core.exceptions import UpstreamServiceException
from app.main import app
from app.schemas.movie import Coordinates, MovieLocation

client = TestClient(app)


class MockMovieService:
    """Mock MovieService for deterministic route integration tests."""

    def __init__(self, locations: list[MovieLocation] | None = None, raise_exc: Exception | None = None) -> None:
        self._locations = locations or []
        self._raise_exc = raise_exc
        self.last_query: dict = {}

    async def get_movie_locations(
        self,
        *,
        search: str | None = None,
        title: str | None = None,
        location: str | None = None,
        year: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MovieLocation]:
        self.last_query = {
            "search": search,
            "title": title,
            "location": location,
            "year": year,
            "limit": limit,
            "offset": offset,
        }
        if self._raise_exc:
            raise self._raise_exc
        return self._locations


def test_list_movies_success():
    """Test 1: GET /api/v1/movies returns 200 OK with correct envelope structure."""
    sample_location = MovieLocation(
        title="Vertigo",
        release_year=1958,
        location="Mission Dolores",
        coordinates=Coordinates(latitude=37.7643, longitude=-122.4269),
        director="Alfred Hitchcock",
        actors=["James Stewart", "Kim Novak"],
    )
    mock_service = MockMovieService(locations=[sample_location])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies")
        assert response.status_code == 200

        body = response.json()
        assert "data" in body
        assert "meta" in body
        assert body["meta"]["count"] == 1
        assert body["meta"]["limit"] == 100
        assert body["meta"]["offset"] == 0

        first_item = body["data"][0]
        assert first_item["title"] == "Vertigo"
        assert first_item["release_year"] == 1958
        assert first_item["location"] == "Mission Dolores"
        assert first_item["coordinates"] == {"latitude": 37.7643, "longitude": -122.4269}
        assert first_item["actors"] == ["James Stewart", "Kim Novak"]
    finally:
        app.dependency_overrides.clear()


def test_list_movies_pagination_params():
    """Test 2: Pagination query parameters (limit and offset) reach the service and reflect in meta."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?limit=25&offset=50")
        assert response.status_code == 200

        body = response.json()
        assert body["meta"]["limit"] == 25
        assert body["meta"]["offset"] == 50

        assert mock_service.last_query["limit"] == 25
        assert mock_service.last_query["offset"] == 50
    finally:
        app.dependency_overrides.clear()


def test_list_movies_search_param():
    """Test 3: Search query parameter reaches the service layer."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?search=vertigo")
        assert response.status_code == 200
        assert mock_service.last_query["search"] == "vertigo"
    finally:
        app.dependency_overrides.clear()


def test_list_movies_year_param():
    """Test 4: Release year query parameter reaches the service layer."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?year=1958")
        assert response.status_code == 200
        assert mock_service.last_query["year"] == 1958
    finally:
        app.dependency_overrides.clear()


def test_list_movies_empty_results():
    """Test 5: Empty search match returns 200 OK with data: [] and count: 0 (not 404)."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?search=nonexistent")
        assert response.status_code == 200

        body = response.json()
        assert body["data"] == []
        assert body["meta"]["count"] == 0
    finally:
        app.dependency_overrides.clear()


def test_list_movies_invalid_limit_zero():
    """Test 6: Query limit < 1 fails validation with HTTP 422."""
    response = client.get("/api/v1/movies?limit=0")
    assert response.status_code == 422


def test_list_movies_invalid_limit_exceeded():
    """Test 7: Query limit > 500 fails validation with HTTP 422."""
    response = client.get("/api/v1/movies?limit=1000")
    assert response.status_code == 422


def test_list_movies_invalid_offset():
    """Test 8: Query offset < 0 fails validation with HTTP 422."""
    response = client.get("/api/v1/movies?offset=-1")
    assert response.status_code == 422


def test_list_movies_search_too_long():
    """Test 9: Search parameter exceeding max length (100) fails validation with HTTP 422."""
    too_long_query = "a" * 101
    response = client.get(f"/api/v1/movies?search={too_long_query}")
    assert response.status_code == 422


def test_list_movies_upstream_error_propagation():
    """Test 10: Upstream error in service raises UpstreamServiceException mapped to HTTP 502 response."""
    mock_service = MockMovieService(
        raise_exc=UpstreamServiceException(
            code="UPSTREAM_SERVICE_ERROR",
            message="DataSF is unreachable.",
        )
    )
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies")
        assert response.status_code == 502

        body = response.json()
        assert body == {
            "error": {
                "code": "UPSTREAM_SERVICE_ERROR",
                "message": "DataSF is unreachable.",
            }
        }
    finally:
        app.dependency_overrides.clear()


def test_list_movies_title_param():
    """Test 11: Exact title query parameter reaches the service layer."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?title=Vertigo")
        assert response.status_code == 200
        assert mock_service.last_query["title"] == "Vertigo"
    finally:
        app.dependency_overrides.clear()


def test_list_movies_location_param():
    """Test 12: Exact location query parameter reaches the service layer."""
    mock_service = MockMovieService(locations=[])
    app.dependency_overrides[get_movie_service] = lambda: mock_service

    try:
        response = client.get("/api/v1/movies?location=Golden%20Gate%20Bridge")
        assert response.status_code == 200
        assert mock_service.last_query["location"] == "Golden Gate Bridge"
    finally:
        app.dependency_overrides.clear()

