import { useQuery } from "@tanstack/react-query";
import { getMovies } from "../api/movies";
import type { GetMoviesParams } from "../types/movie";

export function useMovies(params: GetMoviesParams = {}) {
  return useQuery({
    queryKey: ["movies", params],
    queryFn: () => getMovies(params),
  });
}
