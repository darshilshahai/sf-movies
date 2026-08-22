import { render, screen, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App";
import { apiClient } from "./api/client";

// Mock MovieMap component to avoid Leaflet JSDOM container sizing issues in unit tests
vi.mock("./components/map/MovieMap", () => ({
  default: ({ movies }: { movies: Array<{ title: string; location: string }> }) => (
    <div data-testid="mock-movie-map">
      Mock Movie Map with {movies.length} markers
    </div>
  ),
}));

vi.mock("./api/client", () => ({
  apiClient: {
    get: vi.fn(),
  },
}));

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });
}

function renderWithClient(ui: React.ReactElement) {
  const testQueryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={testQueryClient}>{ui}</QueryClientProvider>
  );
}

describe("App & HomePage Leaflet Map Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders loading state initially", () => {
    vi.mocked(apiClient.get).mockImplementation(() => new Promise(() => {}));
    renderWithClient(<App />);
    expect(screen.getByText("SF Movies Explorer")).toBeInTheDocument();
    expect(
      screen.getByText("Loading San Francisco filming locations...")
    ).toBeInTheDocument();
  });

  it("renders location count and MovieMap on successful data fetch", async () => {
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
        meta: { count: 1, limit: 500, offset: 0 },
      },
    });

    renderWithClient(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("Showing 1 filming locations")
      ).toBeInTheDocument();
      expect(screen.getByTestId("mock-movie-map")).toBeInTheDocument();
      expect(
        screen.getByText("Mock Movie Map with 1 markers")
      ).toBeInTheDocument();
    });
  });

  it("renders error state when API fails", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Upstream Error"));

    renderWithClient(<App />);

    await waitFor(() => {
      expect(
        screen.getByText("Unable to load filming locations")
      ).toBeInTheDocument();
      expect(screen.getByText("Try Again")).toBeInTheDocument();
    });
  });

  it("renders empty state when location list is empty", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [],
        meta: { count: 0, limit: 500, offset: 0 },
      },
    });

    renderWithClient(<App />);

    await waitFor(() => {
      expect(screen.getByText("No filming locations found.")).toBeInTheDocument();
    });
  });
});
