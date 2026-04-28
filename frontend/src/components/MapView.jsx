import { useEffect } from "react";
import { CircleMarker, MapContainer, Marker, Polyline, TileLayer, useMapEvents } from "react-leaflet";
import { Map as MapIcon } from "lucide-react";
import { getRoute } from "../api/helmetApi";

function TapHandler({ setDestination, userPosition, setRoute, readOnly }) {
  useMapEvents({
    async click(e) {
      if (readOnly) return;
      const dest = { lat: e.latlng.lat, lng: e.latlng.lng };
      setDestination(dest);
      if (userPosition) {
        const route = await getRoute(userPosition.lat, userPosition.lng, dest.lat, dest.lng);
        setRoute(route);
      }
    },
  });
  return null;
}

function getRiskColor(risk) {
  if (risk > 70) return "#ef4444";
  if (risk > 40) return "#f97316";
  return "#22c55e";
}

export default function MapView({
  userPosition,
  setUserPosition,
  destination,
  setDestination,
  route,
  setRoute,
  obstaclePins,
  riskSegments,
  readOnly = false,
}) {
  useEffect(() => {
    if (readOnly || !navigator.geolocation) return;
    const watcher = navigator.geolocation.watchPosition((pos) => {
      setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
    });
    return () => navigator.geolocation.clearWatch(watcher);
  }, [setUserPosition, readOnly]);

  const center = userPosition ? [userPosition.lat, userPosition.lng] : [18.5204, 73.8567];
  const routeLatLng = (route.coordinates ?? []).map(([lng, lat]) => [lat, lng]);

  return (
    <div className="visual-card" style={readOnly ? { height: "100%", margin: 0, padding: 0 } : {}}>
      {!readOnly && <div className="visual-title"><MapIcon size={12} /> LIVE TACTICAL MAP</div>}
      <MapContainer center={center} zoom={15} style={{ height: readOnly ? "100%" : 360, borderRadius: 10 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <TapHandler setDestination={setDestination} userPosition={userPosition} setRoute={setRoute} readOnly={readOnly} />
        {userPosition && <CircleMarker center={[userPosition.lat, userPosition.lng]} radius={8} pathOptions={{ color: "#3b82f6" }} />}
        {destination && <Marker position={[destination.lat, destination.lng]} />}
        {riskSegments?.length > 0
          ? riskSegments.map((seg, i) => (
              <Polyline key={i} positions={seg.coords} pathOptions={{ color: getRiskColor(seg.risk), weight: 6 }} />
            ))
          : routeLatLng.length > 1 && <Polyline positions={routeLatLng} pathOptions={{ color: "#38bdf8" }} />}
        {obstaclePins.map((p, i) => (
          <Marker key={i} position={[p.lat, p.lng]} />
        ))}
      </MapContainer>
    </div>
  );
}
