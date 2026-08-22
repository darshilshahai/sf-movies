export type Coordinates = {
  latitude: number;
  longitude: number;
};

export type MovieLocation = {
  title: string;
  release_year: number | null;
  location: string;
  coordinates: Coordinates;
  director: string | null;
  production_company: string | null;
  distributor: string | null;
  writer: string | null;
  actors: string[];
  fun_facts: string | null;
  neighborhood: string | null;
};

export type MovieListMeta = {
  count: number;
  limit: number;
  offset: number;
};

export type MovieListResponse = {
  data: MovieLocation[];
  meta: MovieListMeta;
};

export type GetMoviesParams = {
  search?: string;
  year?: number;
  limit?: number;
  offset?: number;
};
