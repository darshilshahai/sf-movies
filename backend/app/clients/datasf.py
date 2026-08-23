import logging
import time
from typing import Any

import httpx
from app.core.config import get_settings
from app.core.exceptions import UpstreamServiceException, UpstreamTimeoutException

logger = logging.getLogger("sf_movies.datasf_client")


class DataSFClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        settings = get_settings()
        self.base_url = settings.datasf_base_url
        self.app_token = settings.datasf_app_token
        self.timeout_seconds = settings.datasf_timeout_seconds
        self._client = client

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is not None:
            return self._client
        return httpx.AsyncClient(timeout=httpx.Timeout(self.timeout_seconds))

    async def get_film_locations(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        where: str | None = None,
        order: str | None = None,
        q: str | None = None,
    ) -> list[dict[str, Any]]:


        params: dict[str, Any] = {
            "$limit": limit,
            "$offset": offset,
        }
        if where:
            params["$where"] = where
        if order:
            params["$order"] = order
        if q:
            params["$q"] = q

        headers: dict[str, str] = {
            "User-Agent": "SF-Movies-Backend/1.0",
            "Accept": "application/json",
        }
        if self.app_token:
            headers["X-App-Token"] = self.app_token

        logger.info(
            f"datasf_request_started base_url={self.base_url} limit={limit} offset={offset}"
        )

        client_is_managed = self._client is None
        client = await self._get_client()

        start_time = time.perf_counter()
        try:
            response = await client.get(self.base_url, params=params, headers=headers)
            duration_ms = (time.perf_counter() - start_time) * 1000
        except httpx.TimeoutException as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"datasf_request_timeout base_url={self.base_url} duration_ms={duration_ms:.2f} error={exc}"
            )
            raise UpstreamTimeoutException(
                code="UPSTREAM_SERVICE_TIMEOUT",
                message="DataSF API request timed out.",
            ) from exc
        except httpx.RequestError as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                f"datasf_request_failed base_url={self.base_url} duration_ms={duration_ms:.2f} error={exc}"
            )
            raise UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message="Failed to connect to DataSF API.",
            ) from exc
        finally:
            if client_is_managed:
                await client.aclose()

        if response.is_error:
            logger.error(
                f"datasf_request_error status={response.status_code} "
                f"duration_ms={duration_ms:.2f} body='{response.text[:200]}'"
            )
            raise UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message=f"DataSF API responded with error status {response.status_code}.",
            )

        try:
            data = response.json()
        except ValueError as exc:
            logger.error(
                f"datasf_invalid_json error={exc} body='{response.text[:200]}'"
            )
            raise UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message="DataSF API returned invalid JSON response.",
            ) from exc

        if not isinstance(data, list):
            logger.error(f"datasf_invalid_shape type={type(data).__name__}")
            raise UpstreamServiceException(
                code="UPSTREAM_SERVICE_ERROR",
                message="DataSF API returned unexpected response shape (expected list).",
            )

        logger.info(
            f"datasf_request_completed status={response.status_code} "
            f"duration_ms={duration_ms:.2f} result_count={len(data)}"
        )
        return data
