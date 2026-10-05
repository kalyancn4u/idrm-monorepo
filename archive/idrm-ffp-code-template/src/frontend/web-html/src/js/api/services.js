/**
 * js/api/services.js — service-request API calls (built on the core `apiFetch`).
 *
 * Paths are canonical (CLAUDE.md / backend M3): `/services`, `/services/{id}`, and
 * the POST action sub-endpoints `/services/{id}/<action>`. (Note: the older
 * `instructions_pages_v3.md` shows `/services/requests` + `PUT …/status` — that's
 * stale; this module uses the canonical shape.)
 *
 * `listServices` returns the `{ status, data: { items, total, page, per_page, pages } }`
 * envelope; the create/detail/action calls return a bare ServiceOut object.
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

/** Create a request. `payload` matches ServiceCreate (service_type, priority,
 *  description, location {type:"Point", coordinates:[lon,lat]}, …). */
export const createService = (payload) =>
  apiFetch("/services", { method: "POST", body: JSON.stringify(payload) });

/** List requests. Pass `{ mine: true }` for the signed-in user's own; also accepts
 *  `status`, `service_type`, `priority`, `page`, `per_page`. */
export const listServices = (params = {}) => apiFetch(`/services${query(params)}`);

/** Fetch one request's full detail (privacy applied server-side). */
export const getService = (id) => apiFetch(`/services/${id}`);

/** POST a lifecycle action; `body` is the action's payload (may be empty). */
const action = (id, name, body = {}) =>
  apiFetch(`/services/${id}/${name}`, { method: "POST", body: JSON.stringify(body) });

// ---- citizen (requestor) actions -------------------------------------------
export const verifyService = (id, rating, feedback) => action(id, "verify", { rating, feedback });
export const cancelService = (id, reason) => action(id, "cancel", { reason });
export const disputeService = (id, reason) => action(id, "dispute", { reason });

// ---- provider / DM actions (used by the provider + admin pages) ------------
export const acceptService = (id, org_id, notes) => action(id, "accept", { org_id, notes });
export const startService = (id) => action(id, "start", {});
export const completeService = (id, notes) => action(id, "complete", { notes });
export const approveService = (id, notes) => action(id, "approve", { notes });
export const rejectService = (id, reason) => action(id, "reject", { reason });
