import { apiClient } from "./client";
import type { GetMoviesParams, MovieListResponse } from "../types/movie";

/**
 * Fetches a list of normalized movie filming locations from the FastAPI backend.
 *
 * @param params Optional search, release year, limit, and offset query parameters.
 * @returns Promise resolving to MovieListResponse payload envelope.
 */
export async function getMovies(
  params?: GetMoviesParams
): Promise<MovieListResponse> {
  const response = await apiClient.get<MovieListResponse>("/api/v1/movies", {
    params,
  });
  return response.data;
}
