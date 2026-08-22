import { useQuery } from "@tanstack/react-query";
import { getSearchSuggestions } from "../api/search";

/**
 * Custom TanStack Query hook for fetching autocomplete suggestions for movie titles and locations.
 * Automatically disables query execution when trimmed query string is less than 2 characters.
 *
 * @param query Search string input from user.
 * @param limit Maximum number of suggestions to retrieve (default: 8).
 * @returns TanStack Query result object containing suggestions data, status, etc.
 */
export function useSearchSuggestions(query: string, limit = 8) {
  const trimmedQuery = query.trim();

  return useQuery({
    queryKey: ["search-suggestions", trimmedQuery, limit],
    queryFn: () => getSearchSuggestions(trimmedQuery, limit),
    enabled: trimmedQuery.length >= 2,
  });
}
