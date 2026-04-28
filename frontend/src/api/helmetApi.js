import axios from "axios";

const API_BASE = import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:5000";

export async function processFrame(frame, lat, lng, route = null) {
  const payload = { frame, lat, lng };
  if (route) {
    payload.route = route;
  }
  const res = await axios.post(`${API_BASE}/api/process_frame`, payload);
  return res.data;
}

export async function getRoute(originLat, originLng, destLat, destLng) {
  const url = `https://router.project-osrm.org/route/v1/driving/${originLng},${originLat};${destLng},${destLat}?geometries=geojson&steps=true&overview=full`;
  const res = await axios.get(url);
  return {
    coordinates: res.data.routes?.[0]?.geometry?.coordinates ?? [],
    steps: res.data.routes?.[0]?.legs?.[0]?.steps ?? [],
  };
}
