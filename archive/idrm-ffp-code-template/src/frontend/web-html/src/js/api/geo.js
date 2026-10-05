/**
 * js/api/geo.js — geospatial (map) API calls. These are public/read-only, so no
 * auth token is sent.
 *   geoNearby  → { center, radius_km, total, results: [{ service_id, service_type,
 *                  priority, status, address, location:{coordinates:[lon,lat]}, distance_km }] }
 *   geoCluster → { clusters: [{ latitude, longitude, count, priority_breakdown }] }
 */
import { apiFetch } from "./client.js";

/** Build a `?a=1&b=2` query string, skipping empty/undefined values. */
function query(params = {}) {
  const usp = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "") usp.set(key, value);
  }
  const qs = usp.toString();
  return qs ? `?${qs}` : "";
}

/** Requests within a radius (km) of a point, nearest first. `service_type` optional. */
export const geoNearby = (params) => apiFetch(`/geo/nearby${query(params)}`, { auth: false });

/** Aggregated clusters for a zoom level (optionally limited to a `south,west,north,east` box). */
export const geoCluster = (params) => apiFetch(`/geo/cluster${query(params)}`, { auth: false });
