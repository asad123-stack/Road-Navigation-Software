import { useEffect } from "react";
import { CircleMarker, MapContainer, Marker, Polyline, TileLayer, useMapEvents } from "react-leaflet";
import { getRoute } from "../api/helmetApi";

function TapHandler({ setDestination, userPosition, setRoute }) {
  useMapEvents({
    async click(e) {
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
}) {
  useEffect(() => {
    if (!navigator.geolocation) return;
    const watcher = navigator.geolocation.watchPosition((pos) => {
      setUserPosition({ lat: pos.coords.latitude, lng: pos.coords.longitude });
    });
    return () => navigator.geolocation.clearWatch(watcher);
  }, [setUserPosition]);

  const center = userPosition ? [userPosition.lat, userPosition.lng] : [18.5204, 73.8567];
  const routeLatLng = (route.coordinates ?? []).map(([lng, lat]) => [lat, lng]);

  return (
    <div className="visual-card">
      <div className="visual-title">Live Map</div>
      <MapContainer center={center} zoom={15} style={{ height: 360, borderRadius: 10 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <TapHandler setDestination={setDestination} userPosition={userPosition} setRoute={setRoute} />
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
