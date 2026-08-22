import { Sparkles, X } from "lucide-react";
import type { SearchSuggestion } from "../../types/search";

type ResultStatusProps = {
  /** Total number of locations currently displayed on the map. */
  count: number;
  /** Active search autocomplete suggestion filter, if any. */
  selectedSuggestion: SearchSuggestion | null;
  /** Callback fired to reset active search filter. */
  onClearFilter: () => void;
};

/**
 * Presentational component rendering location count badge, singular/plural grammar,
 * active filter callout tag, and accessible WAI-ARIA live updates.
 */
export default function ResultStatus({
  count,
  selectedSuggestion,
  onClearFilter,
}: ResultStatusProps) {
  const isFiltered = Boolean(selectedSuggestion);
  const locationText = count === 1 ? "filming location" : "filming locations";

  return (
    <div className="space-y-3" role="status" aria-live="polite">
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
            onClick={onClearFilter}
            className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 font-semibold underline underline-offset-2 ml-4 shrink-0 transition-colors"
            aria-label="Reset active search filter"
          >
            <span>Reset Filter</span>
            <X className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Location Count Pill */}
      <div className="flex items-center justify-between text-xs text-slate-400">
        <span className="font-medium text-slate-300">
          {isFiltered
            ? `${count} filtered ${locationText}`
            : `Showing ${count} ${locationText}`}
        </span>
      </div>
    </div>
  );
}
