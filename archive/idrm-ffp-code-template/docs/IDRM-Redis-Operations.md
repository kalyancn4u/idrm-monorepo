# IDRM Redis Operations Reference
## Caching, Sessions, Rate Limiting & Pub/Sub

**Version**: 3.0  
**Source**: `backup/46-REDIS-OPERATIONS-REFERENCE.md`  
**Stack**: Redis 7.2+ · Python `redis-py` library  
**Last Updated**: May 30, 2026

---

## Overview — How IDRM Uses Redis

Redis sits alongside PostgreSQL as a fast in-memory store. Every request that can be served from Redis saves a round-trip to PostgreSQL (~50 ms → ~5 ms).

```
Request → API Gateway → Check Redis
                              ↓
                        HIT?  → Return immediately (5 ms)
                        MISS? → Query PostgreSQL (50 ms)
                                   → Store result in Redis
                                   → Return to caller
```

### Redis Key Patterns

| Key pattern | Type | TTL | Purpose |
|-------------|------|-----|---------|
| `session:{jti}` | Hash | 900 s | Active JWT session data |
| `blacklist:{jti}` | String | Access TTL | Revoked token (logout) |
| `ratelimit:{ip}:{endpoint}` | String | 60 s | Request count per IP |
| `cache:nearby:{lat}:{lng}:{r}` | String (JSON) | 300 s | Geo query results |
| `cache:dashboard:{org_id}` | String (JSON) | 300 s | Analytics summary |
| `pubsub:service_requests` | Pub/Sub | — | WebSocket fan-out |
| `lock:service:{id}` | String | 30 s | Accept-race-condition guard |

### Golden rules

1. **Always set TTL on cached data** — Redis is memory-limited; stale entries must expire automatically.
2. **Keep values small** — cache summaries, not raw database dumps.
3. **Use consistent key naming** — `object:id:attribute` pattern throughout.
4. **Handle cache misses gracefully** — always have a fallback to PostgreSQL.
5. **Use pipelines** for batches of commands.

---

## Part 1 — String Operations

Strings are used for simple scalar values, counters, and JSON blobs.

### SET / SETEX — Store data

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Plain store — no expiry (only for permanent config values)
r.set('config:max_radius_km', '50')

# Store with expiry — ALWAYS use this for caches
r.setex('cache:nearby:17.38:78.48:10', 300, json.dumps(results))

# Store session (15 min)
r.setex(f'session:{jti}', 900, user_id)
```

### GET — Retrieve data

```python
# Returns None on miss — always check!
cached = r.get('cache:nearby:17.38:78.48:10')
if cached:
    return json.loads(cached)   # Cache HIT
# else: fall through to PostgreSQL
```

### INCR — Atomic counter (rate limiting)

```python
key = f'ratelimit:{ip}:/api/v1/auth/login'
count = r.incr(key)
if count == 1:
    r.expire(key, 60)   # Start the window on first hit
if count > 5:
    raise RateLimitError()
```

### EXISTS / DEL

```python
r.exists(f'session:{jti}')   # 1 = exists, 0 = not found
r.delete(f'session:{jti}')   # Invalidate on logout
```

---

## Part 2 — Hash Operations (objects)

Hashes store structured data without serialising to JSON — individual fields can be updated without fetching the whole object.

```python
# Store session data
r.hset(f'session:{jti}', mapping={
    'user_id': user_id,
    'role': 'CITIZEN',
    'login_time': '2026-05-16T10:00:00Z',
    'ip': '203.0.113.1'
})
r.expire(f'session:{jti}', 900)

# Read a single field
role = r.hget(f'session:{jti}', 'role')   # 'CITIZEN'

# Read all fields
session = r.hgetall(f'session:{jti}')
# {'user_id': '...', 'role': 'CITIZEN', 'login_time': '...', 'ip': '...'}

# Update last-activity without touching other fields
r.hset(f'session:{jti}', 'last_activity', datetime.now().isoformat())
r.expire(f'session:{jti}', 900)   # Slide the window
```

---

## Part 3 — Set Operations (unique collections)

Sets track membership. IDRM uses them for active-user tracking and blacklisting.

```python
# Mark user as online
r.sadd('active_users', user_id)
r.expire('active_users', 3600)

# Check if online
r.sismember('active_users', user_id)   # True / False

# Count online users
r.scard('active_users')

# Mark user offline
r.srem('active_users', user_id)
```

---

## Part 4 — Sorted Set Operations (rankings & queues)

Sorted sets associate a float score with each member. IDRM uses them for the service priority queue and sliding-window rate limiting.

```python
# Service priority queue — higher priority = higher score
PRIORITY_SCORE = {'CRITICAL': 1000, 'HIGH': 500, 'MEDIUM': 100, 'LOW': 10}

def enqueue_service(service_id, priority):
    score = PRIORITY_SCORE[priority] + time.time()   # tie-break by time
    r.zadd('service_priority_queue', {service_id: score})

def dequeue_next():
    items = r.zrevrange('service_priority_queue', 0, 0)
    if items:
        service_id = items[0]
        r.zrem('service_priority_queue', service_id)
        return service_id

# Sliding-window rate limiter
def sliding_rate_limit(user_id, limit=100, window=3600):
    key = f'ratelimit:sliding:{user_id}'
    now = time.time()
    r.zremrangebyscore(key, 0, now - window)   # prune old entries
    count = r.zcard(key)
    if count >= limit:
        return False
    r.zadd(key, {str(now): now})
    r.expire(key, window)
    return True
```

---

## Part 5 — Session Management

```python
def create_session(jti: str, user_id: str, role: str) -> None:
    r.hset(f'session:{jti}', mapping={
        'user_id': user_id,
        'role': role,
        'login_time': datetime.utcnow().isoformat(),
    })
    r.expire(f'session:{jti}', 900)   # 15 min access token lifetime

def validate_session(jti: str) -> dict | None:
    key = f'session:{jti}'
    if not r.exists(key):
        return None   # Expired or logged out
    r.hset(key, 'last_activity', datetime.utcnow().isoformat())
    r.expire(key, 900)   # Slide window on activity
    return r.hgetall(key)

def logout(jti: str, ttl_remaining: int) -> None:
    r.delete(f'session:{jti}')
    # Blacklist the JTI so the token can't be reused before natural expiry
    r.setex(f'blacklist:{jti}', ttl_remaining, '1')

def is_blacklisted(jti: str) -> bool:
    return r.exists(f'blacklist:{jti}') == 1
```

---

## Part 6 — Caching Pattern (Cache-Aside)

```python
def get_nearby_services(lat: float, lng: float, radius_km: int) -> list:
    cache_key = f'cache:nearby:{lat:.4f}:{lng:.4f}:{radius_km}'

    # 1. Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # 2. Cache miss → query PostgreSQL
    results = db.execute("""
        SELECT service_id, service_type, priority, address,
               ST_AsGeoJSON(location)::json AS location
        FROM service_requests
        WHERE ST_DWithin(location::geography,
                         ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
                         %s)
          AND status IN ('APPROVED', 'ACCEPTED', 'IN_PROGRESS')
    """, [lng, lat, radius_km * 1000]).fetchall()

    # 3. Store in cache (5 min)
    r.setex(cache_key, 300, json.dumps(results))
    return results

def invalidate_nearby_cache(lat: float, lng: float) -> None:
    """Call after creating or updating a service request."""
    pattern = f'cache:nearby:{lat:.2f}*'
    keys = r.keys(pattern)
    if keys:
        r.delete(*keys)
```

---

## Part 7 — Rate Limiting

```python
def check_rate_limit(identifier: str, limit: int, window: int) -> tuple[bool, int]:
    """
    Returns (allowed: bool, remaining: int).
    identifier: IP address or user_id
    limit:      max requests in window
    window:     seconds (e.g. 60, 900, 3600)
    """
    key = f'ratelimit:{identifier}'
    count = r.incr(key)
    if count == 1:
        r.expire(key, window)
    remaining = max(0, limit - count)
    return count <= limit, remaining

# Usage in FastAPI middleware
allowed, remaining = check_rate_limit(request.client.host, limit=60, window=60)
if not allowed:
    raise HTTPException(status_code=429, headers={
        'X-RateLimit-Limit': '60',
        'X-RateLimit-Remaining': '0',
        'Retry-After': '60',
    })
```

---

## Part 8 — Pub/Sub (WebSocket fan-out)

The Bun API Gateway subscribes to Redis Pub/Sub and fans out messages to connected WebSocket clients.

**Publisher** (FastAPI — called after status changes):

```python
def publish_service_event(event_type: str, service_data: dict) -> None:
    """Publish to Redis; Bun gateway receives and forwards to WebSocket clients."""
    message = json.dumps({
        'type': event_type,      # 'request_created' | 'request_updated' | 'request_deleted'
        'request': service_data,
        'timestamp': datetime.utcnow().isoformat(),
    })
    r.publish('pubsub:service_requests', message)

# Call after creating a service request
publish_service_event('request_created', service_dict)

# Call after status change
publish_service_event('request_updated', service_dict)
```

**Subscriber** (Bun gateway — `src/backend/api-gateway/ws.ts`):

```typescript
const subscriber = redis.createClient({ url: 'redis://localhost:6379' });
await subscriber.subscribe('pubsub:service_requests', (message) => {
  const event = JSON.parse(message);
  // Fan out to all WebSocket clients subscribed to service_requests
  broadcastToSubscribers('service_requests', event);
});
```

---

## Part 9 — Geospatial Operations

Redis GEORADIUS is used to cache and query active provider locations. The primary geo queries run in PostGIS; Redis provides a 30-second cache for provider proximity.

```python
# Store provider's current GPS location (updated by mobile app every 30 s)
r.geoadd('active_providers', [lng, lat, f'provider:{org_id}'])
r.expire('active_providers', 120)   # Remove stale providers after 2 min

# Find providers within 10 km
nearby = r.georadius(
    'active_providers',
    lng, lat,
    10, unit='km',
    withdist=True,
    withcoord=True,
    count=20,
    sort='ASC',
)
```

---

## Part 10 — Performance Tips

```python
# Pipeline — multiple commands in one round-trip
pipe = r.pipeline()
pipe.hset(f'session:{jti}', mapping=session_data)
pipe.expire(f'session:{jti}', 900)
pipe.sadd('active_users', user_id)
pipe.execute()   # All three commands sent and executed atomically

# MGET — retrieve multiple keys at once
cache_keys = [f'cache:user:{uid}' for uid in user_ids]
cached_users = r.mget(cache_keys)   # One round-trip for all

# HGETALL instead of multiple HGETs
session = r.hgetall(f'session:{jti}')   # One command, all fields
```

---

## Common Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| No TTL on cache | `r.set(key, data)` | `r.setex(key, 300, data)` |
| Not checking None on GET | `json.loads(r.get(key))` | `if cached := r.get(key): json.loads(cached)` |
| Storing large payloads | Cache 10 MB DB dump | Cache 10 KB summary |
| Key name collisions | `r.set('user', data)` | `r.set('user:123:profile', data)` |
| Invalidating too broadly | `r.flushdb()` | Delete only affected keys by pattern |

---

**See also**:
- `backup/46-REDIS-OPERATIONS-REFERENCE.md` — Full beginner tutorial with all 30 commands
- `docs/IDRM-Database-Query-Reference.md` — PostgreSQL query reference
- `start-here/COMPLETE-API-SPECS-GUIDE.md` — API endpoints that trigger cache invalidation
