/**
 * middleware/cors.ts — Cross-Origin Resource Sharing for the browser frontends.
 *
 * Browsers block cross-origin calls unless the server opts in. Our frontends run
 * on different ports (5173 HTML, 5174 React) than the gateway (3000), so we echo
 * an allowed Origin back. IDRM uses only GET and POST, so those (plus the OPTIONS
 * preflight) are the only methods advertised.
 */
import { config } from "../config";

/**
 * Build the CORS response headers for a given request `Origin`.
 *
 * If the Origin is in the allow-list we echo it back (required when credentials
 * are allowed — you can't use `*`); otherwise we fall back to the first allowed
 * origin. `Vary: Origin` keeps caches from serving the wrong origin's headers.
 */
export function corsHeaders(origin: string | null): Record<string, string> {
  const allowed = origin && config.corsOrigins.includes(origin) ? origin : config.corsOrigins[0];
  return {
    "Access-Control-Allow-Origin": allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Authorization, Content-Type, Accept",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Max-Age": "86400",
    Vary: "Origin",
  };
}

/** Build the 204 response a browser expects for a CORS preflight (OPTIONS) request. */
export function preflightResponse(origin: string | null): Response {
  return new Response(null, { status: 204, headers: corsHeaders(origin) });
}
