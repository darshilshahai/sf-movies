import httpx
import pytest
from app.clients.datasf import DataSFClient
from app.core.exceptions import UpstreamServiceException, UpstreamTimeoutException


@pytest.mark.asyncio
async def test_get_film_locations_success():
    """Test 1: Successful request returns list of raw record dictionaries."""
    mock_payload = [
        {
            "title": "Vertigo",
            "release_year": "1958",
            "locations": "Fort Point",
            "latitude": "37.8102",
            "longitude": "-122.4770",
        }
    ]

    def transport_handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        return httpx.Response(200, json=mock_payload)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    result = await datasf_client.get_film_locations(limit=1)
    assert result == mock_payload
    assert len(result) == 1
    assert result[0]["title"] == "Vertigo"


@pytest.mark.asyncio
async def test_get_film_locations_empty():
    """Test 2: Empty result list is returned successfully without raising error."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    result = await datasf_client.get_film_locations()
    assert result == []


@pytest.mark.asyncio
async def test_get_film_locations_upstream_500():
    """Test 3: Upstream 500 server error raises UpstreamServiceException."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error")

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    with pytest.raises(UpstreamServiceException) as exc_info:
        await datasf_client.get_film_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_film_locations_timeout():
    """Test 4: Timeout raises UpstreamTimeoutException."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Request timed out", request=request)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    with pytest.raises(UpstreamTimeoutException) as exc_info:
        await datasf_client.get_film_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_TIMEOUT"
    assert exc_info.value.status_code == 504


@pytest.mark.asyncio
async def test_get_film_locations_network_failure():
    """Test 5: Network connection failure raises UpstreamServiceException."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused", request=request)

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    with pytest.raises(UpstreamServiceException) as exc_info:
        await datasf_client.get_film_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_film_locations_invalid_json():
    """Test 6: Invalid JSON response raises UpstreamServiceException."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="<html>502 Bad Gateway</html>")

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    with pytest.raises(UpstreamServiceException) as exc_info:
        await datasf_client.get_film_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_film_locations_invalid_shape():
    """Test 7: Unexpected response shape (JSON object instead of list) raises UpstreamServiceException."""

    def transport_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"error": "Invalid query"})

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    with pytest.raises(UpstreamServiceException) as exc_info:
        await datasf_client.get_film_locations()

    assert exc_info.value.code == "UPSTREAM_SERVICE_ERROR"
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_get_film_locations_query_params():
    """Test 8: Query parameters ($limit, $offset, $where, $order, $q) are passed correctly."""
    recorded_url = None

    def transport_handler(request: httpx.Request) -> httpx.Response:
        nonlocal recorded_url
        recorded_url = request.url
        return httpx.Response(200, json=[])

    mock_client = httpx.AsyncClient(transport=httpx.MockTransport(transport_handler))
    datasf_client = DataSFClient(client=mock_client)

    await datasf_client.get_film_locations(
        limit=25,
        offset=50,
        where="release_year > 2000",
        order="release_year DESC",
        q="vertigo",
    )

    assert recorded_url is not None
    assert recorded_url.params["$limit"] == "25"
    assert recorded_url.params["$offset"] == "50"
    assert recorded_url.params["$where"] == "release_year > 2000"
    assert recorded_url.params["$order"] == "release_year DESC"
    assert recorded_url.params["$q"] == "vertigo"
