import { apiClient } from "./client";
import type { SearchSuggestionsResponse } from "../types/search";

/**
 * Fetches autocomplete search suggestions for movie titles and filming locations.
 *
 * @param query Search query string (minimum 2 characters).
 * @param limit Maximum number of suggestions to return (default: 8).
 * @returns Promise resolving to SearchSuggestionsResponse payload envelope.
 */
export async function getSearchSuggestions(
  query: string,
  limit = 8
): Promise<SearchSuggestionsResponse> {
  const response = await apiClient.get<SearchSuggestionsResponse>(
    "/api/v1/search/suggestions",
    {
      params: {
        q: query,
        limit,
      },
    }
  );
  return response.data;
}
