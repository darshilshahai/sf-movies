import pytest
from app.clients.datasf import DataSFClient
from app.core.exceptions import UpstreamServiceException
from app.services.movie_service import MovieService


class FakeDataSFClient(DataSFClient):
    """Fake DataSF client for isolated unit testing."""

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
    """Test 1: Full valid raw DataSF record is transformed into a clean MovieLocation model."""
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
    """Test 2: Record with only required map attributes normalizes optional fields to None."""
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
    """Test 3: Record missing latitude is skipped."""
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
    """Test 4: Record missing longitude is skipped."""
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
    """Test 5: Record with non-numeric latitude string is skipped."""
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
    """Test 6: Coordinates out of valid WGS84 range (-90 to 90 lat, -180 to 180 lng) are rejected."""
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
    """Test 7: Record with missing title is skipped."""
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
    """Test 8: Record with missing location description is skipped."""
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
    """Test 9: Invalid release year is converted to None without rejecting the record."""
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
    """Test 10: Actor names are trimmed, empty values ignored, and duplicates removed."""
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
    """Test 11: Upstream errors from DataSFClient propagate without being swallowed as []."""
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
    """Test 12: Mixed list with 3 valid and 2 malformed records returns 3 valid records."""
    raw_data = [
        {"title": "Valid 1", "locations": "Loc 1", "latitude": "37.77", "longitude": "-122.41"},
        {"title": "Bad 1", "locations": "Loc 2"},  # missing coords
        {"title": "Valid 2", "locations": "Loc 3", "latitude": "37.78", "longitude": "-122.42"},
        {"locations": "Loc 4", "latitude": "37.79", "longitude": "-122.43"},  # missing title
        {"title": "Valid 3", "locations": "Loc 5", "latitude": "37.80", "longitude": "-122.44"},
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 3
    titles = [item.title for item in result]
    assert titles == ["Valid 1", "Valid 2", "Valid 3"]


@pytest.mark.asyncio
async def test_exact_duplicate_deduplication():
    """Test 13: Identical movie location records are deduplicated."""
    raw_data = [
        {"title": "Milk", "locations": "Castro", "latitude": "37.76", "longitude": "-122.43"},
        {"title": "Milk", "locations": "Castro", "latitude": "37.76", "longitude": "-122.43"},
    ]

    service = MovieService(datasf_client=FakeDataSFClient(records=raw_data))
    result = await service.get_movie_locations()

    assert len(result) == 1
    assert result[0].title == "Milk"


def test_soql_where_construction():
    """Test 14: Verifies SoQL $where clause construction, parameter combination, and quote escaping."""
    service = MovieService(datasf_client=FakeDataSFClient())

    # Case A: No filters
    assert service._build_soql_where() is None

    # Case B: Search only
    where_search = service._build_soql_where(search="vertigo")
    assert where_search == "(lower(title) like '%vertigo%' or lower(locations) like '%vertigo%')"

    # Case C: Year only
    where_year = service._build_soql_where(year=1958)
    assert where_year == "release_year = '1958'"

    # Case D: Search + Year combined
    where_combined = service._build_soql_where(search="vertigo", year=1958)
    assert (
        where_combined
        == "(lower(title) like '%vertigo%' or lower(locations) like '%vertigo%') and release_year = '1958'"
    )

    # Case E: Quote escaping (e.g. O'Brien -> o''brien)
    where_quote = service._build_soql_where(search="O'Brien")
    assert "o''brien" in where_quote
