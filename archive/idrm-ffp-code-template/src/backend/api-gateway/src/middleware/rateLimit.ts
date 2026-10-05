/**
 * middleware/rateLimit.ts — per-IP, per-endpoint rate limiting (Module G2).
 *
 * Fixed-window counters: each (path-class, client-IP) pair gets N requests per
 * window; exceeding it returns 429. The strict auth endpoints additionally "block"
 * the IP for a cooldown after they're exceeded. Limits mirror the Bun Gateway Guide
 * §Rate Limiting and the API specs rate-limit table.
 *
 * Storage is pluggable (`RateLimitStore`):
 *   • InMemoryStore (default) — correct for the single-instance MVP; zero deps and
 *     runnable/verifiable with no external services.
 *   • RedisStore (used when REDIS_URL is set) — shares counters across gateway
 *     instances for horizontal scaling, via Bun's native RedisClient. It FAILS OPEN
 *     (a Redis error allows the request) so a cache outage never locks users out.
 *
 * Client IP comes from `X-Forwarded-For` / `X-Real-IP` (set by NGINX in prod); a
 * direct connection with neither falls back to "unknown" (one shared bucket).
 */
import { RedisClient } from "bun";

import { config } from "../config";

/** A rate-limit rule: `points` requests per `duration` seconds, with an optional
 *  post-breach `blockDuration` cooldown (0 = no extra block). */
export interface RateLimitConfig {
  points: number;
  duration: number;
  blockDuration: number;
}

/** Pick the limit for a path (most specific first), mirroring the API specs table. */
export function getRateLimitConfig(path: string): RateLimitConfig {
  if (path.startsWith("/api/v1/auth/login")) return { points: 5, duration: 900, blockDuration: 1800 };
  if (path.startsWith("/api/v1/auth/register")) return { points: 3, duration: 3600, blockDuration: 7200 };
  if (path.startsWith("/api/v1/auth/")) return { points: 10, duration: 900, blockDuration: 1800 };
  if (path.startsWith("/api/v1/")) return { points: 60, duration: 60, blockDuration: 300 };
  return { points: 1000, duration: 60, blockDuration: 0 }; // static / everything else
}

interface HitResult {
  count: number; // requests so far in the current window
  ttl: number; // seconds remaining in the window
}

/** Storage backend for the counters + block flags. */
interface RateLimitStore {
  /** Increment the window counter for `key` (starting the window on the first hit). */
  hit(key: string, windowSeconds: number): Promise<HitResult>;
  /** Seconds remaining on a block for `key`, or 0 if not blocked. */
  getBlockTtl(key: string): Promise<number>;
  /** Block `key` for `seconds`. */
  setBlock(key: string, seconds: number): Promise<void>;
}

/** In-process fixed-window store. Correct for a single gateway instance (MVP). */
class InMemoryStore implements RateLimitStore {
  private counters = new Map<string, { count: number; expiresAt: number }>();
  private blocks = new Map<string, number>(); // key → epoch-ms when the block ends

  async hit(key: string, windowSeconds: number): Promise<HitResult> {
    const now = Date.now();
    const entry = this.counters.get(key);
    if (!entry || entry.expiresAt <= now) {
      this.counters.set(key, { count: 1, expiresAt: now + windowSeconds * 1000 });
      return { count: 1, ttl: windowSeconds };
    }
    entry.count += 1;
    return { count: entry.count, ttl: Math.ceil((entry.expiresAt - now) / 1000) };
  }

  async getBlockTtl(key: string): Promise<number> {
    const until = this.blocks.get(key);
    if (until === undefined) return 0;
    const remaining = Math.ceil((until - Date.now()) / 1000);
    if (remaining <= 0) {
      this.blocks.delete(key);
      return 0;
    }
    return remaining;
  }

  async setBlock(key: string, seconds: number): Promise<void> {
    this.blocks.set(key, Date.now() + seconds * 1000);
  }
}

/** Redis-backed store (shared across instances). Uses raw commands via `send` and
 *  fails open so a Redis outage never blocks legitimate traffic. */
class RedisStore implements RateLimitStore {
  private client: RedisClient;

  constructor(url: string) {
    this.client = new RedisClient(url);
  }

  async hit(key: string, windowSeconds: number): Promise<HitResult> {
    try {
      const count = Number(await this.client.send("INCR", [key]));
      if (count === 1) await this.client.send("EXPIRE", [key, String(windowSeconds)]);
      const ttl = Number(await this.client.send("TTL", [key]));
      return { count, ttl: ttl > 0 ? ttl : windowSeconds };
    } catch (err) {
      console.warn("Rate limiter: Redis hit() failed — failing open:", err);
      return { count: 1, ttl: windowSeconds }; // allow the request
    }
  }

  async getBlockTtl(key: string): Promise<number> {
    try {
      const ttl = Number(await this.client.send("TTL", [key]));
      return ttl > 0 ? ttl : 0;
    } catch {
      return 0;
    }
  }

  async setBlock(key: string, seconds: number): Promise<void> {
    try {
      await this.client.send("SETEX", [key, String(seconds), "1"]);
    } catch (err) {
      console.warn("Rate limiter: Redis setBlock() failed:", err);
    }
  }
}

const store: RateLimitStore = config.redisUrl ? new RedisStore(config.redisUrl) : new InMemoryStore();

/** Best-guess client IP, trusting the proxy headers NGINX sets in production. */
function clientIp(req: Request): string {
  return (
    req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    req.headers.get("x-real-ip") ||
    "unknown"
  );
}

/** Build a 429 Too Many Requests response with the standard rate-limit headers. */
function tooManyRequests(limit: number, retryAfter: number, message: string): Response {
  return Response.json(
    { detail: message, code: "RATE_LIMITED", retry_after: retryAfter },
    {
      status: 429,
      headers: {
        "X-RateLimit-Limit": String(limit),
        "X-RateLimit-Remaining": "0",
        "Retry-After": String(retryAfter),
      },
    },
  );
}

/**
 * Check the rate limit for a request.
 *
 * @returns `limited` — a 429 Response if the caller is over the limit (the caller
 *          should return it), else null; and `headers` — `X-RateLimit-*` headers to
 *          attach to an allowed response.
 */
export async function checkRateLimit(
  req: Request,
): Promise<{ limited: Response | null; headers: Record<string, string> }> {
  const path = new URL(req.url).pathname;
  const cfg = getRateLimitConfig(path);
  const ip = clientIp(req);
  const key = `ratelimit:${path}:${ip}`;
  const blockKey = `ratelimit:block:${path}:${ip}`;

  // Already serving a cooldown from an earlier breach?
  const blockTtl = await store.getBlockTtl(blockKey);
  if (blockTtl > 0) {
    return { limited: tooManyRequests(cfg.points, blockTtl, "Temporarily blocked — too many requests"), headers: {} };
  }

  const { count, ttl } = await store.hit(key, cfg.duration);
  if (count > cfg.points) {
    if (cfg.blockDuration > 0) await store.setBlock(blockKey, cfg.blockDuration);
    const retryAfter = cfg.blockDuration > 0 ? cfg.blockDuration : ttl;
    return { limited: tooManyRequests(cfg.points, retryAfter, "Rate limit exceeded"), headers: {} };
  }

  return {
    limited: null,
    headers: {
      "X-RateLimit-Limit": String(cfg.points),
      "X-RateLimit-Remaining": String(Math.max(0, cfg.points - count)),
    },
  };
}
