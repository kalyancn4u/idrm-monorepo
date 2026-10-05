# IDRM Complete Monitoring Guide
## Redis Operations, Bun Gateway, Observability, and Scaling

**Version**: 3.0  
**Sources**: `46-REDIS-OPERATIONS-REFERENCE.md` · `51-BUN-API-GATEWAY-GUIDE.md` · HLD §11 Caching · `MIGRATION-TO-MICROSERVICES-v3.md` §7

---

## Table of Contents

1. [Redis Operations Reference](#1-redis-operations-reference)
2. [Bun API Gateway Internals](#2-bun-api-gateway-internals)
3. [Observability Stack](#3-observability-stack)
4. [Key Metrics to Watch](#4-key-metrics-to-watch)
5. [Alerting Rules](#5-alerting-rules)
6. [Scaling Guide](#6-scaling-guide)
7. [Health Check Endpoints](#7-health-check-endpoints)

---

## 1. Redis Operations Reference

### Why Redis vs PostgreSQL

| Use Case | Redis | PostgreSQL | Reason |
|----------|-------|-----------|--------|
| User session tokens | Yes | No | Temporary + fast |
| API response cache | Yes | No | Avoid re-computing |
| Service request records | No | Yes | Permanent data |
| Rate limiting counters | Yes | No | Fast atomic INCR |
| Real-time pub/sub | Yes | No | Built-in feature |
| Audit logs | No | Yes | Permanent + queryable |

**Golden rule**: PostgreSQL for permanent data, Redis for temporary/fast-access data.

### Redis Key Patterns

```
session:{user_id}                  → JWT payload + metadata (7 day TTL)
blacklist:{jti}                    → "1" (access token TTL)
api:cache:{endpoint}:{params_hash} → JSON response body
rate_limit:{endpoint}:{ip}         → Request count integer (60s TTL)
realtime:{service_id}              → Current service status (5 min TTL)
ws:connections:{user_id}           → WebSocket connection ID
```

### Session Management

```python
# src/backend/app-python/core/redis.py
import redis
from core.config import settings

redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

# Store session (login)
def store_session(user_id: str, session_data: dict, ttl_seconds: int = 604800):
    key = f"session:{user_id}"
    redis_client.setex(key, ttl_seconds, json.dumps(session_data))

# Retrieve session
def get_session(user_id: str) -> dict | None:
    data = redis_client.get(f"session:{user_id}")
    return json.loads(data) if data else None

# Blacklist token on logout
def blacklist_token(jti: str, ttl_seconds: int):
    redis_client.setex(f"blacklist:{jti}", ttl_seconds, "1")

# Check if token is blacklisted
def is_blacklisted(jti: str) -> bool:
    return redis_client.exists(f"blacklist:{jti}") == 1
```

### API Response Caching

```python
from functools import wraps
import hashlib, json

def cache_response(ttl_seconds: int = 60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from endpoint + params
            params_hash = hashlib.md5(
                json.dumps(kwargs, sort_keys=True).encode()
            ).hexdigest()
            cache_key = f"api:cache:{func.__name__}:{params_hash}"

            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl_seconds, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage — TTL varies by endpoint sensitivity
@cache_response(ttl_seconds=60)    # Services list: 60s
async def get_services(...): ...

@cache_response(ttl_seconds=300)   # Analytics: 5 min
async def get_dashboard(...): ...

@cache_response(ttl_seconds=3600)  # Static data: 1 hour
async def get_service_types(...): ...
```

### Rate Limiting in Redis

```python
def check_rate_limit(endpoint: str, ip: str, limit: int, window_seconds: int) -> bool:
    key = f"rate_limit:{endpoint}:{ip}"
    count = redis_client.incr(key)
    if count == 1:
        redis_client.expire(key, window_seconds)
    return count <= limit

# Returns False (rate limit exceeded) if over threshold
```

### Real-Time Pub/Sub for WebSockets

```python
# Publisher (backend service update)
def publish_service_update(service_id: str, event_type: str, payload: dict):
    message = json.dumps({"event": event_type, "data": payload})
    redis_client.publish(f"service_updates:{service_id}", message)

# Subscriber (Bun gateway WebSocket handler)
# TypeScript — bun-gateway/src/websocket.ts
const subscriber = redis.createClient();
await subscriber.subscribe(`service_updates:${serviceId}`, (message) => {
    const event = JSON.parse(message);
    ws.send(JSON.stringify(event));
});
```

### Redis CLI Commands for Debugging

```bash
# Monitor all operations in real-time
redis-cli monitor

# Check memory usage
redis-cli info memory | grep used_memory_human

# List all sessions
redis-cli keys "session:*" | head -20

# Check rate limit for an IP
redis-cli get "rate_limit:/api/v1/auth/login:203.0.113.45"

# Check a specific cache entry
redis-cli get "api:cache:get_services:abc123"

# Flush cache only (keep sessions/blacklist)
redis-cli --scan --pattern "api:cache:*" | xargs redis-cli del

# Check pub/sub subscribers
redis-cli pubsub channels
```

---

## 2. Bun API Gateway Internals

### Why Bun as Gateway

Traditional approach: NGINX → FastAPI directly (no rate limiting, no auth pre-check, no WebSocket coordination)

v3 approach:
```
NGINX (SSL/load balancing)
  ↓
Bun Gateway (port 3000)
  ├─ Rate limiting (Redis INCR)
  ├─ JWT pre-validation
  ├─ Security headers (CSP, X-Frame-Options, HSTS)
  ├─ CORS for all three frontends
  ├─ WebSocket server (port 3001)
  └─ Proxy to FastAPI (port 8000)
```

**Bun advantages**: 3–4× faster than Node.js, built-in TypeScript, built-in WebSocket support, ~30% less memory.

### Middleware Chain

```typescript
// bun-gateway/src/index.ts
import { serve } from "bun";

serve({
  port: 3000,
  async fetch(req) {
    // 1. Logger
    await loggerMiddleware(req);

    // 2. CORS (handles OPTIONS preflight)
    const corsRes = corsMiddleware(req);
    if (corsRes) return corsRes;

    // 3. Rate limiting (Redis)
    const rateLimitRes = await rateLimitMiddleware(req);
    if (rateLimitRes) return rateLimitRes;

    // 4. JWT pre-validation (optional — backend validates fully)
    const authRes = authMiddleware(req);
    if (authRes) return authRes;

    // 5. Security headers applied to all responses
    const response = await apiProxy(req);
    return addSecurityHeaders(response);
  },
});
```

### CORS Configuration

```typescript
// bun-gateway/src/middleware/cors.ts
const ALLOWED_ORIGINS = [
    process.env.FRONTEND_HTML_URL,   // http://localhost:5173
    process.env.FRONTEND_SPA_URL,    // http://localhost:5174
    process.env.FRONTEND_MOBILE_URL, // exp://192.168.1.100:19000
];

export function corsMiddleware(req: Request): Response | null {
    const origin = req.headers.get("Origin");
    if (!origin || !ALLOWED_ORIGINS.includes(origin)) {
        return new Response("Forbidden", { status: 403 });
    }
    if (req.method === "OPTIONS") {
        return new Response(null, {
            status: 204,
            headers: {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Authorization, Content-Type",
                "Access-Control-Max-Age": "86400",
            },
        });
    }
    return null; // Continue middleware chain
}
```

### Security Headers

```typescript
function addSecurityHeaders(response: Response): Response {
    const headers = new Headers(response.headers);
    headers.set("X-Content-Type-Options", "nosniff");
    headers.set("X-Frame-Options", "DENY");
    headers.set("X-XSS-Protection", "1; mode=block");
    headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains");
    headers.set("Content-Security-Policy",
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'");
    return new Response(response.body, {
        status: response.status,
        headers,
    });
}
```

---

## 3. Observability Stack

Production monitoring runs on the same server (or a dedicated monitoring node).

### Components

| Tool | Port | Purpose |
|------|------|---------|
| Prometheus | 9090 | Metrics collection and storage |
| Grafana | 3001 | Dashboards and visualization |
| Loki | 3100 | Log aggregation |
| Promtail | — | Log shipping to Loki |
| Node Exporter | 9100 | Host metrics (CPU, memory, disk) |

### Docker Compose (Monitoring Stack)

```yaml
# monitoring/docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus

  grafana:
    image: grafana/grafana:latest
    ports: ["3001:3000"]
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards

  loki:
    image: grafana/loki:latest
    ports: ["3100:3100"]

  node-exporter:
    image: prom/node-exporter:latest
    ports: ["9100:9100"]
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
```

### Prometheus Scrape Config

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "idrm-backend"
    static_configs:
      - targets: ["backend:8000"]

  - job_name: "idrm-bun-gateway"
    static_configs:
      - targets: ["api-gateway:3000"]

  - job_name: "node"
    static_configs:
      - targets: ["node-exporter:9100"]

  - job_name: "postgres"
    static_configs:
      - targets: ["postgres-exporter:9187"]

  - job_name: "redis"
    static_configs:
      - targets: ["redis-exporter:9121"]
```

### FastAPI Metrics Endpoint

```python
# src/backend/app-python/main.py — expose Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

---

## 4. Key Metrics to Watch

### Application Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| API response time (p95) | < 200ms | 200-500ms | > 500ms |
| Error rate (5xx) | < 0.1% | 0.1-1% | > 1% |
| Active WebSocket connections | < 10,000 | 10k-50k | > 50k |
| Service request creation rate | Normal | 5× normal | 10× normal |
| Auth failure rate | < 1% | 1-5% | > 5% (possible attack) |

### Infrastructure Metrics

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| CPU usage | < 60% | 60-80% | > 80% |
| Memory usage | < 70% | 70-85% | > 85% |
| Disk I/O wait | < 10% | 10-20% | > 20% |
| PostgreSQL connections | < 80% max | 80-90% | > 90% |
| Redis memory | < 70% max | 70-85% | > 85% |

### Business Metrics (Grafana Dashboard)

```
- Total active service requests
- Average response time (DM to provider assignment)
- Provider coverage map (% of requests within 10km of a provider)
- Request fulfillment rate (last 24h)
- Critical requests pending > 30 minutes
```

---

## 5. Alerting Rules

```yaml
# monitoring/alert-rules.yml
groups:
  - name: idrm-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 2m
        annotations:
          summary: "Error rate above 1%"

      - alert: SlowAPIResponse
        expr: histogram_quantile(0.95, http_request_duration_seconds_bucket) > 0.5
        for: 5m
        annotations:
          summary: "95th percentile response time > 500ms"

      - alert: CriticalRequestsStuck
        expr: service_requests_by_status{status="SUBMITTED",priority="CRITICAL"} > 0
        for: 30m
        annotations:
          summary: "Critical requests unassigned for 30+ minutes"

      - alert: HighMemoryUsage
        expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.15
        for: 5m
        annotations:
          summary: "Less than 15% memory available"

      - alert: DatabaseConnectionsHigh
        expr: pg_stat_database_numbackends / pg_settings_max_connections > 0.85
        for: 2m
        annotations:
          summary: "PostgreSQL connections > 85% of max"
```

---

## 6. Scaling Guide

### Current: Modular Monolith (v3)

Single FastAPI process serves all endpoints. Scale by:
1. Adding vCPUs / RAM to the server (vertical scaling)
2. Running multiple uvicorn workers: `uvicorn app.main:app --workers 4`
3. Adding a second server behind the load balancer

### Future: Module Extraction (when needed)

If a single module hits resource limits, it can be extracted into a standalone service without changing the API surface (URL versioning maintained).

**Extraction order** (by likely need):
1. Geospatial service — heaviest compute, most isolated
2. Notifications service — async/background, independently scalable
3. Analytics service — heavy read, can use read replica

**Infrastructure requirements** to support extraction:
- Redis already in place (pub/sub ready)
- JWT already stateless (services can validate independently)
- Database already modular (schemas per domain)

See `archive/MIGRATION-TO-MICROSERVICES-v3.md` §7 for the full extraction runbook.

---

## 7. Health Check Endpoints

| Endpoint | Port | Returns |
|----------|------|---------|
| `GET /health` | 8000 | `{"status":"healthy","db":"connected","redis":"connected"}` |
| `GET /health` | 3000 | `{"status":"ok","gateway":"running","backend_reachable":true}` |
| `GET /metrics` | 8000 | Prometheus text format |
| `GET /api/v1/admin/system-health` | 3000 | Full system health (ADMIN only) |

### Automated Health Check Script

```bash
#!/bin/bash
# Production health check — run via cron every 5 minutes

BACKEND_HEALTH=$(curl -s http://localhost:8000/health | jq -r .status)
GATEWAY_HEALTH=$(curl -s http://localhost:3000/health | jq -r .status)
REDIS_PING=$(redis-cli ping 2>/dev/null)
PG_STATUS=$(pg_isready -U idrm_user -d idrm_db 2>/dev/null && echo "OK" || echo "FAIL")

if [ "$BACKEND_HEALTH" != "healthy" ] || [ "$REDIS_PING" != "PONG" ] || [ "$PG_STATUS" != "OK" ]; then
    # Send alert (Slack, PagerDuty, etc.)
    curl -X POST "$SLACK_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{\"text\": \"IDRM Health Check FAILED: backend=$BACKEND_HEALTH redis=$REDIS_PING db=$PG_STATUS\"}"
fi
```

---

**Full source documents**:
- Redis reference: `docs/IDRM-Redis-Operations.md`
- Bun gateway guide: `docs/IDRM-Bun-Gateway-Guide.md`
- Scaling to microservices: `archive/MIGRATION-TO-MICROSERVICES-v3.md`
- Production monitoring setup: `docs/IDRM-DEPLOYMENT-GUIDE.md` Production section
