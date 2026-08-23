import { useState, useRef, useEffect, type KeyboardEvent } from "react";
import { Search, X, Clapperboard, MapPin, Loader2 } from "lucide-react";
import { useDebounce } from "../../hooks/useDebounce";
import { useSearchSuggestions } from "../../hooks/useSearchSuggestions";
import type { SearchSuggestion } from "../../types/search";

type SearchAutocompleteProps = {

  onSelect: (suggestion: SearchSuggestion) => void;

  onClear?: () => void;

  placeholder?: string;
};

export default function SearchAutocomplete({
  onSelect,
  onClear,
  placeholder = "Search movies or filming locations...",
}: SearchAutocompleteProps) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);

  const containerRef = useRef<HTMLDivElement>(null);
  const debouncedQuery = useDebounce(query, 300);

  const { data, isLoading, isError } = useSearchSuggestions(debouncedQuery);
  const suggestions = data?.data || [];

  const isMinLength = debouncedQuery.trim().length >= 2;
  const showDropdown = isOpen && isMinLength;

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  function handleSelect(suggestion: SearchSuggestion) {
    setQuery(suggestion.value);
    setIsOpen(false);
    setHighlightedIndex(-1);
    onSelect(suggestion);
  }

  function handleClear() {
    setQuery("");
    setIsOpen(false);
    setHighlightedIndex(-1);
    if (onClear) {
      onClear();
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (!showDropdown || suggestions.length === 0) {
      if (e.key === "Escape") {
        setIsOpen(false);
      }
      return;
    }

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case "Enter":
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < suggestions.length) {
          handleSelect(suggestions[highlightedIndex]);
        }
        break;
      case "Escape":
        e.preventDefault();
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-xl z-50">
      {}
      <div className="relative flex items-center">
        <Search className="absolute left-3.5 w-4 h-4 text-slate-400 pointer-events-none" />

        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
            setHighlightedIndex(-1);
          }}
          onFocus={() => {
            if (query.trim().length >= 2) {
              setIsOpen(true);
            }
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          role="combobox"
          aria-expanded={showDropdown}
          aria-autocomplete="list"
          aria-controls="search-suggestions-list"
          aria-label="Search movies and filming locations"
          aria-activedescendant={
            highlightedIndex >= 0 ? `suggestion-option-${highlightedIndex}` : undefined
          }
          className="w-full pl-10 pr-10 py-2.5 text-sm bg-slate-900/90 text-slate-100 placeholder-slate-400 rounded-xl border border-slate-700/80 focus:border-amber-400 focus:outline-none focus:ring-2 focus:ring-amber-400/20 transition-all shadow-lg"
        />

        {query && (
          <button
            type="button"
            onClick={handleClear}
            aria-label="Clear search"
            className="absolute right-3 p-1 rounded-full text-slate-400 hover:text-amber-400 hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {}
      {showDropdown && (
        <div
          id="search-suggestions-list"
          role="listbox"
          className="absolute left-0 right-0 top-full mt-2 bg-slate-900/95 backdrop-blur-md border border-slate-800 rounded-xl shadow-2xl overflow-hidden z-50 max-h-80 overflow-y-auto divide-y divide-slate-800/60"
        >
          {isLoading && (
            <div className="p-4 flex items-center justify-center gap-2 text-slate-400 text-xs">
              <Loader2 className="w-4 h-4 animate-spin text-amber-400" />
              <span>Searching...</span>
            </div>
          )}

          {isError && !isLoading && (
            <div className="p-4 text-center text-xs text-red-400">
              Unable to load suggestions.
            </div>
          )}

          {!isLoading && !isError && suggestions.length === 0 && (
            <div className="p-4 text-center text-xs text-slate-400">
              No matching movies or locations found.
            </div>
          )}

          {!isLoading &&
            !isError &&
            suggestions.length > 0 &&
            suggestions.map((suggestion, index) => {
              const isHighlighted = index === highlightedIndex;
              const isMovie = suggestion.type === "movie";

              return (
                <button
                  key={`${suggestion.type}-${suggestion.value}-${index}`}
                  id={`suggestion-option-${index}`}
                  type="button"
                  role="option"
                  aria-selected={isHighlighted}
                  onMouseDown={(e) => {

                    e.preventDefault();
                  }}
                  onClick={() => handleSelect(suggestion)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full text-left px-4 py-3 text-xs flex items-center justify-between transition-colors ${
                    isHighlighted
                      ? "bg-amber-400/10 text-amber-300 font-medium"
                      : "text-slate-200 hover:bg-slate-800/80"
                  }`}
                >
                  <div className="flex items-center gap-2.5 truncate pr-2">
                    {isMovie ? (
                      <Clapperboard className="w-4 h-4 text-amber-400 shrink-0" />
                    ) : (
                      <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
                    )}
                    <span className="truncate">{suggestion.value}</span>
                  </div>

                  <span
                    className={`text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded shrink-0 border ${
                      isMovie
                        ? "bg-amber-950/60 text-amber-400 border-amber-800/50"
                        : "bg-emerald-950/60 text-emerald-400 border-emerald-800/50"
                    }`}
                  >
                    {suggestion.type}
                  </span>
                </button>
              );
            })}
        </div>
      )}
    </div>
  );
}
