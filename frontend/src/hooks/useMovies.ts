import { useQuery } from "@tanstack/react-query";
import { getMovies } from "../api/movies";
import type { GetMoviesParams } from "../types/movie";

/**
 * Custom TanStack Query hook for fetching paginated and filtered movie location records.
 *
 * @param params Optional search, year, limit, and offset query parameters.
 * @returns TanStack Query result object containing data, isLoading, isError, error, etc.
 */
export function useMovies(params: GetMoviesParams = {}) {
  return useQuery({
    queryKey: ["movies", params],
    queryFn: () => getMovies(params),
  });
}
