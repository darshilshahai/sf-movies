from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    latitude: float = Field(..., description="Geographic latitude coordinate (-90.0 to 90.0)")
    longitude: float = Field(..., description="Geographic longitude coordinate (-180.0 to 180.0)")


class MovieLocation(BaseModel):
    title: str = Field(..., description="Movie title")
    release_year: int | None = Field(default=None, description="Film release year")
    location: str = Field(..., description="Filming location description or landmark name")
    coordinates: Coordinates = Field(..., description="Geographic coordinates for map pin placement")
    director: str | None = Field(default=None, description="Director name")
    production_company: str | None = Field(default=None, description="Production studio name")
    distributor: str | None = Field(default=None, description="Film distributor name")
    writer: str | None = Field(default=None, description="Screenwriter name")
    actors: list[str] = Field(default_factory=list, description="Aggregated list of cast members")
    fun_facts: str | None = Field(default=None, description="Location trivia or narrative note")
    neighborhood: str | None = Field(default=None, description="San Francisco municipal neighborhood")


class PaginationMeta(BaseModel):
    count: int = Field(..., description="Number of items returned in the current response page")
    limit: int = Field(..., description="Maximum number of items requested")
    offset: int = Field(..., description="Pagination offset applied")


class MovieListResponse(BaseModel):
    data: list[MovieLocation] = Field(..., description="List of normalized film locations")
    meta: PaginationMeta = Field(..., description="Response pagination metadata")
