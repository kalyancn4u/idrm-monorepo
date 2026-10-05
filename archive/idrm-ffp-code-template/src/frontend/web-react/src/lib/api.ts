/**
 * api.ts — typed fetch client for the IDRM admin SPA.
 *
 * Mirrors the HTML frontend's client (src/frontend/web-html/src/js/api/client.js):
 *   - tokens live in sessionStorage (cleared when the tab closes);
 *   - every authed call sends `Authorization: Bearer <access>`;
 *   - on a 401 we try ONE silent refresh via POST /auth/refresh, then retry once.
 *
 * Canonical contract (see start-here/COMPLETE-API-SPECS-GUIDE.md):
 *   - base path is /api/v1 (Vite/NGINX proxy to the gateway);
 *   - auth responses are BARE ({ access_token, refresh_token, expires_in, user });
 *   - list endpoints use the { status, data: { items, total, page, ... } } envelope.
 */

const API_BASE = "/api/v1";

/* ----------------------------- shared types ------------------------------ */

/** Account roles (UPPERCASE — must match the DB CHECK constraints). */
export type Role =
  | "CITIZEN" | "VOLUNTEER" | "ORGANIZER" | "PROVIDER" | "MANAGER"
  | "EVENT_MANAGER" | "EXECUTIVE" | "DM_AUTHORITY" | "AUDITOR" | "ADMIN";

export type ServiceType = "RESCUE" | "MEDICAL" | "FOOD" | "SHELTER" | "WATER" | "OTHER";
export type Priority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type RequestStatus =
  | "SUBMITTED" | "APPROVED" | "ACCEPTED" | "IN_PROGRESS" | "COMPLETED"
  | "VERIFIED" | "REJECTED" | "CANCELLED" | "EXPIRED" | "DISPUTED";

/** The logged-in user (UserOut exposes the PK as `id`). */
export interface User {
  id: string;
  email: string;
  full_name: string;
  phone?: string | null;
  role: Role;
  preferences?: { language?: string } | null;
  created_at?: string;
}

/** A single service-request row as returned by the list/detail endpoints. */
export interface ServiceRequest {
  service_id: string;
  service_type: ServiceType;
  description: string;
  priority: Priority;
  status: RequestStatus;
  address?: string | null;
  num_people_affected?: number | null;
  privacy_level?: "PUBLIC" | "PROTECTED" | "PRIVATE";
  contact_phone?: string | null;
  created_at: string;
  updated_at?: string;
  requestor?: Partial<User> | null;
}

/** The { status, data } envelope used by paginated list endpoints. */
export interface Paginated<T> {
  status: string;
  data: { items: T[]; total: number; page: number; per_page: number; pages: number };
}

/** Shape of GET /analytics/dashboard's `data` block. */
export interface DashboardData {
  total_requests: number;
  active_requests: number;
  avg_response_time_min: number;
  completion_rate: number;
  by_service_type: Record<string, number>;
  by_status: Record<string, number>;
}

/** Error thrown by apiFetch — carries the HTTP status + parsed body. */
export interface ApiError extends Error {
  status?: number;
  body?: unknown;
}

/* --------------------------- token plumbing ------------------------------ */

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
const USER_KEY = "user";

export const tokens = {
  access: () => sessionStorage.getItem(ACCESS_KEY),
  refresh: () => sessionStorage.getItem(REFRESH_KEY),
  set(access: string, refresh?: string) {
    sessionStorage.setItem(ACCESS_KEY, access);
    if (refresh) sessionStorage.setItem(REFRESH_KEY, refresh);
  },
  clear() {
    sessionStorage.removeItem(ACCESS_KEY);
    sessionStorage.removeItem(REFRESH_KEY);
    sessionStorage.removeItem(USER_KEY);
  },
};

/** Exchange the refresh token for a fresh access token. Returns false on failure. */
async function tryRefresh(): Promise<boolean> {
  const refresh_token = tokens.refresh();
  if (!refresh_token) return false;
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });
  if (!res.ok) return false;
  const body = (await res.json()) as { access_token?: string };
  if (!body.access_token) return false;
  tokens.set(body.access_token);
  return true;
}

/* ------------------------------ core fetch ------------------------------- */

interface FetchOptions extends RequestInit {
  /** Attach the bearer token (default true). Set false for login/refresh. */
  auth?: boolean;
  /** Internal: prevents infinite refresh→retry recursion. */
  _retried?: boolean;
}

/**
 * Perform an API call against /api/v1 and parse the JSON body.
 * Throws an {@link ApiError} (with `.status`) on any non-2xx response.
 */
export async function apiFetch<T = unknown>(path: string, options: FetchOptions = {}): Promise<T> {
  const { auth = true, headers, _retried, ...rest } = options;
  const access = tokens.access();

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(auth && access ? { Authorization: `Bearer ${access}` } : {}),
      ...(headers as Record<string, string> | undefined),
    },
  });

  // One transparent refresh-and-retry on an expired access token.
  if (res.status === 401 && auth && !_retried && (await tryRefresh())) {
    return apiFetch<T>(path, { ...options, _retried: true });
  }

  const body = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(
      (body as { detail?: string } | null)?.detail || `Request failed (${res.status})`,
    ) as ApiError;
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body as T;
}

/* ------------------------------ endpoints -------------------------------- */

/**
 * Authenticate, persist tokens + user, and return the user.
 * The auth response is BARE (no { status, data } wrapper).
 */
export async function login(email: string, password: string): Promise<User> {
  const data = await apiFetch<{ access_token: string; refresh_token: string; user: User }>(
    "/auth/login",
    { method: "POST", auth: false, body: JSON.stringify({ email, password }) },
  );
  tokens.set(data.access_token, data.refresh_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(data.user));
  return data.user;
}

/** Best-effort server-side logout; tokens are cleared by the caller regardless. */
export async function logout(): Promise<void> {
  try {
    await apiFetch("/auth/logout", { method: "POST" });
  } catch {
    /* ignore — local clear is what matters */
  } finally {
    tokens.clear();
  }
}

/** Current authenticated user (GET /users/me). */
export function getMe(): Promise<User> {
  return apiFetch<User>("/users/me");
}

/** Analytics summary for the dashboard (GET /analytics/dashboard). */
export async function getDashboard(): Promise<DashboardData> {
  const res = await apiFetch<{ status: string; data: DashboardData }>("/analytics/dashboard");
  return res.data;
}

/** Filters accepted by the request list (GET /services). */
export interface ListServicesParams {
  status?: RequestStatus;
  service_type?: ServiceType;
  priority?: Priority;
  page?: number;
  per_page?: number;
}

/** List service requests (paginated, { status, data } envelope). */
export function listServices(params: ListServicesParams = {}): Promise<Paginated<ServiceRequest>> {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) qs.set(k, String(v));
  });
  const suffix = qs.toString() ? `?${qs}` : "";
  return apiFetch<Paginated<ServiceRequest>>(`/services${suffix}`);
}

/** DM-Authority action: approve a SUBMITTED request (POST /services/{id}/approve). */
export function approveService(id: string, notes?: string): Promise<ServiceRequest> {
  return apiFetch<ServiceRequest>(`/services/${id}/approve`, {
    method: "POST",
    body: JSON.stringify({ notes: notes ?? "" }),
  });
}

/** DM-Authority action: reject a SUBMITTED request (POST /services/{id}/reject). */
export function rejectService(id: string, reason: string): Promise<ServiceRequest> {
  return apiFetch<ServiceRequest>(`/services/${id}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}
