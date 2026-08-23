export type SearchSuggestionType = "movie" | "location";

export type SearchSuggestion = {
  value: string;
  type: SearchSuggestionType;
};

export type SearchSuggestionsResponse = {
  data: SearchSuggestion[];
};

export type GetSearchSuggestionsParams = {
  q: string;
  limit?: number;
};
