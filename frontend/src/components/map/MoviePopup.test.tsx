import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import MoviePopup from "./MoviePopup";
import type { MovieLocation } from "../../types/movie";

describe("MoviePopup Component", () => {
  const fullMovie: MovieLocation = {
    title: "Vertigo",
    release_year: 1958,
    location: "Mission Dolores",
    coordinates: { latitude: 37.76, longitude: -122.42 },
    director: "Alfred Hitchcock",
    production_company: "Paramount Pictures",
    distributor: "Paramount Pictures",
    writer: "Alec Coppel",
    actors: ["James Stewart", "Kim Novak"],
    fun_facts: "Famous bell tower climax scene",
    neighborhood: "Mission District",
  };

  const minimalMovie: MovieLocation = {
    title: "The Rock",
    release_year: null,
    location: "Alcatraz Island",
    coordinates: { latitude: 37.82, longitude: -122.42 },
    director: null,
    production_company: null,
    distributor: null,
    writer: null,
    actors: [],
    fun_facts: null,
    neighborhood: null,
  };

  it("renders full movie metadata correctly when all fields are provided", () => {
    render(<MoviePopup movie={fullMovie} />);

    expect(screen.getByText("Vertigo")).toBeInTheDocument();
    expect(screen.getByText("1958")).toBeInTheDocument();
    expect(screen.getByText("Mission Dolores")).toBeInTheDocument();
    expect(screen.getByText("Mission District")).toBeInTheDocument();
    expect(screen.getByText("Alfred Hitchcock")).toBeInTheDocument();
    expect(screen.getByText("James Stewart • Kim Novak")).toBeInTheDocument();
    expect(screen.getByText("Paramount Pictures")).toBeInTheDocument();
    expect(
      screen.getByText("Famous bell tower climax scene")
    ).toBeInTheDocument();
  });

  it("renders minimal movie metadata hiding absent optional fields cleanly", () => {
    render(<MoviePopup movie={minimalMovie} />);

    expect(screen.getByText("The Rock")).toBeInTheDocument();
    expect(screen.getByText("Alcatraz Island")).toBeInTheDocument();

    expect(screen.queryByText(/Director/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Cast/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Studio/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Fun Fact/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/null/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/undefined/i)).not.toBeInTheDocument();
  });
});
