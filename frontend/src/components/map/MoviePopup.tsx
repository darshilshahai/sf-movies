import type { MovieLocation } from "../../types/movie";
import {
  MapPin,
  Calendar,
  Clapperboard,
  Users,
  Building2,
  Sparkles,
  Navigation,
} from "lucide-react";

type MoviePopupProps = {
  movie: MovieLocation;
};

export default function MoviePopup({ movie }: MoviePopupProps) {
  const hasActors = Boolean(movie.actors && movie.actors.length > 0);

  return (
    <div className="w-64 max-w-[280px] p-3 text-slate-100 space-y-3 font-sans text-xs">
      {}
      <header className="border-b border-slate-800/90 pb-2 space-y-1">
        <div className="flex items-start justify-between gap-2">
          <h3 className="font-bold text-sm text-amber-400 leading-snug tracking-tight">
            {movie.title}
          </h3>
          {movie.release_year && (
            <span className="flex items-center gap-1 text-[11px] font-semibold text-slate-300 shrink-0 bg-slate-800/90 px-2 py-0.5 rounded-full border border-slate-700">
              <Calendar className="w-3 h-3 text-amber-400" />
              {movie.release_year}
            </span>
          )}
        </div>
      </header>

      {}
      <div className="space-y-1.5">
        <div className="flex items-start gap-1.5 text-slate-100">
          <MapPin className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
          <span className="font-medium leading-relaxed text-slate-200">
            {movie.location}
          </span>
        </div>

        {movie.neighborhood && (
          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 pl-5">
            <Navigation className="w-3 h-3 text-slate-500 shrink-0" />
            <span>{movie.neighborhood}</span>
          </div>
        )}
      </div>

      {}
      {(movie.director || hasActors || movie.production_company || movie.fun_facts) && (
        <div className="space-y-2 border-t border-slate-800/90 pt-2 text-[11px]">
          {}
          {movie.director && (
            <div className="flex items-start gap-1.5">
              <Clapperboard className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-slate-500 uppercase tracking-wider text-[10px] font-semibold block">
                  Director
                </span>
                <span className="text-slate-200 font-medium">
                  {movie.director}
                </span>
              </div>
            </div>
          )}

          {}
          {hasActors && (
            <div className="flex items-start gap-1.5">
              <Users className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-slate-500 uppercase tracking-wider text-[10px] font-semibold block">
                  Cast
                </span>
                <span className="text-slate-200 font-medium leading-normal">
                  {movie.actors.join(" • ")}
                </span>
              </div>
            </div>
          )}

          {}
          {movie.production_company && (
            <div className="flex items-start gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
              <div>
                <span className="text-slate-500 uppercase tracking-wider text-[10px] font-semibold block">
                  Studio
                </span>
                <span className="text-slate-300">
                  {movie.production_company}
                </span>
              </div>
            </div>
          )}

          {}
          {movie.fun_facts && (
            <div className="flex items-start gap-1.5 bg-amber-950/30 border border-amber-800/40 p-2 rounded-lg mt-2 text-amber-200/90">
              <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
              <div className="space-y-0.5">
                <span className="text-amber-400 uppercase tracking-wider text-[10px] font-bold block">
                  Fun Fact
                </span>
                <p className="text-[11px] leading-relaxed text-amber-100/90 max-h-24 overflow-y-auto whitespace-pre-line">
                  {movie.fun_facts}
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
