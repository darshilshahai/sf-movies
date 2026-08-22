import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";
import type { MovieLocation } from "../../types/movie";
import { SAN_FRANCISCO_CENTER, DEFAULT_MAP_ZOOM } from "../../constants/map";

type MapBoundsControllerProps = {
  movies: MovieLocation[];
  isFiltered: boolean;
};

/**
 * Controller component rendered inside MapContainer to adjust Leaflet viewport
 * based on returned movie coordinates and active search filter state.
 */
export default function MapBoundsController({
  movies,
  isFiltered,
}: MapBoundsControllerProps) {
  const map = useMap();

  useEffect(() => {
    if (!isFiltered) {
      // When filter is cleared, reset map to San Francisco default center & zoom
      map.setView(SAN_FRANCISCO_CENTER, DEFAULT_MAP_ZOOM);
      return;
    }

    if (movies.length === 0) {
      return;
    }

    if (movies.length === 1) {
      // Single marker: center view around marker coordinates with zoom 15
      const { latitude, longitude } = movies[0].coordinates;
      map.setView([latitude, longitude], 15);
      return;
    }

    // Multiple markers: fit bounds around all coordinates with padding
    const bounds = L.latLngBounds(
      movies.map((m) => [m.coordinates.latitude, m.coordinates.longitude])
    );
    map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
  }, [map, movies, isFiltered]);

  return null;
}
