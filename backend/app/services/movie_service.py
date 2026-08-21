import logging
from typing import Any

from app.clients.datasf import DataSFClient
from app.schemas.movie import Coordinates, MovieLocation

logger = logging.getLogger("sf_movies.movie_service")


class MovieService:
    """Service layer for fetching, normalizing, filtering, and searching DataSF film locations."""

    def __init__(self, datasf_client: DataSFClient) -> None:
        self._datasf_client = datasf_client

    def _normalize_string(self, value: Any) -> str | None:
        """Trims leading/trailing whitespace and converts empty strings or None to None."""
        if value is None:
            return None
        s_val = str(value).strip()
        return s_val if s_val else None

    def _parse_coordinates(self, record: dict[str, Any]) -> Coordinates | None:
        """Parses and validates geographic coordinates from raw record fields."""
        raw_lat = record.get("latitude")
        raw_lng = record.get("longitude")

        if raw_lat is None or raw_lng is None:
            return None

        try:
            lat = float(raw_lat)
            lng = float(raw_lng)
        except (ValueError, TypeError):
            return None

        if not (-90.0 <= lat <= 90.0) or not (-180.0 <= lng <= 180.0):
            return None

        return Coordinates(latitude=lat, longitude=lng)

    def _parse_release_year(self, record: dict[str, Any]) -> int | None:
        """Parses release year string to integer safely."""
        raw_year = record.get("release_year")
        if not raw_year:
            return None
        try:
            return int(str(raw_year).strip())
        except (ValueError, TypeError):
            return None

    def _parse_actors(self, record: dict[str, Any]) -> list[str]:
        """Extracts, cleans, and deduplicates actor fields into a list."""
        actors: list[str] = []
        for key in ("actor_1", "actor_2", "actor_3"):
            normalized = self._normalize_string(record.get(key))
            if normalized and normalized not in actors:
                actors.append(normalized)
        return actors

    def _build_soql_where(self, search: str | None = None, year: int | None = None) -> str | None:
        """
        Builds a safe SODA SoQL $where clause for search and release_year filters.

        Sanitizes single quotes in search text to prevent SoQL injection/syntax errors.
        """
        clauses: list[str] = []

        if search:
            escaped_search = search.strip().replace("'", "''").lower()
            if escaped_search:
                clauses.append(
                    f"(lower(title) like '%{escaped_search}%' or lower(locations) like '%{escaped_search}%')"
                )

        if year is not None:
            clauses.append(f"release_year = '{year}'")

        if not clauses:
            return None

        return " and ".join(clauses)

    def normalize_record(self, record: dict[str, Any]) -> MovieLocation | None:
        """Normalizes a single raw DataSF record into a MovieLocation model, returning None if unusable."""
        title = self._normalize_string(record.get("title"))
        if not title:
            logger.warning("movie_record_skipped reason=missing_title")
            return None

        location = self._normalize_string(record.get("locations"))
        if not location:
            logger.warning(f"movie_record_skipped reason=missing_location title='{title}'")
            return None

        coords = self._parse_coordinates(record)
        if not coords:
            logger.warning(
                f"movie_record_skipped reason=invalid_coordinates title='{title}' location='{location}'"
            )
            return None

        return MovieLocation(
            title=title,
            release_year=self._parse_release_year(record),
            location=location,
            coordinates=coords,
            director=self._normalize_string(record.get("director")),
            production_company=self._normalize_string(record.get("production_company")),
            distributor=self._normalize_string(record.get("distributor")),
            writer=self._normalize_string(record.get("writer")),
            actors=self._parse_actors(record),
            fun_facts=self._normalize_string(record.get("fun_facts")),
            neighborhood=self._normalize_string(record.get("analysis_neighborhood")),
        )

    async def get_movie_locations(
        self,
        *,
        search: str | None = None,
        year: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MovieLocation]:
        """
        Fetches raw records from DataSFClient using safe SoQL parameters, normalizing and deduplicating results.

        :param search: Optional title/location search query string.
        :param year: Optional release year integer filter.
        :param limit: Maximum number of location records to return.
        :param offset: Pagination offset.
        :return: List of normalized MovieLocation domain objects.
        """
        soql_where = self._build_soql_where(search=search, year=year)

        raw_records = await self._datasf_client.get_film_locations(
            limit=limit,
            offset=offset,
            where=soql_where,
        )

        normalized_locations: list[MovieLocation] = []
        seen_keys: set[tuple[str, str, float, float]] = set()

        for raw in raw_records:
            item = self.normalize_record(raw)
            if item is None:
                continue

            dedup_key = (
                item.title.lower(),
                item.location.lower(),
                item.coordinates.latitude,
                item.coordinates.longitude,
            )
            if dedup_key in seen_keys:
                logger.debug(f"movie_record_skipped reason=duplicate_record key={dedup_key}")
                continue

            seen_keys.add(dedup_key)
            normalized_locations.append(item)

        logger.info(
            f"movie_transformation_completed input_raw={len(raw_records)} "
            f"output_normalized={len(normalized_locations)} search='{search}' year={year}"
        )
        return normalized_locations
