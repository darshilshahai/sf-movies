import { useState, useMemo } from "react";
import { Loader2 } from "lucide-react";
import { useMovies } from "../hooks/useMovies";
import MovieMap from "../components/map/MovieMap";
import SearchAutocomplete from "../components/search/SearchAutocomplete";
import ResultStatus from "../components/common/ResultStatus";
import ErrorState from "../components/common/ErrorState";
import type { SearchSuggestion } from "../types/search";
import type { GetMoviesParams } from "../types/movie";

export default function HomePage() {
  const [selectedSuggestion, setSelectedSuggestion] =
    useState<SearchSuggestion | null>(null);

  const movieParams = useMemo<GetMoviesParams>(() => {
    if (!selectedSuggestion) {
      return { limit: 500 };
    }
    if (selectedSuggestion.type === "movie") {
      return { title: selectedSuggestion.value, limit: 500 };
    }
    return { location: selectedSuggestion.value, limit: 500 };
  }, [selectedSuggestion]);

  const { data, isLoading, isFetching, isError, refetch } = useMovies(movieParams);
  const isFiltered = Boolean(selectedSuggestion);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {}
      <header className="border-b border-slate-800/80 bg-slate-900/80 backdrop-blur sticky top-0 z-40 px-4 sm:px-6 lg:px-8 py-3.5 sm:py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-3 sm:gap-4">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-amber-400">
              SF Movies Explorer
            </h1>
            <p className="text-[11px] sm:text-xs text-slate-400">
              Explore filming locations from movies shot across San Francisco
            </p>
          </div>

          {}
          <div className="flex-1 max-w-xl w-full md:mx-4">
            <SearchAutocomplete
              onSelect={(suggestion) => {
                setSelectedSuggestion(suggestion);
              }}
              onClear={() => {
                setSelectedSuggestion(null);
              }}
            />
          </div>
        </div>
      </header>

      {}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col space-y-4">
        {}
        {!isLoading && !isError && data && (
          <ResultStatus
            count={data.data.length}
            selectedSuggestion={selectedSuggestion}
            onClearFilter={() => setSelectedSuggestion(null)}
          />
        )}

        {}
        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-4">
            <div className="h-10 w-10 border-4 border-amber-400/20 border-t-amber-400 rounded-full animate-spin" />
            <p className="text-slate-400 text-sm animate-pulse font-medium">
              Loading San Francisco filming locations...
            </p>
          </div>
        )}

        {}
        {isError && (
          <ErrorState
            onRetry={() => refetch()}
            isRetrying={isFetching}
          />
        )}

        {}
        {!isLoading && !isError && data && (
          <div className="relative flex-1">
            {}
            {isFetching && (
              <div className="absolute top-3 right-3 z-10 bg-slate-900/90 text-amber-400 text-xs px-3 py-1.5 rounded-full border border-amber-500/40 flex items-center gap-2 shadow-lg backdrop-blur">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Updating map...</span>
              </div>
            )}

            {data.data.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-3 bg-slate-900/40 rounded-xl border border-slate-800 text-center px-4">
                <p className="text-slate-300 text-sm font-medium">
                  {selectedSuggestion
                    ? `No filming locations found for "${selectedSuggestion.value}".`
                    : "No filming locations found."}
                </p>
                {selectedSuggestion && (
                  <button
                    type="button"
                    onClick={() => setSelectedSuggestion(null)}
                    className="px-3.5 py-1.5 text-xs font-semibold rounded-xl bg-amber-500 text-slate-950 hover:bg-amber-400 transition-colors shadow"
                  >
                    Clear Search Filter
                  </button>
                )}
              </div>
            ) : (
              <MovieMap movies={data.data} isFiltered={isFiltered} />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
