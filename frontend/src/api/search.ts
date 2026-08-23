import { apiClient } from "./client";
import type { SearchSuggestionsResponse } from "../types/search";

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
