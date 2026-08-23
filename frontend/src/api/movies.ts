import { apiClient } from "./client";
import type { GetMoviesParams, MovieListResponse } from "../types/movie";

export async function getMovies(
  params?: GetMoviesParams
): Promise<MovieListResponse> {
  const response = await apiClient.get<MovieListResponse>("/api/v1/movies", {
    params,
  });
  return response.data;
}
