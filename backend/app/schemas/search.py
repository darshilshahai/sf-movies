from typing import Literal
from pydantic import BaseModel, Field


class SearchSuggestion(BaseModel):
    """Schema for an individual autocomplete search suggestion."""

    value: str = Field(..., description="Matched movie title or filming location name")
    type: Literal["movie", "location"] = Field(
        ..., description="Type of suggestion ('movie' or 'location')"
    )


class SearchSuggestionsResponse(BaseModel):
    """Envelope model for autocomplete suggestions response."""

    data: list[SearchSuggestion] = Field(
        ..., description="List of deduplicated search suggestions"
    )
