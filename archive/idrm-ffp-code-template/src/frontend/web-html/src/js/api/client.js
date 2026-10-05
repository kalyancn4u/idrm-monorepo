/**
 * js/api/client.js — the IDRM API client (dependency-free `fetch` wrapper).
 *
 * Every call targets a RELATIVE path under `/api/v1`, which Vite's dev proxy (and
 * NGINX in production) forwards to the Bun gateway on :3000. The wrapper:
 *   • attaches `Authorization: Bearer <access_token>`,
 *   • refreshes the access token PROACTIVELY (~1 min before it expires),
 *   • refreshes REACTIVELY once on a 401 and retries,
 *   • parses JSON and throws a friendly Error on a non-2xx response.
 *
 * Tokens live in `sessionStorage` (cleared when the tab closes). Auth endpoints
 * return the BARE token object — `{ access_token, refresh_token, expires_in, user }`
 * (see CLAUDE.md §Auth) — while list endpoints use the `{ status, data }` envelope;
 * callers pick the fields they need from the parsed body.
 */

const API_BASE = "/api/v1";
const REFRESH_SKEW_MS = 60_000; // refresh this long before the token actually expires

// ---- token storage (sessionStorage) ----------------------------------------
const KEY_ACCESS = "access_token";
const KEY_REFRESH = "refresh_token";
const KEY_EXPIRES = "access_expires_at"; // epoch milliseconds
const KEY_USER = "user";

export const getAccessToken = () => sessionStorage.getItem(KEY_ACCESS);
export const getRefreshToken = () => sessionStorage.getItem(KEY_REFRESH);
export const isAuthenticated = () => !!getAccessToken();

/** The signed-in user object (or null). */
export function getUser() {
  try {
    return JSON.parse(sessionStorage.getItem(KEY_USER) || "null");
  } catch {
    return null;
  }
}

/** Persist whatever an auth response returned (any missing fields are skipped). */
function storeSession({ access_token, refresh_token, expires_in, user } = {}) {
  if (access_token) sessionStorage.setItem(KEY_ACCESS, access_token);
  if (refresh_token) sessionStorage.setItem(KEY_REFRESH, refresh_token);
  if (typeof expires_in === "number") {
    sessionStorage.setItem(KEY_EXPIRES, String(Date.now() + expires_in * 1000));
  }
  if (user) sessionStorage.setItem(KEY_USER, JSON.stringify(user));
}

/** Forget the session (on logout, or when a refresh fails). */
export function clearSession() {
  [KEY_ACCESS, KEY_REFRESH, KEY_EXPIRES, KEY_USER].forEach((k) => sessionStorage.removeItem(k));
}

// ---- token refresh ----------------------------------------------------------
/** True if there's an access token whose expiry is within REFRESH_SKEW_MS. */
function accessTokenExpiringSoon() {
  const expiresAt = Number(sessionStorage.getItem(KEY_EXPIRES) || 0);
  return expiresAt > 0 && Date.now() >= expiresAt - REFRESH_SKEW_MS;
}

/** Exchange the refresh token for a fresh access token. Clears session on failure. */
export async function refreshAccessToken() {
  const refresh_token = getRefreshToken();
  if (!refresh_token) throw new Error("No refresh token");
  const res = await fetch(`${API_BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });
  if (!res.ok) {
    clearSession();
    throw new Error("Session expired — please sign in again");
  }
  const data = await res.json(); // { access_token, token_type, expires_in }
  storeSession(data);
  return data.access_token;
}

// ---- core request -----------------------------------------------------------
/**
 * Call the API. `path` is relative to `/api/v1` (e.g. `"/services?status=SUBMITTED"`).
 *
 * @param {string} path
 * @param {RequestInit & { auth?: boolean }} [options]  pass `auth: false` for public calls
 * @returns {Promise<any>} the parsed JSON body (or null for 204)
 * @throws  {Error & { status?: number, body?: any }} on a non-2xx response
 */
export async function apiFetch(path, options = {}) {
  const { auth = true, headers = {}, ...rest } = options;

  // Proactive refresh — renew before the token lapses (best-effort; the 401 path
  // below is the safety net).
  if (auth && getAccessToken() && accessTokenExpiringSoon()) {
    try {
      await refreshAccessToken();
    } catch {
      /* ignore — handled reactively below */
    }
  }

  const doFetch = () =>
    fetch(`${API_BASE}${path}`, {
      ...rest,
      headers: {
        "Content-Type": "application/json",
        ...(auth && getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
        ...headers,
      },
    });

  let res = await doFetch();

  // Reactive refresh — one retry if the token was rejected.
  if (res.status === 401 && auth && getRefreshToken()) {
    try {
      await refreshAccessToken();
      res = await doFetch();
    } catch {
      /* fall through to the error below */
    }
  }

  const body = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    throw Object.assign(new Error(body?.detail || `Request failed (${res.status})`), {
      status: res.status,
      body,
    });
  }
  return body;
}

// ---- convenience helpers ----------------------------------------------------
/** Sign in; stores the token pair + user and returns the user. */
export async function login(email, password) {
  const data = await apiFetch("/auth/login", {
    auth: false,
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  storeSession(data);
  return data.user;
}

/**
 * Create a new account (self-roles: CITIZEN / PROVIDER / VOLUNTEER only). Returns
 * the created user — it does NOT sign in (call `login` afterwards).
 * @param {{email:string, password:string, full_name:string, phone?:string, role?:string, language_preference?:string}} payload
 */
export const register = (payload) =>
  apiFetch("/auth/register", { auth: false, method: "POST", body: JSON.stringify(payload) });

/** Sign out (best-effort server call) and clear the local session. */
export async function logout() {
  try {
    await apiFetch("/auth/logout", { method: "POST" });
  } catch {
    /* ignore network/expiry errors — we clear locally regardless */
  }
  clearSession();
}

/** Liveness check (no auth) — e.g. `{ status: "ok", service, environment }`. */
export const health = () => apiFetch("/health", { auth: false });

/** The signed-in user's profile (GET /users/me). */
export const getMe = () => apiFetch("/users/me");

/** Update the signed-in user's own profile (POST /users/me).
 *  `payload` = { full_name?, phone?, preferences? } — `preferences` is merged server-side. */
export const updateMe = (payload) => apiFetch("/users/me", { method: "POST", body: JSON.stringify(payload) });
