import pytest
from fastapi.testclient import TestClient

from app.api.v1.movies import get_movie_service
from app.core.exceptions import UpstreamServiceException
from app.main import app
from app.schemas.search import SearchSuggestion
from app.services.movie_service import MovieService
from tests.test_movie_service import FakeDataSFClient


def test_search_suggestions_success():
    raw_data = [
        {"title": "Vertigo", "locations": "Mission Dolores"},
        {"title": "The Making of Vertigo", "locations": "Palace of Fine Arts"},
    ]
    fake_service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    app.dependency_overrides[get_movie_service] = lambda: fake_service

    try:
        client = TestClient(app)
        response = client.get("/api/v1/search/suggestions?q=vert")

        assert response.status_code == 200
        payload = response.json()
        assert "data" in payload
        assert isinstance(payload["data"], list)
        assert len(payload["data"]) == 2
        assert payload["data"][0] == {"value": "Vertigo", "type": "movie"}
        assert payload["data"][1] == {"value": "The Making of Vertigo", "type": "movie"}
    finally:
        app.dependency_overrides.clear()


def test_search_suggestions_missing_query():
    client = TestClient(app)
    response = client.get("/api/v1/search/suggestions")
    assert response.status_code == 422


def test_search_suggestions_query_too_short():
    client = TestClient(app)
    response = client.get("/api/v1/search/suggestions?q=a")
    assert response.status_code == 422


def test_search_suggestions_query_too_long():
    client = TestClient(app)
    long_query = "a" * 101
    response = client.get(f"/api/v1/search/suggestions?q={long_query}")
    assert response.status_code == 422


def test_search_suggestions_custom_valid_limit():
    raw_data = [
        {"title": f"Movie {i}", "locations": f"Location {i}"}
        for i in range(10)
    ]
    fake_service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    app.dependency_overrides[get_movie_service] = lambda: fake_service

    try:
        client = TestClient(app)
        response = client.get("/api/v1/search/suggestions?q=movie&limit=3")

        assert response.status_code == 200
        payload = response.json()
        assert len(payload["data"]) == 3
    finally:
        app.dependency_overrides.clear()


def test_search_suggestions_invalid_limit_zero():
    client = TestClient(app)
    response = client.get("/api/v1/search/suggestions?q=vert&limit=0")
    assert response.status_code == 422


def test_search_suggestions_invalid_limit_exceeds_max():
    client = TestClient(app)
    response = client.get("/api/v1/search/suggestions?q=vert&limit=20")
    assert response.status_code == 422


def test_search_suggestions_empty_results():
    fake_service = MovieService(datasf_client=FakeDataSFClient(records=[]))
    app.dependency_overrides[get_movie_service] = lambda: fake_service

    try:
        client = TestClient(app)
        response = client.get("/api/v1/search/suggestions?q=nonexistent")

        assert response.status_code == 200
        payload = response.json()
        assert payload == {"data": []}
    finally:
        app.dependency_overrides.clear()


def test_search_suggestions_upstream_failure():
    fake_service = MovieService(
        datasf_client=FakeDataSFClient(
            raise_exc=UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message="Unable to retrieve search suggestions.",
            )
        )
    )
    app.dependency_overrides[get_movie_service] = lambda: fake_service

    try:
        client = TestClient(app)
        response = client.get("/api/v1/search/suggestions?q=vert")

        assert response.status_code == 502
        payload = response.json()
        assert payload["error"]["code"] == "UPSTREAM_SERVICE_ERROR"
        assert payload["error"]["message"] == "Unable to retrieve search suggestions."
    finally:
        app.dependency_overrides.clear()


def test_search_suggestions_whitespace_trimmed_short():
    raw_data = [{"title": "Vertigo", "locations": "Mission Dolores"}]
    fake_service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    app.dependency_overrides[get_movie_service] = lambda: fake_service

    try:
        client = TestClient(app)
        response = client.get("/api/v1/search/suggestions?q=%20a%20")

        assert response.status_code == 200
        payload = response.json()
        assert payload == {"data": []}
    finally:
        app.dependency_overrides.clear()
