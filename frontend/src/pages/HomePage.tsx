import { useMovies } from "../hooks/useMovies";

export default function HomePage() {
  const { data, isLoading, isError } = useMovies({ limit: 10 });

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
      <div className="max-w-md w-full space-y-6 bg-slate-900/80 p-6 rounded-xl border border-slate-800 shadow-xl">
        <header className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-amber-400">
            SF Movies
          </h1>
          <p className="text-slate-300 text-sm">
            Discover where movies were filmed in San Francisco
          </p>
        </header>

        {isLoading && (
          <p className="text-slate-400 text-sm animate-pulse">
            Loading movie locations...
          </p>
        )}

        {isError && (
          <div className="p-4 rounded-lg bg-red-950/50 border border-red-800 text-red-300 text-sm">
            Unable to load movie locations.
          </div>
        )}

        {!isLoading && !isError && data && (
          <div className="space-y-4 text-left">
            <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800 pb-2">
              <span className="text-emerald-400 font-medium flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-ping" />
                Backend Connected
              </span>
              <span>Loaded {data.meta.count} locations</span>
            </div>

            {data.data.length === 0 ? (
              <p className="text-slate-400 text-sm text-center py-4">
                No movie locations found.
              </p>
            ) : (
              <div className="space-y-2">
                <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Sample Data Preview
                </h2>
                <ul className="space-y-2 text-sm">
                  {data.data.slice(0, 5).map((movie, idx) => (
                    <li
                      key={`${movie.title}-${movie.location}-${idx}`}
                      className="p-2.5 rounded bg-slate-800/60 border border-slate-700/50 flex flex-col"
                    >
                      <span className="font-semibold text-amber-300">
                        {movie.title}{" "}
                        {movie.release_year && (
                          <span className="text-xs font-normal text-slate-400">
                            ({movie.release_year})
                          </span>
                        )}
                      </span>
                      <span className="text-xs text-slate-300 truncate">
                        📍 {movie.location}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
