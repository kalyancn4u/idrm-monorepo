/**
 * index.ts — IDRM API Gateway entry point (Bun.serve).
 *
 * RUN IT:
 *     cd src/backend/api-gateway && bun run dev      # HTTP :3000 · WebSocket :3001
 *
 * VERIFY (with the FastAPI backend running on :8000):
 *     curl http://localhost:3000/api/v1/health       # → the backend's health JSON
 *
 * The gateway sits in front of FastAPI and handles cross-cutting concerns:
 *   • CORS (preflight + headers) and security headers      ← G1
 *   • Rate limiting (per IP + endpoint)                    ← G2
 *   • JWT verification → inject X-User-* and proxy         ← G3
 *   • WebSocket fan-out (separate :3001 server)            ← G4
 *
 * HTTP flow (port 3000): OPTIONS → preflight; else rate-limit (→ 429) → JWT auth
 * (→ 401) → route. `/api/*` is proxied to FastAPI (with the verified X-User-*
 * headers), everything else is 404. CORS + security (+ rate-limit) headers are
 * added to every response. WebSocket (port 3001) is its own server at the bottom.
 */
import { config } from "./config";
import { authenticate } from "./middleware/auth";
import { corsHeaders, preflightResponse } from "./middleware/cors";
import { checkRateLimit } from "./middleware/rateLimit";
import { addSecurityHeaders } from "./middleware/security";
import { proxyToFastAPI } from "./routes/api";
import { handleClose, handleMessage, handleOpen, startRedisBridge, type WsData } from "./routes/websocket";

// --- HTTP server (port 3000) -------------------------------------------------
const server = Bun.serve({
  port: config.port,

  async fetch(req): Promise<Response> {
    const url = new URL(req.url);
    const path = url.pathname;
    const origin = req.headers.get("Origin");
    // (WebSocket lives on its own server — see the bottom of this file — not here.)

    // CORS preflight — answer OPTIONS directly, never proxied or rate-limited.
    if (req.method === "OPTIONS") {
      return preflightResponse(origin);
    }

    // --- G2: rate limit (per IP + endpoint) ----------------------------------
    const rate = await checkRateLimit(req);
    if (rate.limited) {
      return addSecurityHeaders(rate.limited, corsHeaders(origin));
    }

    // --- G3: JWT auth (verify token, forward identity) -----------------------
    const auth = await authenticate(req);
    if (auth.denied) {
      return addSecurityHeaders(auth.denied, corsHeaders(origin));
    }

    // Route: proxy the API (injecting the verified X-User-* headers); everything
    // else is 404 here (static files are served by Vite in dev / NGINX in prod).
    let response: Response;
    if (path.startsWith("/api/")) {
      response = await proxyToFastAPI(req, auth.userHeaders);
    } else {
      response = Response.json({ detail: "Not found", code: "NOT_FOUND" }, { status: 404 });
    }

    // Add CORS + security + rate-limit headers to every outgoing response.
    return addSecurityHeaders(response, { ...corsHeaders(origin), ...rate.headers });
  },
});

// --- G4: WebSocket server (port 3001) ----------------------------------------
// A separate Bun.serve so the URL is ws://localhost:3001 (per the API contract).
// `fetch` upgrades WebSocket requests; the handlers live in routes/websocket.ts.
const wsServer = Bun.serve<WsData>({
  port: config.wsPort,
  fetch(req, srv) {
    if (srv.upgrade(req, { data: { channels: new Set<string>() } })) return; // upgraded → no Response
    return new Response("IDRM WebSocket endpoint — connect with a WebSocket client.", { status: 426 });
  },
  websocket: {
    open: handleOpen,
    message: handleMessage,
    close: handleClose,
  },
});

// Start relaying Redis pub/sub events to WebSocket clients (best-effort; no-op without REDIS_URL).
void startRedisBridge();

console.log(
  `IDRM API Gateway → http://localhost:${server.port}  ·  WebSocket → ws://localhost:${wsServer.port}` +
    `  (proxying /api/* to ${config.fastApiUrl})`,
);
