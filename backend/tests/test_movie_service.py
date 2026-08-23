import pytest
from app.clients.datasf import DataSFClient
from app.core.exceptions import UpstreamServiceException
from app.services.movie_service import MovieService


class FakeDataSFClient(DataSFClient):
    def __init__(self, records: list[dict] | None = None, raise_exc: Exception | None = None) -> None:
        super().__init__()
        self._records = records or []
        self._raise_exc = raise_exc

    async def get_film_locations(self, **kwargs) -> list[dict]:
        if self._raise_exc:
            raise self._raise_exc
        return self._records


@pytest.mark.asyncio
async def test_normalize_valid_record():
    raw_data = [
        {
            "title": "Vertigo",
            "release_year": "1958",
            "locations": "Fort Point",
            "director": "Alfred Hitchcock",
            "production_company": "Paramount Pictures",
            "distributor": "Paramount Pictures",
            "writer": "Alec Coppel",
            "actor_1": "James Stewart",
            "actor_2": "Kim Novak",
            "actor_3": "",
            "fun_facts": "Famous golden gate scene",
            "analysis_neighborhood": "Presidio",
            "latitude": "37.8102",
            "longitude": "-122.4770",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    item = result[0]
    assert item.title == "Vertigo"
    assert item.release_year == 1958
    assert item.location == "Fort Point"
    assert item.coordinates.latitude == 37.8102
    assert item.coordinates.longitude == -122.4770
    assert item.director == "Alfred Hitchcock"
    assert item.production_company == "Paramount Pictures"
    assert item.distributor == "Paramount Pictures"
    assert item.writer == "Alec Coppel"
    assert item.actors == ["James Stewart", "Kim Novak"]
    assert item.fun_facts == "Famous golden gate scene"
    assert item.neighborhood == "Presidio"


@pytest.mark.asyncio
async def test_missing_optional_fields():
    raw_data = [
        {
            "title": "Milk",
            "locations": "Castro Theatre",
            "latitude": "37.7620",
            "longitude": "-122.4350",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    item = result[0]
    assert item.title == "Milk"
    assert item.location == "Castro Theatre"
    assert item.release_year is None
    assert item.director is None
    assert item.actors == []


@pytest.mark.asyncio
async def test_missing_latitude():
    raw_data = [
        {
            "title": "Desperate Measures",
            "locations": "City Hall",
            "longitude": "-122.4194",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_missing_longitude():
    raw_data = [
        {
            "title": "Desperate Measures",
            "locations": "City Hall",
            "latitude": "37.7749",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_invalid_latitude():
    raw_data = [
        {
            "title": "Bad Record",
            "locations": "Market St",
            "latitude": "invalid_number",
            "longitude": "-122.4194",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_invalid_coordinate_range():
    raw_data = [
        {
            "title": "Out of Bounds",
            "locations": "Somewhere",
            "latitude": "150.0",
            "longitude": "-122.4194",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_missing_title():
    raw_data = [
        {
            "locations": "Lombard Street",
            "latitude": "37.8021",
            "longitude": "-122.4187",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_missing_location():
    raw_data = [
        {
            "title": "Untitled Filming",
            "latitude": "37.8021",
            "longitude": "-122.4187",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()
    assert result == []


@pytest.mark.asyncio
async def test_invalid_release_year():
    raw_data = [
        {
            "title": "The Rock",
            "release_year": "unknown_year",
            "locations": "Alcatraz Island",
            "latitude": "37.8267",
            "longitude": "-122.4230",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    assert result[0].title == "The Rock"
    assert result[0].release_year is None


@pytest.mark.asyncio
async def test_actor_cleanup_and_deduplication():
    raw_data = [
        {
            "title": "Zodiac",
            "locations": "SF Chronicle",
            "actor_1": " Jake Gyllenhaal ",
            "actor_2": "",
            "actor_3": "Jake Gyllenhaal",
            "latitude": "37.7812",
            "longitude": "-122.4061",
        }
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    assert result[0].actors == ["Jake Gyllenhaal"]


@pytest.mark.asyncio
async def test_upstream_exception_propagation():
    service = MovieService(
        datasf_client=FakeDataSFClient(
            raise_exc=UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message="DataSF is offline",
            )
        )
    )

    with pytest.raises(UpstreamServiceException) as exc_info:
        await service.get_movie_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"


@pytest.mark.asyncio
async def test_mixed_valid_and_invalid_rows():
    raw_data = [
        {"title": "Valid 1", "locations": "Loc 1", "latitude": "37.77", "longitude": "-122.41"},
        {"title": "Bad 1", "locations": "Loc 2"},
        {"title": "Valid 2", "locations": "Loc 3", "latitude": "37.78", "longitude": "-122.42"},
        {"locations": "Loc 4", "latitude": "37.79", "longitude": "-122.43"},
        {"title": "Valid 3", "locations": "Loc 5", "latitude": "37.80", "longitude": "-122.44"},
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 3
    titles = [item.title for item in result]
    assert titles == ["Valid 1", "Valid 2", "Valid 3"]


@pytest.mark.asyncio
async def test_exact_duplicate_deduplication():
    raw_data = [
        {"title": "Milk", "locations": "Castro", "latitude": "37.76", "longitude": "-122.43"},
        {"title": "Milk", "locations": "Castro", "latitude": "37.76", "longitude": "-122.43"},
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    assert result[0].title == "Milk"


def test_soql_where_construction():
    service = MovieService(datasf_client=FakeDataSFClient())


    assert service._build_soql_where() is None


    where_search = service._build_soql_where(search="vertigo")
    assert where_search == "(lower(title) like '%vertigo%' or lower(locations) like '%vertigo%')"


    where_year = service._build_soql_where(year=1958)
    assert where_year == "release_year = '1958'"


    where_combined = service._build_soql_where(search="vertigo", year=1958)
    assert (
        where_combined
        == "(lower(title) like '%vertigo%' or lower(locations) like '%vertigo%') and release_year = '1958'"
    )


    where_quote = service._build_soql_where(search="O'Brien")
    assert "o''brien" in where_quote


    where_title = service._build_soql_where(title="Vertigo")
    assert where_title == "lower(title) = 'vertigo'"


    where_location = service._build_soql_where(location="Golden Gate Bridge")
    assert where_location == "lower(locations) = 'golden gate bridge'"


@pytest.mark.asyncio
async def test_autocomplete_movie_title_match():
    raw_data = [{"title": "Vertigo", "locations": "Mission Dolores"}]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="vert")

    assert len(suggestions) == 1
    assert suggestions[0].value == "Vertigo"
    assert suggestions[0].type == "movie"


@pytest.mark.asyncio
async def test_autocomplete_location_match():
    raw_data = [{"title": "Movie A", "locations": "Golden Gate Bridge"}]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="gate")

    assert len(suggestions) == 1
    assert suggestions[0].value == "Golden Gate Bridge"
    assert suggestions[0].type == "location"


@pytest.mark.asyncio
async def test_autocomplete_duplicate_movie_titles():
    raw_data = [
        {"title": "Vertigo", "locations": "Mission Dolores"},
        {"title": "Vertigo", "locations": "Palace of Fine Arts"},
        {"title": "Vertigo", "locations": "Coit Tower"},
    ]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="vert")

    movie_suggestions = [s for s in suggestions if s.type == "movie"]
    assert len(movie_suggestions) == 1
    assert movie_suggestions[0].value == "Vertigo"


@pytest.mark.asyncio
async def test_autocomplete_duplicate_locations():
    raw_data = [
        {"title": "Movie A", "locations": "Golden Gate Bridge"},
        {"title": "Movie B", "locations": "Golden Gate Bridge"},
    ]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="gate")

    location_suggestions = [s for s in suggestions if s.type == "location"]
    assert len(location_suggestions) == 1
    assert location_suggestions[0].value == "Golden Gate Bridge"


@pytest.mark.asyncio
async def test_autocomplete_case_insensitive_duplicates():
    raw_data = [
        {"title": "Movie A", "locations": "Golden Gate Bridge"},
        {"title": "Movie B", "locations": "golden gate bridge"},
    ]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="gate")

    location_suggestions = [s for s in suggestions if s.type == "location"]
    assert len(location_suggestions) == 1
    assert location_suggestions[0].value == "Golden Gate Bridge"


@pytest.mark.asyncio
async def test_autocomplete_missing_location():
    raw_data = [{"title": "Vertigo", "locations": None}]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="vert")

    assert len(suggestions) == 1
    assert suggestions[0].value == "Vertigo"
    assert suggestions[0].type == "movie"


@pytest.mark.asyncio
async def test_autocomplete_missing_title():
    raw_data = [{"title": None, "locations": "Golden Gate Park"}]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="park")

    assert len(suggestions) == 1
    assert suggestions[0].value == "Golden Gate Park"
    assert suggestions[0].type == "location"


@pytest.mark.asyncio
async def test_autocomplete_empty_result():
    service = MovieService(datasf_client=FakeDataSFClient(records=[]))

    suggestions = await service.get_search_suggestions(query="nonexistent")

    assert suggestions == []


@pytest.mark.asyncio
async def test_autocomplete_ranking_prefix_over_contains():
    raw_data = [
        {"title": "The Making of Vertigo", "locations": "Studio"},
        {"title": "Vertigo", "locations": "Mission Dolores"},
    ]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="vert")

    movie_values = [s.value for s in suggestions if s.type == "movie"]
    assert movie_values == ["Vertigo", "The Making of Vertigo"]


@pytest.mark.asyncio
async def test_autocomplete_limit_enforcement():
    raw_data = [
        {"title": f"Movie {i}", "locations": f"Location {i}"}
        for i in range(20)
    ]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="movie", limit=5)

    assert len(suggestions) == 5


@pytest.mark.asyncio
async def test_autocomplete_upstream_exception():
    client = FakeDataSFClient(
        raise_exc=UpstreamServiceException(
            code="UPSTREAM_SERVICE_ERROR", message="DataSF connection failed"
        )
    )
    service = MovieService(datasf_client=client)

    with pytest.raises(UpstreamServiceException) as exc_info:
        await service.get_search_suggestions(query="vert")

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"


@pytest.mark.asyncio
async def test_autocomplete_special_character_query():
    raw_data = [{"title": "O'Brien's Tower", "locations": "O'Brien Place"}]
    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))

    suggestions = await service.get_search_suggestions(query="O'Brien")

    assert len(suggestions) >= 1
    assert any("O'Brien" in s.value for s in suggestions)


@pytest.mark.asyncio
async def test_coordinate_exact_boundary_values():
    raw_data = [
        {
            "title": "North Pole Movie",
            "locations": "Arctic Center",
            "latitude": "90.0",
            "longitude": "-180.0",
        },
        {
            "title": "South Pole Movie",
            "locations": "Antarctic Base",
            "latitude": "-90.0",
            "longitude": "180.0",
        },
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 2
    assert result[0].coordinates.latitude == 90.0
    assert result[0].coordinates.longitude == -180.0
    assert result[1].coordinates.latitude == -90.0
    assert result[1].coordinates.longitude == 180.0
