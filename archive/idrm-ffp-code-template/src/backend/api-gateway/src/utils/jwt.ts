/**
 * utils/jwt.ts — minimal, dependency-free HS256 JWT verification (Module G3).
 *
 * The FastAPI backend signs tokens with HS256 (python-jose). We verify them here
 * with the Web Crypto API (HMAC-SHA256) — no npm dependency. A token is accepted
 * only if BOTH its signature and its `exp` (expiry) check out.
 *
 * 🚩 The gateway's secret MUST equal the backend's `JWT_SECRET_KEY`; otherwise
 * every signature check (correctly) fails and all tokens are rejected.
 *
 * A JWT is three base64url parts joined by dots:  header.payload.signature
 *   signature = HMAC-SHA256( "header.payload", secret )
 */

/** The claims IDRM puts in a token (see backend core/security.py). */
export interface JwtClaims {
  sub: string; // the user_id
  role?: string; // user role (CITIZEN, ADMIN, …)
  type?: string; // "access" | "refresh"
  exp?: number; // expiry, Unix seconds
  iat?: number; // issued-at, Unix seconds
  [key: string]: unknown;
}

/** Decode a base64url string to raw bytes. */
function base64UrlToBytes(input: string): Uint8Array {
  // base64url → base64: swap -/_ back to +//, then pad to a multiple of 4.
  let b64 = input.replace(/-/g, "+").replace(/_/g, "/");
  b64 += "=".repeat((4 - (b64.length % 4)) % 4);
  const binary = atob(b64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

/** Decode a base64url string to UTF-8 text (used for the header + payload JSON). */
function base64UrlToText(input: string): string {
  return new TextDecoder().decode(base64UrlToBytes(input));
}

/**
 * Verify an HS256 JWT against `secret`.
 *
 * @returns the decoded claims if the signature is valid and the token hasn't expired.
 * @throws  Error if the token is malformed, uses a non-HS256 alg, has a bad
 *          signature, or is expired.
 */
export async function verifyJwtHS256(token: string, secret: string): Promise<JwtClaims> {
  const parts = token.split(".");
  if (parts.length !== 3) throw new Error("Malformed token");
  const [headerB64, payloadB64, signatureB64] = parts;

  // 1. The header must declare HS256 — reject "alg: none" and other algorithms.
  const header = JSON.parse(base64UrlToText(headerB64)) as { alg?: string };
  if (header.alg !== "HS256") throw new Error(`Unsupported JWT alg: ${header.alg}`);

  // 2. Re-verify the HMAC over "header.payload" with the shared secret.
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["verify"],
  );
  const signingInput = new TextEncoder().encode(`${headerB64}.${payloadB64}`);
  const valid = await crypto.subtle.verify("HMAC", key, base64UrlToBytes(signatureB64), signingInput);
  if (!valid) throw new Error("Bad signature");

  // 3. Decode the claims and enforce expiry (with a small clock-skew allowance).
  const claims = JSON.parse(base64UrlToText(payloadB64)) as JwtClaims;
  const now = Math.floor(Date.now() / 1000);
  if (typeof claims.exp === "number" && claims.exp < now - 5) {
    throw new Error("Token expired");
  }
  return claims;
}
