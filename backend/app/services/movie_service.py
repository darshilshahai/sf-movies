import logging
from typing import Any, Literal

from app.clients.datasf import DataSFClient
from app.schemas.movie import Coordinates, MovieLocation
from app.schemas.search import SearchSuggestion

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

    def _build_soql_where(
        self,
        search: str | None = None,
        title: str | None = None,
        location: str | None = None,
        year: int | None = None,
    ) -> str | None:
        """
        Builds a safe SODA SoQL $where clause for search, title, location, and release_year filters.

        Sanitizes single quotes in text to prevent SoQL injection/syntax errors.
        """
        clauses: list[str] = []

        if title:
            escaped_title = title.strip().replace("'", "''").lower()
            if escaped_title:
                clauses.append(f"lower(title) = '{escaped_title}'")

        if location:
            escaped_location = location.strip().replace("'", "''").lower()
            if escaped_location:
                clauses.append(f"lower(locations) = '{escaped_location}'")

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
        title: str | None = None,
        location: str | None = None,
        year: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MovieLocation]:
        """
        Fetches raw records from DataSFClient using safe SoQL parameters, normalizing and deduplicating results.

        :param search: Optional title/location fuzzy search query string.
        :param title: Optional exact movie title query string.
        :param location: Optional exact filming location query string.
        :param year: Optional release year integer filter.
        :param limit: Maximum number of location records to return.
        :param offset: Pagination offset.
        :return: List of normalized MovieLocation domain objects.
        """
        soql_where = self._build_soql_where(
            search=search, title=title, location=location, year=year
        )

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

    async def get_search_suggestions(
        self,
        *,
        query: str,
        limit: int = 8,
    ) -> list[SearchSuggestion]:
        """
        Retrieves case-insensitive, deduplicated, and ranked autocomplete suggestions for titles and locations.

        :param query: Search query string (minimum 2 characters).
        :param limit: Maximum number of suggestions to return (default: 8).
        :return: List of SearchSuggestion domain objects.
        """
        trimmed_query = query.strip()
        if len(trimmed_query) < 2:
            return []

        soql_where = self._build_soql_where(search=trimmed_query)

        # Fetch up to 50 raw records from DataSF to ensure sufficient sample for deduplication
        raw_records = await self._datasf_client.get_film_locations(
            limit=50,
            offset=0,
            where=soql_where,
        )

        q_lower = trimmed_query.lower()
        candidates: list[tuple[int, str, Literal["movie", "location"]]] = []
        seen_keys: set[tuple[str, str]] = set()

        for raw in raw_records:
            title = self._normalize_string(raw.get("title"))
            location = self._normalize_string(raw.get("locations"))

            # Evaluate Title candidate
            if title and q_lower in title.lower():
                dedup_key = (title.lower(), "movie")
                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    # Rank 1: Movie Title prefix match; Rank 3: Movie Title contains match
                    rank = 1 if title.lower().startswith(q_lower) else 3
                    candidates.append((rank, title, "movie"))

            # Evaluate Location candidate
            if location and q_lower in location.lower():
                dedup_key = (location.lower(), "location")
                if dedup_key not in seen_keys:
                    seen_keys.add(dedup_key)
                    # Rank 2: Location prefix match; Rank 4: Location contains match
                    rank = 2 if location.lower().startswith(q_lower) else 4
                    candidates.append((rank, location, "location"))

        # Sort candidate suggestions by rank ascending, preserving discovery order for ties
        candidates.sort(key=lambda item: item[0])

        suggestions = [
            SearchSuggestion(value=value, type=stype)
            for _, value, stype in candidates[:limit]
        ]

        logger.info(
            f"search_suggestions_returned query='{trimmed_query}' "
            f"raw_records={len(raw_records)} suggestions_count={len(suggestions)}"
        )
        return suggestions

