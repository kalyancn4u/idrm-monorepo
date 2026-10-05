/**
 * middleware/auth.ts — JWT authentication at the edge (Module G3).
 *
 * Each request falls into one of three modes:
 *   • PUBLIC   — login / register / refresh / health: no token needed, skip entirely.
 *   • OPTIONAL — GET /geo/* and GET /services*: the public map. If a valid token is
 *                present we still forward the identity (so a logged-in requestor
 *                sees their own private details); with no token we pass through
 *                anonymously.
 *   • REQUIRED — everything else under /api/*: a valid access token is mandatory,
 *                otherwise 401.
 *
 * On success we hand the verified identity to the proxy as `X-User-ID` /
 * `X-User-Role` headers, which the FastAPI backend trusts (see core/security.py's
 * `get_current_user`). 🚩 The proxy also STRIPS any client-supplied `X-User-*`
 * headers first (see routes/api.ts) so a caller can never spoof their identity.
 */
import { config } from "../config";
import { verifyJwtHS256 } from "../utils/jwt";

/** Paths reachable with NO token at all. */
const PUBLIC_PREFIXES = [
  "/api/v1/health",
  "/api/v1/auth/login",
  "/api/v1/auth/register",
  "/api/v1/auth/refresh",
];

type AuthMode = "public" | "optional" | "required";

/** Classify a request into its auth mode. */
function authMode(method: string, path: string): AuthMode {
  if (PUBLIC_PREFIXES.some((p) => path.startsWith(p))) return "public";
  // Public, read-only browsing for the map (writes are POSTs → "required").
  if (method === "GET" && (path.startsWith("/api/v1/geo") || path.startsWith("/api/v1/services"))) {
    return "optional";
  }
  return "required";
}

/** Pull the token from `Authorization: Bearer …` or the `access_token` cookie. */
function extractToken(req: Request): string | null {
  const authHeader = req.headers.get("Authorization");
  if (authHeader && authHeader.toLowerCase().startsWith("bearer ")) {
    return authHeader.slice(7).trim();
  }
  // httpOnly cookie fallback (browser sessions).
  const cookie = req.headers.get("Cookie") || "";
  const match = cookie.match(/(?:^|;\s*)access_token=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : null;
}

function unauthorized(message: string): Response {
  return Response.json(
    { detail: message, code: "UNAUTHORIZED" },
    { status: 401, headers: { "WWW-Authenticate": 'Bearer realm="IDRM API"' } },
  );
}

/**
 * Authenticate a request.
 *
 * @returns `denied` — a 401 Response when auth fails (the caller returns it), else
 *          null; and `userHeaders` — the verified `X-User-*` headers to forward to
 *          FastAPI (empty for anonymous/public requests).
 */
export async function authenticate(
  req: Request,
): Promise<{ denied: Response | null; userHeaders: Record<string, string> }> {
  const path = new URL(req.url).pathname;
  const mode = authMode(req.method, path);

  if (mode === "public") return { denied: null, userHeaders: {} };

  const token = extractToken(req);
  if (!token) {
    // Optional endpoints are fine without a token (anonymous view); required ones aren't.
    if (mode === "optional") return { denied: null, userHeaders: {} };
    return { denied: unauthorized("No authentication token provided"), userHeaders: {} };
  }

  // A token IS present (optional or required) — it must be valid, even on optional paths.
  try {
    const claims = await verifyJwtHS256(token, config.jwtSecret);
    if (claims.type && claims.type !== "access") {
      return { denied: unauthorized("Wrong token type — use the access token"), userHeaders: {} };
    }
    const userHeaders: Record<string, string> = { "X-User-ID": String(claims.sub) };
    if (claims.role) userHeaders["X-User-Role"] = String(claims.role);
    return { denied: null, userHeaders };
  } catch (err) {
    return { denied: unauthorized(err instanceof Error ? err.message : "Invalid token"), userHeaders: {} };
  }
}
