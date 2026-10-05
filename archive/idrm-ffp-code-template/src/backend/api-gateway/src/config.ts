/**
 * config.ts — gateway configuration, read once from the environment.
 *
 * Every field has a sensible development default, so `bun run dev` works with no
 * `.env` file. In staging/production these come from real environment variables
 * (see `.env.example`).
 */
export const config = {
  /** HTTP port the gateway listens on. */
  port: parseInt(process.env.PORT || "3000", 10),

  /** WebSocket port (a separate server from the HTTP one) — `ws://localhost:3001` (G4). */
  wsPort: parseInt(process.env.WEBSOCKET_PORT || "3001", 10),

  /** Base URL of the FastAPI backend that `/api/*` requests are proxied to. */
  fastApiUrl: process.env.FASTAPI_URL || "http://localhost:8000",

  /** Browser origins permitted by CORS (the first entry is the fallback). */
  corsOrigins: (process.env.CORS_ORIGINS ||
    "http://localhost:5173,http://localhost:5174,exp://127.0.0.1:19000")
    .split(",")
    .map((o) => o.trim())
    .filter(Boolean),

  /**
   * Redis URL for SHARED rate-limit counters (G2) and pub/sub (G4). When empty,
   * the rate limiter uses an in-process store — correct for the single-instance
   * MVP; set this only when running multiple gateway replicas.
   */
  redisUrl: process.env.REDIS_URL || "",

  /**
   * Secret used to verify JWT signatures (G3). 🚩 MUST be byte-for-byte identical
   * to the backend's `JWT_SECRET_KEY`, or every token fails verification. The dev
   * default matches the committed `.env`; override it in staging/production.
   */
  jwtSecret: process.env.JWT_SECRET || "dev-only-secret-change-in-production-min-32-chars",
} as const;
