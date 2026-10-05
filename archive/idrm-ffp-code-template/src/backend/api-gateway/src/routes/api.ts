/**
 * routes/api.ts — reverse proxy to the FastAPI backend.
 *
 * Forwards `/api/*` requests through to FastAPI (port 8000) unchanged, then returns
 * its response. The `extraHeaders` parameter lets later middleware inject trusted
 * context — in G3 the JWT middleware passes `X-User-ID` / `X-User-Role` here after
 * verifying the token (FastAPI then trusts those headers; see core/security.py).
 */
import { config } from "../config";

/**
 * Proxy a request to FastAPI and return its response.
 *
 * @param req          The incoming gateway request.
 * @param extraHeaders Extra headers to add to the upstream request (e.g. the
 *                     `X-User-*` context set by the G3 auth middleware).
 */
export async function proxyToFastAPI(
  req: Request,
  extraHeaders: Record<string, string> = {},
): Promise<Response> {
  const url = new URL(req.url);
  const target = `${config.fastApiUrl}${url.pathname}${url.search}`;

  const headers = new Headers(req.headers);
  headers.delete("host"); // let fetch set the correct upstream Host
  // 🚩 SECURITY: drop any client-supplied identity headers so a caller can't spoof
  // auth. Only the gateway's own verified values (extraHeaders, set by G3) are kept.
  headers.delete("x-user-id");
  headers.delete("x-user-role");
  headers.delete("x-user-email");
  for (const [key, value] of Object.entries(extraHeaders)) headers.set(key, value);

  // Buffer the body for non-GET/HEAD requests (simpler + avoids streaming/duplex
  // quirks; IDRM payloads are small JSON).
  const hasBody = req.method !== "GET" && req.method !== "HEAD";
  const body = hasBody ? await req.arrayBuffer() : undefined;

  try {
    // 30s ceiling so a slow/unresponsive backend can't hang the gateway forever.
    return await fetch(target, {
      method: req.method,
      headers,
      body,
      signal: AbortSignal.timeout(30_000),
    });
  } catch (err) {
    // FastAPI is unreachable (down/restarting/wrong URL) → 502, or too slow → 504.
    const timedOut = err instanceof Error && err.name === "TimeoutError";
    console.error("FastAPI proxy error:", err);
    return Response.json(
      {
        detail: timedOut ? "Upstream timed out" : "Upstream service unavailable",
        code: timedOut ? "GATEWAY_TIMEOUT" : "BAD_GATEWAY",
      },
      { status: timedOut ? 504 : 502 },
    );
  }
}
