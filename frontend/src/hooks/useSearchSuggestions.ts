import { useQuery } from "@tanstack/react-query";
import { getSearchSuggestions } from "../api/search";

export function useSearchSuggestions(query: string, limit = 8) {
  const trimmedQuery = query.trim();

  return useQuery({
    queryKey: ["search-suggestions", trimmedQuery, limit],
    queryFn: () => getSearchSuggestions(trimmedQuery, limit),
    enabled: trimmedQuery.length >= 2,
  });
}
