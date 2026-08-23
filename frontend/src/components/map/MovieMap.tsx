import L from "leaflet";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import type { MovieLocation } from "../../types/movie";
import { SAN_FRANCISCO_CENTER, DEFAULT_MAP_ZOOM } from "../../constants/map";
import MoviePopup from "./MoviePopup";
import MapBoundsController from "./MapBoundsController";

import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

delete (L.Icon.Default.prototype as unknown as { _getIconUrl?: () => void })._getIconUrl;

L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

type MovieMapProps = {
  movies: MovieLocation[];
  isFiltered?: boolean;
};

export default function MovieMap({ movies, isFiltered = false }: MovieMapProps) {
  return (
    <div className="w-full h-[450px] md:h-[550px] lg:h-[650px] rounded-xl overflow-hidden shadow-2xl border border-slate-800 relative z-0">
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

        <MapBoundsController movies={movies} isFiltered={isFiltered} />

        {movies.map((movie, index) => (
          <Marker
            key={`${movie.title}-${movie.location}-${movie.coordinates.latitude}-${movie.coordinates.longitude}-${index}`}
            position={[movie.coordinates.latitude, movie.coordinates.longitude]}
          >
            <Popup>
              <MoviePopup movie={movie} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
