/**
 * js/map-view.js — the live map (pages/map-view.html).
 *
 * Auth-gated. Shows active requests on a Leaflet/OSM map: priority-coloured markers
 * when zoomed in (GET /geo/nearby) and aggregated cluster circles when zoomed out
 * (GET /geo/cluster). A WebSocket subscribed to `service_requests` (G4) triggers a
 * debounced refresh, so new/updated requests appear in near-real-time.
 *
 * GeoJSON note: the API returns coordinates as [lon, lat]; Leaflet wants [lat, lng].
 */
import { geoCluster, geoNearby } from "./api/geo.js";
import { requireAuth } from "./auth-guard.js";
import { escapeHtml, mountAppHeader } from "./ui.js";

const L = window.L; // Leaflet global (CDN <script> in <head>)
const HYDERABAD = [17.385, 78.4867]; // [lat, lng]
const CLUSTER_BELOW_ZOOM = 12; // zoom < this → clusters; >= → individual markers
const PRIORITY_COLOR = { CRITICAL: "#ef4444", HIGH: "#f97316", MEDIUM: "#f59e0b", LOW: "#10b981" };
const PRIORITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

let map;
let layer; // holds the current markers/clusters
let serviceType = "";
let refreshTimer = null;

if (requireAuth()) {
  mountAppHeader("map");
  initMap();
  document.getElementById("type-filter")?.addEventListener("change", (e) => {
    serviceType = e.target.value;
    refresh();
  });
  connectWebSocket();
}

function setStatus(text) {
  const el = document.getElementById("map-status");
  if (el) el.textContent = text;
}

function initMap() {
  const el = document.getElementById("map");
  if (!L) {
    el.innerHTML = '<p class="p-4 text-sm text-red-600">Map failed to load.</p>';
    return;
  }
  map = L.map("map").setView(HYDERABAD, 12);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);
  layer = L.layerGroup().addTo(map);
  map.on("moveend", scheduleRefresh); // also fires on zoom
  refresh();
}

/** Debounce refreshes from rapid pan/zoom or a burst of WebSocket events. */
function scheduleRefresh() {
  clearTimeout(refreshTimer);
  refreshTimer = setTimeout(refresh, 400);
}

async function refresh() {
  if (!map) return;
  const zoom = map.getZoom();
  try {
    if (zoom < CLUSTER_BELOW_ZOOM) await drawClusters(zoom);
    else await drawMarkers();
  } catch (err) {
    setStatus(`Couldn't load map data (${err.message}).`);
  }
}

async function drawMarkers() {
  const center = map.getCenter();
  // Radius that roughly covers the viewport (capped at the API's 50 km max).
  const radiusKm = Math.min(50, Math.max(1, Math.ceil(center.distanceTo(map.getBounds().getNorthEast()) / 1000)));
  const data = await geoNearby({
    latitude: center.lat,
    longitude: center.lng,
    radius: radiusKm,
    service_type: serviceType,
  });
  layer.clearLayers();
  for (const r of data.results) {
    const [lon, lat] = r.location.coordinates;
    L.circleMarker([lat, lon], markerStyle(r.priority)).addTo(layer).bindPopup(popupHtml(r));
  }
  setStatus(`${data.total} request(s) within ${radiusKm} km`);
}

async function drawClusters(zoom) {
  const b = map.getBounds();
  const bounds = `${b.getSouth()},${b.getWest()},${b.getNorth()},${b.getEast()}`; // south,west,north,east
  const data = await geoCluster({ zoom: Math.min(20, Math.max(1, zoom)), bounds });
  layer.clearLayers();
  let total = 0;
  for (const cl of data.clusters) {
    total += cl.count;
    const color = dominantColor(cl.priority_breakdown);
    L.circleMarker([cl.latitude, cl.longitude], {
      radius: clusterRadius(cl.count),
      color,
      fillColor: color,
      fillOpacity: 0.5,
      weight: 2,
    })
      .addTo(layer)
      .bindTooltip(String(cl.count), { permanent: true, direction: "center", className: "cluster-label" });
  }
  setStatus(`${total} request(s) in ${data.clusters.length} cluster(s) · zoom in for individual pins`);
}

function markerStyle(priority) {
  const color = PRIORITY_COLOR[priority] || "#64748b";
  return { radius: 8, color, fillColor: color, fillOpacity: 0.85, weight: 2 };
}

function clusterRadius(count) {
  return Math.min(28, 10 + Math.log2(count + 1) * 4);
}

/** Colour a cluster by the highest priority present in it. */
function dominantColor(breakdown = {}) {
  for (const p of PRIORITY_ORDER) if (breakdown[p] > 0) return PRIORITY_COLOR[p];
  return "#64748b";
}

function popupHtml(r) {
  return `<div class="text-sm">
      <div class="font-semibold text-slate-900">${escapeHtml(r.service_type)} · ${escapeHtml(r.priority)}</div>
      <div class="text-slate-500">${escapeHtml(r.status)}${r.address ? " · " + escapeHtml(r.address) : ""}</div>
      <a href="/src/pages/service-detail.html?id=${encodeURIComponent(r.service_id)}" class="text-emerald-600 underline">View request</a>
    </div>`;
}

// ---- WebSocket: near-real-time updates --------------------------------------
function connectWebSocket() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  let ws;
  try {
    ws = new WebSocket(`${proto}://${location.host}/ws`); // Vite proxies /ws → gateway :3001
  } catch {
    return; // no live updates; the map still works via polling on pan/zoom
  }
  ws.addEventListener("open", () => ws.send(JSON.stringify({ type: "subscribe", channel: "service_requests" })));
  ws.addEventListener("message", (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      return;
    }
    // Backend events look like { type: "request_created"|"request_updated", request: {…} }.
    if (typeof msg.type === "string" && msg.type.startsWith("request_")) scheduleRefresh();
  });
  ws.addEventListener("close", () => setTimeout(connectWebSocket, 5000)); // simple reconnect
}
