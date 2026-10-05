# IDRM Bun API Gateway Guide

## Rate Limiting · Authentication · Static Files · Security Headers

**Version**: 1.0
**Source**: `backup/51-BUN-API-GATEWAY-GUIDE.md`
**Location**: `src/backend/api-gateway/`
**Ports**: HTTP 3000 · WebSocket 3001
**Last Updated**: May 30, 2026

---

## Why Bun as the API Gateway?

The API gateway sits between NGINX and the Python FastAPI backend. It handles all the cross-cutting concerns so FastAPI only has to deal with business logic.

| Concern                            | Who handles it                               |
| ---------------------------------- | -------------------------------------------- |
| SSL termination                    | NGINX                                        |
| Rate limiting (per IP/endpoint)    | **Bun gateway**                        |
| JWT verification                   | **Bun gateway**                        |
| CORS headers                       | **Bun gateway**                        |
| Security headers (CSP, HSTS, etc.) | **Bun gateway**                        |
| Static file serving (dev)          | **Bun gateway** (Vite in dev)          |
| WebSocket upgrade                  | **Bun gateway**                        |
| Business logic                     | FastAPI (port 8000)                          |
| Geo queries                        | Python geo module inside FastAPI (port 8000) |

**Why Bun instead of Node.js?**

- ~3× faster throughput (~40 000 req/s vs ~12 000)
- Native TypeScript — no transpilation step
- Built-in bundler and test runner
- Drop-in compatible with Node.js packages

---

## Architecture

```
Browser / Mobile App
        │
        │ HTTPS (443)
        ↓
   NGINX (Port 80/443)
   SSL termination
   Load balancing
        │
        │ HTTP (internal)
        ↓
┌────────────────────────────────────────┐
│  Bun API Gateway  (Port 3000 / 3001)  │
│                                        │
│  1. Rate limit check  (Redis)         │
│     → 429 if exceeded                 │
│  2. JWT verification                  │
│     → 401 if invalid/missing          │
│  3. Security headers added            │
│  4. Route decision:                   │
│     /api/v1/*  → proxy to FastAPI     │
│     /ws        → WebSocket upgrade    │
│     /*         → static files        │
└────────────────────────────────────────┘
        │
        ↓
   FastAPI Backend (Port 8000)
   Business logic only
```

### Request flow by type

**Static files** (`GET /index.html`, etc.)

```
Rate limit: 1 000/min (lenient)
Auth:       Not required
Action:     Serve from disk with cache headers
```

**Public API** (`POST /api/v1/auth/login`)

```
Rate limit: 5/15 min (strict)
Auth:       Not required
Action:     Proxy to FastAPI port 8000
```

**Protected API** (`GET /api/v1/services`)

```
Rate limit: 60/min (authenticated)
Auth:       Verify JWT signature + expiry + Redis session
Action:     Add X-User-ID header → proxy to FastAPI
```

---

## Project Structure

```
src/backend/api-gateway/
├── src/
│   ├── index.ts                # Entry point — Bun.serve() setup
│   ├── middleware/
│   │   ├── rateLimit.ts        # Redis-backed rate limiter
│   │   ├── auth.ts             # JWT verification
│   │   ├── security.ts         # Security headers
│   │   └── cors.ts             # CORS configuration
│   ├── routes/
│   │   ├── api.ts              # Proxy to FastAPI
│   │   ├── static.ts           # Static file serving
│   │   └── websocket.ts        # WebSocket handler
│   └── utils/
│       ├── jwt.ts              # JWT helpers
│       └── redis.ts            # Redis client singleton
├── package.json
├── tsconfig.json
└── .env
```

---

## Rate Limiting

**File**: `src/middleware/rateLimit.ts`

Rate limits are stored in Redis with automatic TTL expiry. The key pattern is `rate_limit:{path}:{client_ip}`.

```typescript
import { Redis } from 'ioredis';

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
});

interface RateLimitConfig {
  points:        number;  // Max requests allowed
  duration:      number;  // Window in seconds
  blockDuration: number;  // Seconds to block after exceeding (0 = no block)
}

function getRateLimitConfig(path: string): RateLimitConfig {
  if (path.startsWith('/api/v1/auth/login'))     return { points: 5,    duration: 900,  blockDuration: 1800 };
  if (path.startsWith('/api/v1/auth/register'))  return { points: 3,    duration: 3600, blockDuration: 7200 };
  if (path.startsWith('/api/v1/auth/'))          return { points: 10,   duration: 900,  blockDuration: 1800 };
  if (path.startsWith('/api/v1/analytics/export')) return { points: 10, duration: 3600, blockDuration: 0   };
  if (path.startsWith('/api/v1/'))               return { points: 60,   duration: 60,   blockDuration: 300  };
  return { points: 1000, duration: 60, blockDuration: 0 };   // static files
}

export async function rateLimitMiddleware(req: Request): Promise<Response | null> {
  const path     = new URL(req.url).pathname;
  const config   = getRateLimitConfig(path);
  const clientIP = req.headers.get('x-forwarded-for')?.split(',')[0]
                || req.headers.get('x-real-ip')
                || 'unknown';

  const key      = `ratelimit:${path}:${clientIP}`;
  const blockKey = `ratelimit:block:${path}:${clientIP}`;

  // Check if currently blocked
  const blocked = await redis.get(blockKey);
  if (blocked) {
    return new Response(JSON.stringify({ error: 'Too many requests', retryAfter: parseInt(blocked) }), {
      status: 429,
      headers: { 'Content-Type': 'application/json', 'Retry-After': blocked },
    });
  }

  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, config.duration);
  const ttl = await redis.ttl(key);

  if (count > config.points) {
    if (config.blockDuration > 0) {
      await redis.setex(blockKey, config.blockDuration, String(config.blockDuration));
    }
    return new Response(JSON.stringify({
      error: 'Rate limit exceeded',
      message: `Limit: ${config.points} per ${config.duration}s`,
      retryAfter: ttl,
    }), {
      status: 429,
      headers: {
        'Content-Type': 'application/json',
        'X-RateLimit-Limit': String(config.points),
        'X-RateLimit-Remaining': '0',
        'Retry-After': String(ttl),
      },
    });
  }

  // Attach rate-limit info for the response headers (added downstream)
  (req as any).rateLimitRemaining = config.points - count;
  return null;  // Allow request
}
```

---

## JWT Authentication Middleware

**File**: `src/middleware/auth.ts`

```typescript
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET!;

// Endpoints that do NOT require a token
const PUBLIC_PATHS = [
  '/api/v1/auth/login',
  '/api/v1/auth/register',
  '/api/v1/auth/verify-email',
  '/api/v1/auth/forgot-password',
  '/api/v1/auth/reset-password',
  '/api/v1/health',
];

function isPublic(path: string): boolean {
  return PUBLIC_PATHS.some(p => path.startsWith(p)) || !path.startsWith('/api/');
}

function extractToken(req: Request): string | null {
  // Try Authorization: Bearer <token>
  const header = req.headers.get('Authorization');
  if (header?.startsWith('Bearer ')) return header.slice(7);

  // Try httpOnly cookie (for web browsers)
  const cookies = Object.fromEntries(
    (req.headers.get('Cookie') || '').split(';').map(c => {
      const [k, ...v] = c.trim().split('=');
      return [k, v.join('=')];
    })
  );
  return cookies.access_token ?? null;
}

export async function authMiddleware(req: Request): Promise<Response | null> {
  const path = new URL(req.url).pathname;
  if (isPublic(path)) return null;   // Skip auth check

  const token = extractToken(req);
  if (!token) {
    return new Response(JSON.stringify({ error: 'Unauthorized', message: 'No token provided' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json', 'WWW-Authenticate': 'Bearer realm="IDRM API"' },
    });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET, { algorithms: ['HS256'] }) as {
      user_id: string; email: string; role: string; jti: string; exp: number;
    };

    // Check Redis blacklist (covers logged-out tokens still within expiry window)
    const blacklisted = await redis.exists(`blacklist:${payload.jti}`);
    if (blacklisted) {
      return new Response(JSON.stringify({ error: 'Unauthorized', message: 'Token revoked' }), {
        status: 401, headers: { 'Content-Type': 'application/json' },
      });
    }

    // Attach user context for FastAPI to read
    (req as any).user = payload;
    return null;   // Allow request

  } catch (err) {
    const message = err instanceof jwt.TokenExpiredError ? 'Token expired' : 'Invalid token';
    return new Response(JSON.stringify({ error: 'Unauthorized', message }), {
      status: 401, headers: { 'Content-Type': 'application/json' },
    });
  }
}
```

---

## Security Headers

**File**: `src/middleware/security.ts`

Added to every response — static files and API proxied responses alike.

```typescript
export function addSecurityHeaders(response: Response): Response {
  const headers = new Headers(response.headers);

  headers.set('X-Content-Type-Options',  'nosniff');
  headers.set('X-Frame-Options',          'DENY');
  headers.set('X-XSS-Protection',         '1; mode=block');
  headers.set('Referrer-Policy',           'strict-origin-when-cross-origin');
  headers.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  headers.set('Content-Security-Policy', [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' cdn.jsdelivr.net",   // Tailwind, Leaflet, Axios from CDN
    "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net unpkg.com",
    "img-src 'self' data: tile.openstreetmap.org",           // OSM map tiles
    "connect-src 'self' ws://localhost:3001 wss://api.idrm.gov.in",
    "font-src 'self'",
    "frame-ancestors 'none'",
  ].join('; '));

  return new Response(response.body, {
    status: response.status,
    headers,
  });
}
```

---

## API Proxy to FastAPI

**File**: `src/routes/api.ts`

```typescript
const FASTAPI_BASE = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function proxyToFastAPI(req: Request): Promise<Response> {
  const url     = new URL(req.url);
  const target  = `${FASTAPI_BASE}${url.pathname}${url.search}`;

  // Forward request, adding user context headers from JWT payload
  const user = (req as any).user;
  const proxyHeaders = new Headers(req.headers);
  if (user) {
    proxyHeaders.set('X-User-ID',   user.user_id);
    proxyHeaders.set('X-User-Role', user.role);
    proxyHeaders.set('X-User-Email', user.email);
  }
  // Remove raw Authorization header (FastAPI trusts X-User-* instead)
  proxyHeaders.delete('Authorization');

  const proxyReq = new Request(target, {
    method:  req.method,
    headers: proxyHeaders,
    body:    req.method !== 'GET' && req.method !== 'HEAD' ? req.body : undefined,
  });

  try {
    return await fetch(proxyReq);
  } catch (err) {
    console.error('FastAPI proxy error:', err);
    return new Response(JSON.stringify({ error: 'Service unavailable' }), {
      status: 503, headers: { 'Content-Type': 'application/json' },
    });
  }
}
```

---

## WebSocket Handler

**File**: `src/routes/websocket.ts`

```typescript
import { Redis } from 'ioredis';

const subscriber = new Redis({ host: process.env.REDIS_HOST || 'localhost' });

// Map of channel → Set of connected WebSocket clients
const clients: Map<string, Set<ServerWebSocket<unknown>>> = new Map();

export function handleWebSocket(ws: ServerWebSocket<unknown>, channel: string): void {
  if (!clients.has(channel)) clients.set(channel, new Set());
  clients.get(channel)!.add(ws);

  ws.subscribe(channel);

  ws.data = { channel };
  ws.addEventListener('close', () => {
    clients.get(channel)?.delete(ws);
  });
}

// Redis subscriber → broadcast to all WebSocket clients on a channel
subscriber.subscribe('pubsub:service_requests', (err) => {
  if (err) console.error('Redis subscribe error:', err);
});

subscriber.on('message', (redisChannel, message) => {
  const wsChannel = 'service_requests';
  const channelClients = clients.get(wsChannel);
  if (!channelClients) return;

  for (const client of channelClients) {
    try {
      client.send(message);
    } catch {
      channelClients.delete(client);
    }
  }
});
```

---

## Main Entry Point

**File**: `src/index.ts`

```typescript
import { rateLimitMiddleware } from './middleware/rateLimit';
import { authMiddleware }      from './middleware/auth';
import { addSecurityHeaders }  from './middleware/security';
import { proxyToFastAPI }      from './routes/api';
import { handleWebSocket }     from './routes/websocket';

Bun.serve({
  port: parseInt(process.env.PORT || '3000'),

  async fetch(req, server) {
    const url  = new URL(req.url);
    const path = url.pathname;

    // WebSocket upgrade
    if (path === '/ws' && req.headers.get('Upgrade') === 'websocket') {
      const upgraded = server.upgrade(req, { data: { channel: 'service_requests' } });
      if (!upgraded) return new Response('WebSocket upgrade failed', { status: 400 });
      return;
    }

    // Middleware chain: rate limit → auth → route
    const rateLimitResponse = await rateLimitMiddleware(req);
    if (rateLimitResponse) return addSecurityHeaders(rateLimitResponse);

    const authResponse = await authMiddleware(req);
    if (authResponse) return addSecurityHeaders(authResponse);

    // Route
    let response: Response;
    if (path.startsWith('/api/')) {
      response = await proxyToFastAPI(req);
    } else {
      // Static files (Vite handles this in dev; NGINX in prod)
      response = new Response('Not found', { status: 404 });
    }

    return addSecurityHeaders(response);
  },

  websocket: {
    open(ws) {
      handleWebSocket(ws, 'service_requests');
    },
    message(ws, msg) {
      // Client sends { type: 'subscribe', channel: 'service_requests' }
      // Already subscribed at open; no-op for now
    },
    close(ws) {
      // Cleanup handled inside handleWebSocket close listener
    },
  },
});

console.log(`Bun API Gateway running on port ${process.env.PORT || 3000}`);
```

---

## CORS Configuration

**File**: `src/middleware/cors.ts`

```typescript
const ALLOWED_ORIGINS = (process.env.CORS_ORIGINS || 'http://localhost:5173,http://localhost:5174').split(',');

export function corsHeaders(origin: string | null): Record<string, string> {
  const allowed = origin && ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    'Access-Control-Allow-Origin':      allowed,
    'Access-Control-Allow-Methods':     'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers':     'Authorization, Content-Type, Accept',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Max-Age':           '86400',
  };
}
```

---

## Development Setup

```bash
# Install dependencies
cd src/backend/api-gateway
bun install

# Environment variables
cp .env.example .env
# Edit .env:
#   PORT=3000
#   FASTAPI_URL=http://localhost:8000
#   REDIS_HOST=localhost
#   REDIS_PORT=6379
#   JWT_SECRET=<same secret as FastAPI>
#   CORS_ORIGINS=http://localhost:5173,http://localhost:5174

# Start gateway
bun run dev     # hot-reload
bun run start   # production

# Test rate limiting
curl -X POST http://localhost:3000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"x@x.com","password":"wrong"}' \
     -w "\nHTTP %{http_code}\n"
# Run 6+ times — 6th attempt returns HTTP 429
```

---

## Production Deployment

In production, Bun runs inside a Docker container. NGINX terminates TLS and forwards to Bun on port 3000. Static files are served by NGINX directly (not Bun) for maximum throughput.

```nginx
# nginx.conf — upstream Bun gateway
upstream bun_gateway {
    server 127.0.0.1:3000;
    keepalive 32;
}

server {
    listen 443 ssl http2;
    server_name api.idrm.gov.in;

    # Static files served directly by NGINX
    location ~* \.(html|css|js|png|jpg|ico|woff2)$ {
        root /var/www/idrm/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API + WebSocket → Bun
    location / {
        proxy_pass         http://bun_gateway;
        proxy_http_version 1.1;
        proxy_set_header   Upgrade     $http_upgrade;
        proxy_set_header   Connection  "upgrade";
        proxy_set_header   X-Real-IP   $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

**See also**:

- #TODO: `backup/51-BUN-API-GATEWAY-GUIDE.md` — Complete guide with all middleware and deployment config
- `docs/IDRM-Redis-Operations.md` — Redis patterns used by the rate limiter
- `start-here/COMPLETE-API-SPECS-GUIDE.md` — Rate limits per endpoint (Section 3 table)
