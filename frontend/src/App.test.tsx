import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { apiClient } from "./api/client";
import { getSearchSuggestions } from "./api/search";

vi.mock("./api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
}

function renderWithClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>{ui}</QueryClientProvider>
  );
}

describe("App & HomePage Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    vi.mocked(apiClient.get).mockImplementation(() => new Promise(() => {}));

    renderWithClient(<App />);

    expect(screen.getByText("SF Movies")).toBeInTheDocument();
    expect(screen.getByText("Loading movie locations...")).toBeInTheDocument();
  });

  it("renders fetched movie data preview on success", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [
          {
            title: "Vertigo",
            release_year: 1958,
            location: "Mission Dolores",
            coordinates: { latitude: 37.76, longitude: -122.42 },
            director: "Alfred Hitchcock",
            production_company: "Paramount",
            distributor: null,
            writer: null,
            actors: ["James Stewart"],
            fun_facts: null,
            neighborhood: "Mission",
          },
        ],
        meta: { count: 1, limit: 10, offset: 0 },
      },
    });

    renderWithClient(<App />);

    await waitFor(() => {
      expect(screen.getByText("Loaded 1 locations")).toBeInTheDocument();
      expect(screen.getByText(/Vertigo/)).toBeInTheDocument();
      expect(screen.getByText(/Mission Dolores/)).toBeInTheDocument();
    });
  });

  it("renders error state when API call fails", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Network Error"));

    renderWithClient(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("Unable to load movie locations.")
      ).toBeInTheDocument();
    });
  });

  it("getSearchSuggestions issues correct API GET request", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [{ value: "Vertigo", type: "movie" }],
      },
    });

    const res = await getSearchSuggestions("vert", 5);

    expect(apiClient.get).toHaveBeenCalledWith("/api/v1/search/suggestions", {
      params: { q: "vert", limit: 5 },
    });
    expect(res.data).toEqual([{ value: "Vertigo", type: "movie" }]);
  });
});
