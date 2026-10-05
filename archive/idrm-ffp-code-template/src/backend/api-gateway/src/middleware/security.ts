/**
 * middleware/security.ts — security headers added to EVERY response.
 *
 * These defend the browser frontends against common attacks (clickjacking, MIME
 * sniffing, mixed content, etc.). The Content-Security-Policy allow-lists the few
 * CDNs the HTML frontend uses (Tailwind/Leaflet/Axios), OSM map tiles, and the
 * WebSocket endpoint.
 */

/** The static security headers applied to all responses. */
export const SECURITY_HEADERS: Record<string, string> = {
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "X-XSS-Protection": "1; mode=block",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net", // Tailwind, Leaflet, Axios from CDN
    "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net unpkg.com",
    "img-src 'self' data: tile.openstreetmap.org", // OSM map tiles
    "connect-src 'self' ws://localhost:3001 wss://api.idrm.gov.in",
    "font-src 'self'",
    "frame-ancestors 'none'",
  ].join("; "),
};

/**
 * Return a copy of `response` with the security headers (and any `extra` headers,
 * e.g. CORS) merged in.
 *
 * We build the merged `Headers` first and construct a fresh `Response`, because a
 * Response returned by `fetch()` can have immutable headers.
 */
export function addSecurityHeaders(response: Response, extra: Record<string, string> = {}): Response {
  const headers = new Headers(response.headers);
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) headers.set(key, value);
  for (const [key, value] of Object.entries(extra)) headers.set(key, value);
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}
