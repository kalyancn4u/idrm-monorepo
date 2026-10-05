/**
 * js/auth-guard.js — tiny client-side page guards.
 *
 * Import and call at the very top of a page's module script:
 *   • `requireAuth()`      on a protected page — bounce to login if not signed in.
 *   • `redirectIfAuthed()` on login/register   — skip to the dashboard if already in.
 *
 * This is a UX convenience only — the REAL access control is the gateway (G3) +
 * backend, which reject unauthenticated/forbidden API calls regardless.
 */
import { isAuthenticated } from "./api/client.js";

const LOGIN_URL = "/src/pages/login.html";
const DASHBOARD_URL = "/src/pages/dashboard.html";

/** Redirect to login (preserving where we were headed) unless signed in. */
export function requireAuth() {
  if (!isAuthenticated()) {
    const next = encodeURIComponent(location.pathname + location.search);
    location.replace(`${LOGIN_URL}?next=${next}`);
    return false;
  }
  return true;
}

/** On auth pages: if already signed in, go straight to the dashboard. */
export function redirectIfAuthed() {
  if (isAuthenticated()) location.replace(DASHBOARD_URL);
}
