import L from "leaflet";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import type { MovieLocation } from "../../types/movie";
import { SAN_FRANCISCO_CENTER, DEFAULT_MAP_ZOOM } from "../../constants/map";

// Import Leaflet marker assets explicitly for Vite bundler compatibility
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Reconfigure Leaflet's default marker icons to avoid broken asset URLs in Vite
delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: () => void })._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

type MovieMapProps = {
  movies: MovieLocation[];
};

/**
 * Presentational component rendering an interactive Leaflet map focused on San Francisco.
 * Places markers at latitude/longitude coordinates for each normalized film location.
 */
export default function MovieMap({ movies }: MovieMapProps) {
  return (
    <div className="w-full h-[500px] md:h-[650px] rounded-xl overflow-hidden shadow-2xl border border-slate-800 relative z-0">
      <MapContainer
        center={SAN_FRANCISCO_CENTER}
        zoom={DEFAULT_MAP_ZOOM}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {movies.map((movie, index) => (
          <Marker
            key={`${movie.title}-${movie.location}-${movie.coordinates.latitude}-${movie.coordinates.longitude}-${index}`}
            position={[movie.coordinates.latitude, movie.coordinates.longitude]}
          >
            <Popup>
              <div className="p-1 max-w-xs space-y-1 text-slate-900">
                <h3 className="font-bold text-sm leading-snug">
                  {movie.title}
                </h3>
                {movie.release_year && (
                  <p className="text-xs font-semibold text-slate-500">
                    Released: {movie.release_year}
                  </p>
                )}
                <p className="text-xs text-slate-700 font-medium">
                  📍 {movie.location}
                </p>
                {movie.director && (
                  <p className="text-xs text-slate-500 italic pt-1 border-t border-slate-200 mt-1">
                    Directed by {movie.director}
                  </p>
                )}
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
