import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import SearchAutocomplete from "./SearchAutocomplete";
import { apiClient } from "../../api/client";

vi.mock("../../api/client", () => ({
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

describe("SearchAutocomplete Component", () => {
  const mockOnSelect = vi.fn();
  const mockOnClear = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders search input with default placeholder", () => {
    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox", {
      name: /Search movies and filming locations/i,
    });
    expect(input).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Search movies or filming locations...")
    ).toBeInTheDocument();
  });

  it("does not trigger search when query length is less than 2 characters", () => {
    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "a" } });

    expect(apiClient.get).not.toHaveBeenCalled();
    expect(
      screen.queryByRole("listbox")
    ).not.toBeInTheDocument();
  });

  it("fetches and renders movie and location suggestions when query >= 2 chars", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [
          { value: "Vertigo", type: "movie" },
          { value: "Golden Gate Bridge", type: "location" },
        ],
      },
    });

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "vert" } });

    await waitFor(() => {
      expect(screen.getByRole("listbox")).toBeInTheDocument();
      expect(screen.getByText("Vertigo")).toBeInTheDocument();
      expect(screen.getByText("Golden Gate Bridge")).toBeInTheDocument();
      expect(screen.getByText("movie")).toBeInTheDocument();
      expect(screen.getByText("location")).toBeInTheDocument();
    });
  });

  it("selects suggestion on mouse click and fires onSelect callback", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [{ value: "Vertigo", type: "movie" }],
      },
    });

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "vert" } });

    await waitFor(() => {
      expect(screen.getByText("Vertigo")).toBeInTheDocument();
    });

    const suggestionBtn = screen.getByText("Vertigo");
    fireEvent.click(suggestionBtn);

    expect(mockOnSelect).toHaveBeenCalledWith({
      value: "Vertigo",
      type: "movie",
    });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("resets input and fires onClear callback when clear button is clicked", async () => {
    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox") as HTMLInputElement;
    fireEvent.change(input, { target: { value: "vert" } });

    const clearBtn = screen.getByRole("button", { name: /Clear search/i });
    expect(clearBtn).toBeInTheDocument();

    fireEvent.click(clearBtn);

    expect(input.value).toBe("");
    expect(mockOnClear).toHaveBeenCalled();
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("navigates suggestions via ArrowDown, ArrowUp, and selects on Enter key", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [
          { value: "Vertigo", type: "movie" },
          { value: "Golden Gate Bridge", type: "location" },
        ],
      },
    });

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "vert" } });

    await waitFor(() => {
      expect(screen.getByText("Vertigo")).toBeInTheDocument();
    });

    // Press ArrowDown to highlight first suggestion ("Vertigo")
    fireEvent.keyDown(input, { key: "ArrowDown" });
    const option1 = screen.getByRole("option", { name: /Vertigo movie/i });
    expect(option1).toHaveAttribute("aria-selected", "true");

    // Press ArrowDown to highlight second suggestion ("Golden Gate Bridge")
    fireEvent.keyDown(input, { key: "ArrowDown" });
    const option2 = screen.getByRole("option", {
      name: /Golden Gate Bridge location/i,
    });
    expect(option2).toHaveAttribute("aria-selected", "true");

    // Press Enter to select highlighted suggestion
    fireEvent.keyDown(input, { key: "Enter" });

    expect(mockOnSelect).toHaveBeenCalledWith({
      value: "Golden Gate Bridge",
      type: "location",
    });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("closes dropdown on Escape key", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: {
        data: [{ value: "Vertigo", type: "movie" }],
      },
    });

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "vert" } });

    await waitFor(() => {
      expect(screen.getByText("Vertigo")).toBeInTheDocument();
    });

    fireEvent.keyDown(input, { key: "Escape" });
    expect(screen.queryByRole("listbox")).not.toBeInTheDocument();
  });

  it("renders empty state message when backend returns no suggestions", async () => {
    vi.mocked(apiClient.get).mockResolvedValueOnce({
      data: { data: [] },
    });

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "xyznonexistent" } });

    await waitFor(() => {
      expect(
        screen.getByText("No matching movies or locations found.")
      ).toBeInTheDocument();
    });
  });

  it("renders local error message when search API query fails", async () => {
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Network Error"));

    renderWithClient(
      <SearchAutocomplete onSelect={mockOnSelect} onClear={mockOnClear} />
    );

    const input = screen.getByRole("combobox");
    fireEvent.change(input, { target: { value: "errorquery" } });

    await waitFor(() => {
      expect(
        screen.getByText("Unable to load suggestions.")
      ).toBeInTheDocument();
    });
  });
});
