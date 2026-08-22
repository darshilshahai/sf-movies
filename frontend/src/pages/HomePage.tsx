import { useState, useMemo } from "react";
import { Sparkles, Loader2 } from "lucide-react";
import { useMovies } from "../hooks/useMovies";
import MovieMap from "../components/map/MovieMap";
import SearchAutocomplete from "../components/search/SearchAutocomplete";
import type { SearchSuggestion } from "../types/search";
import type { GetMoviesParams } from "../types/movie";

/**
 * Main application page integrating movie data fetching, search autocomplete UI,
 * active filter management, and responsive Leaflet map viewport adjustment.
 */
export default function HomePage() {
  const [selectedSuggestion, setSelectedSuggestion] =
    useState<SearchSuggestion | null>(null);

  // Derive movie query parameters based on current search filter selection
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
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header & Sticky Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur sticky top-0 z-40 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-amber-400">
              SF Movies Explorer
            </h1>
            <p className="text-xs text-slate-400">
              Discover where movies were filmed across San Francisco
            </p>
          </div>

          {/* Autocomplete Search Input Bar */}
          <div className="flex-1 max-w-xl md:mx-4">
            <SearchAutocomplete
              onSelect={(suggestion) => {
                setSelectedSuggestion(suggestion);
              }}
              onClear={() => {
                setSelectedSuggestion(null);
              }}
            />
          </div>

          {/* Location Count Badge */}
          {!isLoading && !isError && data && (
            <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-800 text-emerald-400 border border-slate-700 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                {isFiltered
                  ? `${data.data.length} filtered location${data.data.length === 1 ? "" : "s"}`
                  : `Showing ${data.meta.count} filming locations`}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Main Content Body */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col space-y-4">
        {/* Active Filter Callout Badge */}
        {selectedSuggestion && (
          <div className="flex items-center justify-between bg-amber-950/40 border border-amber-800/60 px-4 py-2.5 rounded-xl text-xs text-amber-200 shadow-md">
            <div className="flex items-center gap-2 truncate pr-2">
              <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
              <span className="truncate">
                Filtering by {selectedSuggestion.type}:{" "}
                <strong className="text-amber-300 font-bold">
                  "{selectedSuggestion.value}"
                </strong>
              </span>
            </div>
            <button
              type="button"
              onClick={() => setSelectedSuggestion(null)}
              className="text-xs text-amber-400 hover:text-amber-300 font-semibold underline underline-offset-2 ml-4 shrink-0"
            >
              Reset Filter
            </button>
          </div>
        )}

        {/* Initial Loading Spinner */}
        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-4">
            <div className="h-10 w-10 border-4 border-amber-400/20 border-t-amber-400 rounded-full animate-spin" />
            <p className="text-slate-400 text-sm animate-pulse">
              Loading San Francisco filming locations...
            </p>
          </div>
        )}

        {/* Error Feedback Box */}
        {isError && (
          <div className="flex-1 flex flex-col items-center justify-center py-24 max-w-md mx-auto text-center space-y-4">
            <div className="p-4 rounded-xl bg-red-950/40 border border-red-800/80 text-red-300 text-sm space-y-2">
              <p className="font-semibold text-base text-red-200">
                Unable to load filming locations
              </p>
              <p className="text-xs text-red-300/80">
                We couldn't retrieve movie data from the backend server.
              </p>
            </div>
            <button
              type="button"
              onClick={() => refetch()}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors shadow-lg"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Main Leaflet Map & Refetch Status */}
        {!isLoading && !isError && data && (
          <div className="relative">
            {/* Background Refetch Status Indicator */}
            {isFetching && (
              <div className="absolute top-3 right-3 z-10 bg-slate-900/90 text-amber-400 text-xs px-3 py-1.5 rounded-full border border-amber-500/40 flex items-center gap-2 shadow-lg backdrop-blur">
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Updating map...</span>
              </div>
            )}

            {data.data.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-3 bg-slate-900/40 rounded-xl border border-slate-800">
                <p className="text-slate-300 text-sm font-medium">
                  {selectedSuggestion
                    ? `No filming locations found for "${selectedSuggestion.value}".`
                    : "No filming locations found."}
                </p>
                {selectedSuggestion && (
                  <button
                    type="button"
                    onClick={() => setSelectedSuggestion(null)}
                    className="px-3 py-1.5 text-xs font-semibold rounded-lg bg-amber-500 text-slate-950 hover:bg-amber-400 transition-colors"
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
