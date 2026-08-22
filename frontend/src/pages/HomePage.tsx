import { useState } from "react";
import { useMovies } from "../hooks/useMovies";
import MovieMap from "../components/map/MovieMap";
import SearchAutocomplete from "../components/search/SearchAutocomplete";
import type { SearchSuggestion } from "../types/search";

/**
 * Main application page integrating movie data fetching, search autocomplete UI, and Leaflet map.
 */
export default function HomePage() {
  const { data, isLoading, isError, refetch } = useMovies({ limit: 500 });
  const [selectedSuggestion, setSelectedSuggestion] = useState<SearchSuggestion | null>(null);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
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

          {/* Search Autocomplete Bar */}
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

          {!isLoading && !isError && data && (
            <div className="flex items-center gap-2 self-start md:self-auto shrink-0">
              <span className="text-xs font-semibold px-3 py-1.5 rounded-full bg-slate-800 text-emerald-400 border border-slate-700 flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                Showing {data.meta.count} filming locations
              </span>
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6 flex flex-col space-y-4">
        {selectedSuggestion && (
          <div className="bg-slate-900/80 border border-amber-500/30 rounded-lg p-3 text-xs flex items-center justify-between">
            <span className="text-slate-300">
              Selected suggestion:{" "}
              <strong className="text-amber-400">{selectedSuggestion.value}</strong>{" "}
              <span className="text-slate-500">({selectedSuggestion.type})</span>
            </span>
            <button
              onClick={() => setSelectedSuggestion(null)}
              className="text-slate-400 hover:text-slate-200 text-xs underline"
            >
              Reset selection
            </button>
          </div>
        )}

        {isLoading && (
          <div className="flex-1 flex flex-col items-center justify-center py-24 space-y-4">
            <div className="h-10 w-10 border-4 border-amber-400/20 border-t-amber-400 rounded-full animate-spin" />
            <p className="text-slate-400 text-sm animate-pulse">
              Loading San Francisco filming locations...
            </p>
          </div>
        )}

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
              onClick={() => refetch()}
              className="px-4 py-2 text-xs font-semibold rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 transition-colors shadow-lg"
            >
              Try Again
            </button>
          </div>
        )}

        {!isLoading && !isError && data && (
          <>
            {data.data.length === 0 ? (
              <div className="flex-1 flex items-center justify-center py-24">
                <p className="text-slate-400 text-sm">
                  No filming locations found.
                </p>
              </div>
            ) : (
              <MovieMap movies={data.data} />
            )}
          </>
        )}
      </main>
    </div>
  );
}
