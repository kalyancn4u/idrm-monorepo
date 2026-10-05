> *Type: Document (specification) · Audience: DevOps, backend devs · Status: Archived — v3 historical generation*

# IDRM: Complete Redis Operations Reference

<!-- IDRM-CLEANUP doc=v3-81-redis status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — Redis = FFP (not in MVP)
> **No Redis in the MVP** — sessions live in PostgreSQL (ADR-005). Redis (cache/streams/rate-limit) is **FFP** →
> [`../../../../docs/ffp/81-ops-messaging-and-async.md`](../../../../docs/ffp/81-ops-messaging-and-async.md) +
> [`../../../instructions/caching-messaging.md`](../../../instructions/caching-messaging.md) + [`event-driven-architecture-101`](../../../../guides/mvp/learn/event-driven-architecture-101.md).
> Conformance `PICS-STK-REDIS-F01`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## All Redis Commands & Patterns Explained for Beginners

**Version**: 3.0 Consolidated  
**Audience**: Backend developers, Complete beginners to Redis  
**Reading Time**: 60 minutes  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [What is Redis? (For Complete Beginners)](#1-what-is-redis-for-complete-beginners)
2. [Quick Reference: All Operations](#2-quick-reference-all-operations)
3. [Basic String Operations](#3-basic-string-operations)
4. [Hash Operations (Objects/Records)](#4-hash-operations-objectsrecords)
5. [List Operations (Arrays/Queues)](#5-list-operations-arraysqueues)
6. [Set Operations (Unique Collections)](#6-set-operations-unique-collections)
7. [Sorted Set Operations (Rankings)](#7-sorted-set-operations-rankings)
8. [Session Management](#8-session-management)
9. [Caching Patterns](#9-caching-patterns)
10. [Rate Limiting](#10-rate-limiting)
11. [Pub/Sub (Real-time Notifications)](#11-pubsub-real-time-notifications)
12. [Geospatial Operations](#12-geospatial-operations)
13. [Common Patterns & Best Practices](#13-common-patterns--best-practices)

---

## 1. **What is Redis? (For Complete Beginners)**

### 1.1 Simple Explanation

**Redis** = **Super-fast temporary storage** for your application!

**Real-World Analogy**:

```
PostgreSQL Database:
┌────────────────────────────────┐
│  Like a Filing Cabinet         │
│  • Permanent storage           │
│  • Organized by tables         │
│  • Slower but reliable         │
│  • Data stays forever          │
└────────────────────────────────┘

Redis Cache:
┌────────────────────────────────┐
│  Like a Desk (workspace)       │
│  • Temporary storage           │
│  • Quick access                │
│  • 100x faster!                │
│  • Data expires automatically  │
└────────────────────────────────┘
```

**Why Redis?**
- ⚡ **Speed**: 100-1000x faster than database
- 💾 **RAM-based**: Data stored in memory (not disk)
- ⏰ **Auto-expiry**: Data disappears after set time
- 📦 **Simple**: Key-value pairs (like a dictionary)

---

### 1.2 When to Use Redis vs PostgreSQL

| Use Case | Use Redis? | Use PostgreSQL? | Why? |
|----------|------------|-----------------|------|
| Store user profile | ❌ No | ✅ Yes | Permanent data |
| Cache user profile | ✅ Yes | ❌ No | Fast repeated access |
| Store service request | ❌ No | ✅ Yes | Permanent data |
| Cache API response | ✅ Yes | ❌ No | Avoid re-computing |
| Session tokens | ✅ Yes | ❌ No | Temporary + fast |
| Rate limiting | ✅ Yes | ❌ No | Fast counting |
| Real-time notifications | ✅ Yes | ❌ No | Pub/Sub feature |
| Live user tracking | ✅ Yes | ⚠️ Maybe | Temporary data |

**Golden Rule**: 
- **PostgreSQL** = Permanent, important data
- **Redis** = Temporary, frequently accessed data

---

### 1.3 How IDRM Uses Redis

```
IDRM Architecture:
                    
User Request → API Gateway → Check Redis Cache
                                    ↓
                          Found? → Return immediately ⚡
                                    ↓
                          Not found? → Query PostgreSQL
                                           ↓
                                      Store in Redis
                                           ↓
                                      Return to user
                                           
Speed: 5ms (Redis) vs 50ms (PostgreSQL) = 10x faster!
```

**IDRM Redis Usage**:
1. ✅ **Session tokens** (JWT storage)
2. ✅ **API response caching** (nearby services, dashboard)
3. ✅ **Rate limiting** (prevent abuse)
4. ✅ **Real-time data** (active users, live updates)
5. ✅ **Temporary locks** (prevent double-booking)
6. ✅ **Pub/Sub** (notifications)

---

## 2. **Quick Reference: All Operations**

### 2.1 Complete Command Catalog

| # | Operation | Redis Command | Purpose | Difficulty |
|---|-----------|---------------|---------|------------|
| **STRINGS (Simple Values)** |
| 1 | Set value | SET | Store data | 🟢 Easy |
| 2 | Get value | GET | Retrieve data | 🟢 Easy |
| 3 | Set with expiry | SETEX | Auto-delete after time | 🟢 Easy |
| 4 | Delete | DEL | Remove data | 🟢 Easy |
| 5 | Increment | INCR | Count up by 1 | 🟢 Easy |
| 6 | Check exists | EXISTS | Does key exist? | 🟢 Easy |
| **HASHES (Objects/Records)** |
| 7 | Set field | HSET | Store object property | 🟢 Easy |
| 8 | Get field | HGET | Get object property | 🟢 Easy |
| 9 | Get all fields | HGETALL | Get entire object | 🟢 Easy |
| 10 | Delete field | HDEL | Remove property | 🟢 Easy |
| **LISTS (Arrays/Queues)** |
| 11 | Push left | LPUSH | Add to start | 🟢 Easy |
| 12 | Push right | RPUSH | Add to end | 🟢 Easy |
| 13 | Pop left | LPOP | Remove from start | 🟢 Easy |
| 14 | Get range | LRANGE | Get portion of list | 🟢 Easy |
| **SETS (Unique Collections)** |
| 15 | Add member | SADD | Add unique item | 🟢 Easy |
| 16 | Remove member | SREM | Remove item | 🟢 Easy |
| 17 | Check member | SISMEMBER | Is item in set? | 🟢 Easy |
| 18 | Get all members | SMEMBERS | Get all items | 🟢 Easy |
| **SORTED SETS (Rankings)** |
| 19 | Add with score | ZADD | Add ranked item | 🟡 Medium |
| 20 | Get by rank | ZRANGE | Get top N items | 🟡 Medium |
| 21 | Get by score | ZRANGEBYSCORE | Items in score range | 🟡 Medium |
| 22 | Increment score | ZINCRBY | Increase rank | 🟡 Medium |
| **EXPIRY & TTL** |
| 23 | Set expiry | EXPIRE | Auto-delete after N sec | 🟢 Easy |
| 24 | Get TTL | TTL | Time remaining | 🟢 Easy |
| 25 | Remove expiry | PERSIST | Never expire | 🟢 Easy |
| **GEOSPATIAL** |
| 26 | Add location | GEOADD | Store GPS point | 🟡 Medium |
| 27 | Get distance | GEODIST | Distance between points | 🟡 Medium |
| 28 | Find nearby | GEORADIUS | Points within radius | 🟡 Medium |
| **PUB/SUB** |
| 29 | Publish | PUBLISH | Send notification | 🟡 Medium |
| 30 | Subscribe | SUBSCRIBE | Listen for notifications | 🟡 Medium |

**Total Commands**: 30 essential operations

---

### 2.2 Data Type Usage Distribution

**How often you'll use each type**:

```
Daily Use (100+ times/day):
├─ Strings (GET/SET/SETEX)           60%
├─ Hashes (HGET/HSET/HGETALL)        25%
├─ Expiry (EXPIRE/TTL)               10%
└─ Others                             5%

Weekly Use (10-50 times/week):
├─ Lists (message queues)            30%
├─ Sets (unique tracking)            25%
├─ Sorted Sets (rankings)            20%
├─ Geospatial (live tracking)        15%
└─ Pub/Sub (notifications)           10%
```

---

## 3. **Basic String Operations**

### 3.1 Understanding Strings

**What are Redis Strings?**
- Simplest data type
- Can store: text, numbers, JSON, even binary data
- Like variables in programming

**Analogy**: Like sticky notes on your desk!

---

### 3.2 SET - Store Data

#### **Operation #1: Basic SET**

```redis
SET user:123:name "John Doe"
```

**Breakdown**:
```
SET user:123:name "John Doe"
│   │    │   │    │
│   │    │   │    └─ Value to store
│   │    │   └────── Field name
│   │    └────────── User ID
│   └─────────────── Namespace
└─────────────────── Command

Key naming pattern: namespace:id:field
```

**Python Example**:
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Store user's name
r.set('user:123:name', 'John Doe')

# Store JSON data
import json
user_data = {'name': 'John', 'email': 'john@example.com'}
r.set('user:123:profile', json.dumps(user_data))
```

---

#### **Operation #2: SETEX - Set with Expiry**

**Most important operation for caching!**

```redis
SETEX session:abc123 900 "user_id:123"
```

**Breakdown**:
```
SETEX session:abc123 900 "user_id:123"
│     │             │   │
│     │             │   └─ Value
│     │             └───── Expire after 900 seconds (15 min)
│     └─────────────────── Key name
└───────────────────────── Set with expiry
```

**Python Example**:
```python
# Store session token for 15 minutes
r.setex('session:abc123', 900, 'user_id:123')

# Store cached API response for 5 minutes
api_response = json.dumps({'services': [...]})
r.setex('cache:nearby:78.48:17.38', 300, api_response)
```

**Use Cases**:
- ✅ Session tokens (auto-logout after timeout)
- ✅ API cache (refresh automatically)
- ✅ OTP codes (expire after 5 minutes)
- ✅ Temporary locks (prevent race conditions)

---

### 3.3 GET - Retrieve Data

#### **Operation #3: Basic GET**

```redis
GET user:123:name
```

**Returns**: `"John Doe"`

**Python Example**:
```python
# Get user's name
name = r.get('user:123:name')
print(name.decode('utf-8'))  # "John Doe"

# Get cached API response
cached = r.get('cache:nearby:78.48:17.38')
if cached:
    data = json.loads(cached)
    return data  # Use cached data!
else:
    data = query_database()  # Cache miss, query DB
    r.setex('cache:nearby:78.48:17.38', 300, json.dumps(data))
    return data
```

---

### 3.4 Increment/Decrement

#### **Operation #4: INCR - Count Up**

```redis
INCR page_views:homepage
```

**What it does**: Increases number by 1 (atomic operation!)

**Python Example**:
```python
# Track API calls
r.incr('api:calls:user:123')

# Track daily requests
today = datetime.now().strftime('%Y-%m-%d')
r.incr(f'stats:requests:{today}')

# Get count
count = r.get('api:calls:user:123')
print(int(count))  # 42
```

**Use Cases**:
- ✅ Page view counters
- ✅ API rate limiting
- ✅ Daily statistics
- ✅ Like/vote counts

---

### 3.5 Check Existence

#### **Operation #5: EXISTS**

```redis
EXISTS session:abc123
```

**Returns**: `1` (exists) or `0` (doesn't exist)

**Python Example**:
```python
# Check if session is valid
if r.exists('session:abc123'):
    print("Session valid!")
else:
    print("Session expired, please login")
```

---

## 4. **Hash Operations (Objects/Records)**

### 4.1 Understanding Hashes

**What are Redis Hashes?**
- Store objects with multiple fields
- Like a Python dictionary or JavaScript object
- Better than storing JSON strings

**Analogy**: Like a form with multiple fields!

```
String (JSON):                 Hash:
SET user:123 "{                HSET user:123 name "John"
  'name': 'John',              HSET user:123 email "john@example.com"
  'email': '...'               HSET user:123 age 30
}"                             

Problem: Must parse JSON        Benefit: Access individual fields!
```

---

### 4.2 Hash Operations

#### **Operation #6: HSET - Set Field**

```redis
HSET user:123 name "John Doe"
HSET user:123 email "john@example.com"
HSET user:123 age 30
```

**Python Example**:
```python
# Store user profile
r.hset('user:123', 'name', 'John Doe')
r.hset('user:123', 'email', 'john@example.com')
r.hset('user:123', 'age', 30)

# Or all at once (Redis 4.0+)
r.hset('user:123', mapping={
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})
```

---

#### **Operation #7: HGET - Get Field**

```redis
HGET user:123 email
```

**Returns**: `"john@example.com"`

**Python Example**:
```python
# Get specific field
email = r.hget('user:123', 'email')
print(email.decode('utf-8'))
```

---

#### **Operation #8: HGETALL - Get All Fields**

```redis
HGETALL user:123
```

**Returns**: 
```
1) "name"
2) "John Doe"
3) "email"
4) "john@example.com"
5) "age"
6) "30"
```

**Python Example**:
```python
# Get entire user object
user = r.hgetall('user:123')
print(user)
# {b'name': b'John Doe', b'email': b'john@example.com', b'age': b'30'}

# Decode to regular dictionary
user_decoded = {k.decode('utf-8'): v.decode('utf-8') 
                for k, v in user.items()}
```

---

### 4.3 Real-World Hash Example

**Use Case**: Cache user session data

```python
# Store session with multiple fields
session_id = 'session:abc123'
r.hset(session_id, mapping={
    'user_id': '123',
    'role': 'CITIZEN',
    'login_time': '2026-05-16T10:00:00Z',
    'ip_address': '203.0.113.1'
})

# Set expiry on entire hash (15 minutes)
r.expire(session_id, 900)

# Later, check session
if r.exists(session_id):
    user_id = r.hget(session_id, 'user_id').decode('utf-8')
    role = r.hget(session_id, 'role').decode('utf-8')
    print(f"User {user_id} with role {role}")
else:
    print("Session expired")
```

---

## 5. **List Operations (Arrays/Queues)**

### 5.1 Understanding Lists

**What are Redis Lists?**
- Ordered collection of strings
- Can push/pop from both ends
- Perfect for queues and recent activity

**Analogy**: Like a queue at a ticket counter!

```
Queue:
[Person1] ← [Person2] ← [Person3] ← New person joins (RPUSH)
   ↓
Person1 leaves (LPOP)
```

---

### 5.2 List Operations

#### **Operation #9: LPUSH - Add to Start**

```redis
LPUSH recent_services:user:123 "service:999"
LPUSH recent_services:user:123 "service:888"
```

**Result**: `["service:888", "service:999"]` (newest first!)

**Python Example**:
```python
# Track user's recent service requests
r.lpush('recent_services:user:123', 'service:999')
r.lpush('recent_services:user:123', 'service:888')

# Keep only last 10
r.ltrim('recent_services:user:123', 0, 9)
```

---

#### **Operation #10: RPUSH - Add to End**

```redis
RPUSH notification_queue "notification:1"
RPUSH notification_queue "notification:2"
```

**Result**: `["notification:1", "notification:2"]`

**Python Example**:
```python
# Add to notification queue
r.rpush('notification_queue', json.dumps({
    'user_id': '123',
    'message': 'Your service request was approved'
}))
```

---

#### **Operation #11: LPOP - Remove from Start**

```redis
LPOP notification_queue
```

**Returns**: `"notification:1"` (and removes it)

**Python Example**:
```python
# Process notification queue
while True:
    notification = r.lpop('notification_queue')
    if not notification:
        break
    
    data = json.loads(notification)
    send_push_notification(data['user_id'], data['message'])
```

---

#### **Operation #12: LRANGE - Get Range**

```redis
LRANGE recent_services:user:123 0 4
```

**Returns**: First 5 items (indices 0-4)

**Python Example**:
```python
# Get user's 10 most recent services
recent = r.lrange('recent_services:user:123', 0, 9)
recent_decoded = [s.decode('utf-8') for s in recent]
```

---

### 5.3 Real-World List Example

**Use Case**: Recent activity feed

```python
def add_activity(user_id, activity):
    """Add activity to user's feed, keep last 50"""
    key = f'activity_feed:user:{user_id}'
    
    # Add new activity
    r.lpush(key, json.dumps({
        'type': activity['type'],
        'message': activity['message'],
        'timestamp': datetime.now().isoformat()
    }))
    
    # Keep only last 50 activities
    r.ltrim(key, 0, 49)
    
    # Set expiry (30 days)
    r.expire(key, 30 * 24 * 60 * 60)

def get_recent_activities(user_id, count=10):
    """Get user's recent activities"""
    key = f'activity_feed:user:{user_id}'
    activities = r.lrange(key, 0, count - 1)
    return [json.loads(a) for a in activities]
```

---

## 6. **Set Operations (Unique Collections)**

### 6.1 Understanding Sets

**What are Redis Sets?**
- Unordered collection of unique strings
- No duplicates allowed
- Fast membership testing

**Analogy**: Like a bag of unique marbles!

```
List:  [A, B, C, A, B] ← Can have duplicates
Set:   {A, B, C}       ← Unique only!
```

---

### 6.2 Set Operations

#### **Operation #13: SADD - Add Member**

```redis
SADD active_users "user:123"
SADD active_users "user:456"
SADD active_users "user:123"  ← Ignored (already exists)
```

**Result**: `{user:123, user:456}`

**Python Example**:
```python
# Track active users
r.sadd('active_users', 'user:123')
r.sadd('active_users', 'user:456')

# Set expiry (refresh every hour)
r.expire('active_users', 3600)
```

---

#### **Operation #14: SISMEMBER - Check Membership**

```redis
SISMEMBER active_users "user:123"
```

**Returns**: `1` (is member) or `0` (not member)

**Python Example**:
```python
# Check if user is active
if r.sismember('active_users', 'user:123'):
    print("User is online!")
else:
    print("User is offline")
```

---

#### **Operation #15: SMEMBERS - Get All Members**

```redis
SMEMBERS active_users
```

**Returns**: All unique members

**Python Example**:
```python
# Get all active users
active = r.smembers('active_users')
print(f"{len(active)} users online")
```

---

### 6.3 Real-World Set Example

**Use Case**: Track users who viewed a service

```python
def track_view(service_id, user_id):
    """Track that user viewed this service"""
    key = f'service:{service_id}:viewers'
    r.sadd(key, user_id)
    r.expire(key, 24 * 60 * 60)  # 24 hours

def get_view_count(service_id):
    """Get unique view count"""
    key = f'service:{service_id}:viewers'
    return r.scard(key)  # SCARD = count members

def has_viewed(service_id, user_id):
    """Check if user already viewed"""
    key = f'service:{service_id}:viewers'
    return r.sismember(key, user_id)
```

---

## 7. **Sorted Set Operations (Rankings)**

### 7.1 Understanding Sorted Sets

**What are Sorted Sets?**
- Like Sets, but each member has a score
- Automatically sorted by score
- Perfect for leaderboards and rankings

**Analogy**: Like a scoreboard!

```
Leaderboard:
Alice:  95 points
Bob:    87 points
Carol:  82 points
         ↑
    Sorted by score!
```

---

### 7.2 Sorted Set Operations

#### **Operation #16: ZADD - Add with Score**

```redis
ZADD provider_rankings 95 "provider:123"
ZADD provider_rankings 87 "provider:456"
ZADD provider_rankings 82 "provider:789"
```

**Python Example**:
```python
# Track provider ratings
r.zadd('provider_rankings', {
    'provider:123': 4.8,  # Average rating
    'provider:456': 4.5,
    'provider:789': 4.2
})
```

---

#### **Operation #17: ZRANGE - Get by Rank**

```redis
ZRANGE provider_rankings 0 9 WITHSCORES
```

**Returns**: Top 10 providers with scores (lowest to highest)

**For highest to lowest, use ZREVRANGE**:
```redis
ZREVRANGE provider_rankings 0 9 WITHSCORES
```

**Python Example**:
```python
# Get top 10 providers (highest rating first)
top_providers = r.zrevrange('provider_rankings', 0, 9, withscores=True)

for provider_id, score in top_providers:
    print(f"{provider_id.decode('utf-8')}: {score} stars")
```

---

#### **Operation #18: ZINCRBY - Increment Score**

```redis
ZINCRBY provider_rankings 0.1 "provider:123"
```

**What it does**: Increases score by 0.1

**Python Example**:
```python
# Update provider rating after new review
def update_provider_rating(provider_id, new_rating):
    # Simplified: just increment average
    r.zincrby('provider_rankings', new_rating, provider_id)
```

---

### 7.3 Real-World Sorted Set Example

**Use Case**: Service priority queue

```python
def add_to_priority_queue(service_id, priority):
    """Add service to priority queue"""
    # Higher priority = higher score
    priority_score = {
        'CRITICAL': 1000,
        'HIGH': 500,
        'MEDIUM': 100,
        'LOW': 10
    }
    
    score = priority_score[priority] + time.time()
    r.zadd('service_priority_queue', {service_id: score})

def get_next_service():
    """Get highest priority service"""
    # Get highest score (ZREVRANGE)
    services = r.zrevrange('service_priority_queue', 0, 0)
    if services:
        service_id = services[0].decode('utf-8')
        r.zrem('service_priority_queue', service_id)  # Remove from queue
        return service_id
    return None
```

---

## 8. **Session Management**

### 8.1 JWT Token Storage

**Use Case**: Store session tokens with auto-expiry

```python
def create_session(user_id, jwt_token):
    """Store JWT token in Redis"""
    session_key = f'session:{jwt_token}'
    
    # Store user data
    r.hset(session_key, mapping={
        'user_id': user_id,
        'login_time': datetime.now().isoformat(),
        'last_activity': datetime.now().isoformat()
    })
    
    # Set expiry (15 minutes)
    r.expire(session_key, 900)
    
    return session_key

def validate_session(jwt_token):
    """Check if session is valid"""
    session_key = f'session:{jwt_token}'
    
    if not r.exists(session_key):
        return None
    
    # Update last activity
    r.hset(session_key, 'last_activity', datetime.now().isoformat())
    
    # Refresh expiry
    r.expire(session_key, 900)
    
    # Return user data
    return r.hgetall(session_key)

def logout(jwt_token):
    """Invalidate session"""
    session_key = f'session:{jwt_token}'
    r.delete(session_key)
```

---

## 9. **Caching Patterns**

### 9.1 Cache-Aside Pattern

**Most common caching pattern!**

```python
def get_nearby_services(lat, lng, radius):
    """Get nearby services with caching"""
    
    # Create cache key
    cache_key = f'cache:nearby:{lat}:{lng}:{radius}'
    
    # Try to get from cache
    cached = r.get(cache_key)
    if cached:
        print("Cache HIT!")
        return json.loads(cached)
    
    print("Cache MISS - querying database")
    # Query database
    services = query_database_nearby(lat, lng, radius)
    
    # Store in cache (5 minutes)
    r.setex(cache_key, 300, json.dumps(services))
    
    return services
```

**Benefits**:
- ✅ 10-100x faster on cache hits
- ✅ Reduces database load
- ✅ Auto-expires stale data

---

### 9.2 Cache Invalidation

**When to invalidate cache?**

```python
def create_service_request(data):
    """Create service and invalidate cache"""
    
    # Save to database
    service_id = save_to_database(data)
    
    # Invalidate nearby caches
    lat = data['location']['coordinates'][1]
    lng = data['location']['coordinates'][0]
    
    # Delete cache keys that might be affected
    # This is simplified - in production, use patterns
    keys_to_delete = r.keys(f'cache:nearby:{lat:.2f}:*')
    if keys_to_delete:
        r.delete(*keys_to_delete)
    
    return service_id
```

---

## 10. **Rate Limiting**

### 10.1 Simple Rate Limiter

**Use Case**: Limit API calls to 100 per hour per user

```python
def check_rate_limit(user_id, limit=100, window=3600):
    """Check if user exceeded rate limit"""
    
    key = f'rate_limit:{user_id}'
    
    # Increment counter
    current = r.incr(key)
    
    # Set expiry on first request
    if current == 1:
        r.expire(key, window)
    
    # Check limit
    if current > limit:
        return False, 0  # Limit exceeded
    
    # Get remaining requests
    remaining = limit - current
    return True, remaining

# Usage
allowed, remaining = check_rate_limit('user:123')
if not allowed:
    return {"error": "Rate limit exceeded"}
```

---

### 10.2 Sliding Window Rate Limiter

**More accurate rate limiting**

```python
def sliding_window_rate_limit(user_id, limit=100, window=3600):
    """Sliding window rate limiter"""
    
    key = f'rate_limit:sliding:{user_id}'
    now = time.time()
    
    # Remove old entries
    r.zremrangebyscore(key, 0, now - window)
    
    # Count recent requests
    count = r.zcard(key)
    
    if count >= limit:
        return False, 0
    
    # Add current request
    r.zadd(key, {str(now): now})
    r.expire(key, window)
    
    remaining = limit - (count + 1)
    return True, remaining
```

---

## 11. **Pub/Sub (Real-time Notifications)**

### 11.1 Understanding Pub/Sub

**What is Pub/Sub?**
- Publisher sends messages
- Subscribers receive messages
- Real-time notifications

**Analogy**: Like a radio broadcast!

```
Publisher (Radio Station):
    "Breaking news: Service approved!"
           ↓
     [Broadcast]
           ↓
    ┌──────┼──────┐
    ↓      ↓      ↓
User1  User2  User3 (Subscribers/Listeners)
```

---

### 11.2 Publisher Code

```python
def notify_service_update(service_id, status):
    """Publish service status update"""
    
    channel = f'service_updates:{service_id}'
    message = json.dumps({
        'service_id': service_id,
        'status': status,
        'timestamp': datetime.now().isoformat()
    })
    
    # Publish to channel
    r.publish(channel, message)
    print(f"Published to {channel}")
```

---

### 11.3 Subscriber Code

```python
def listen_for_service_updates(service_id):
    """Subscribe to service updates"""
    
    pubsub = r.pubsub()
    channel = f'service_updates:{service_id}'
    pubsub.subscribe(channel)
    
    print(f"Listening on {channel}...")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            print(f"Received: {data}")
            
            # Send push notification
            send_push_notification(data)
```

---

## 12. **Geospatial Operations**

### 12.1 Store Locations

#### **Operation #19: GEOADD**

```redis
GEOADD active_providers 78.4867 17.3850 "provider:123"
GEOADD active_providers 78.5200 17.4100 "provider:456"
```

**Python Example**:
```python
# Track provider locations
r.geoadd('active_providers', 
    78.4867, 17.3850, 'provider:123',
    78.5200, 17.4100, 'provider:456'
)
```

---

### 12.2 Find Nearby

#### **Operation #20: GEORADIUS**

```redis
GEORADIUS active_providers 78.4867 17.3850 5 km WITHDIST
```

**Python Example**:
```python
# Find providers within 5km
nearby = r.georadius(
    'active_providers',
    78.4867, 17.3850,  # Center point
    5, unit='km',       # 5 kilometers
    withdist=True,      # Include distance
    withcoord=True      # Include coordinates
)

for provider_id, distance, coords in nearby:
    print(f"{provider_id.decode('utf-8')}: {distance} km away")
```

---

### 12.3 Calculate Distance

#### **Operation #21: GEODIST**

```redis
GEODIST active_providers "provider:123" "provider:456" km
```

**Returns**: `3.5` (kilometers)

**Python Example**:
```python
# Distance between two providers
distance = r.geodist('active_providers', 'provider:123', 'provider:456', 'km')
print(f"Distance: {distance} km")
```

---

## 13. **Common Patterns & Best Practices**

### 13.1 Key Naming Conventions

**Follow consistent patterns!**

```
Good:
user:123:profile
user:123:sessions:abc
service:456:viewers
cache:nearby:78.48:17.38

Bad:
user123
userProfile_123
service-viewers-456
```

**Pattern**: `object_type:id:attribute[:sub_attribute]`

---

### 13.2 Expiry Best Practices

```python
# Always set expiry for caches!
r.setex('cache:data', 300, value)  # 5 minutes

# Session data
r.setex('session:token', 900, data)  # 15 minutes

# Temporary locks
r.setex('lock:service:123', 30, 'locked')  # 30 seconds

# Daily stats (expire next day)
tomorrow = datetime.now() + timedelta(days=1)
tomorrow_midnight = tomorrow.replace(hour=0, minute=0, second=0)
ttl = int((tomorrow_midnight - datetime.now()).total_seconds())
r.setex('stats:today', ttl, data)
```

---

### 13.3 Common Mistakes to Avoid

#### **Mistake #1: Not Setting Expiry**

```python
# ❌ BAD - Data never expires!
r.set('cache:user:123', data)

# ✅ GOOD - Auto-cleanup
r.setex('cache:user:123', 300, data)
```

#### **Mistake #2: Storing Large Values**

```python
# ❌ BAD - 10MB JSON in Redis
huge_data = get_huge_dataset()  # 10MB
r.set('huge:data', json.dumps(huge_data))

# ✅ GOOD - Only cache what's needed
summary = summarize(huge_data)  # 10KB
r.setex('summary:data', 300, json.dumps(summary))
```

#### **Mistake #3: Not Handling Cache Misses**

```python
# ❌ BAD - Crashes if not cached
cached = r.get('cache:data')
return json.loads(cached)  # Error if None!

# ✅ GOOD - Always check
cached = r.get('cache:data')
if cached:
    return json.loads(cached)
else:
    data = query_database()
    r.setex('cache:data', 300, json.dumps(data))
    return data
```

---

### 13.4 Performance Tips

```python
# Use pipelines for multiple commands
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.set('key3', 'value3')
pipe.execute()  # All executed in one round-trip!

# Use MGET for multiple GETs
values = r.mget(['key1', 'key2', 'key3'])

# Use HGETALL instead of multiple HGETs
user = r.hgetall('user:123')  # One command
# vs
name = r.hget('user:123', 'name')  # Three commands
email = r.hget('user:123', 'email')
age = r.hget('user:123', 'age')
```

---

## 🎯 **Summary for Beginners**

### **What You Learned**:

1. ✅ **What Redis is** - Super-fast temporary storage
2. ✅ **5 Data Types** - String, Hash, List, Set, Sorted Set
3. ✅ **30 Operations** - All commands with examples
4. ✅ **Session Management** - JWT token storage
5. ✅ **Caching Patterns** - Speed up your app 10-100x
6. ✅ **Rate Limiting** - Prevent abuse
7. ✅ **Pub/Sub** - Real-time notifications
8. ✅ **Geospatial** - Location-based features

### **Most Used Operations** (95% of Work):

```python
# 1. Cache API responses
r.setex('cache:key', 300, json.dumps(data))
cached = r.get('cache:key')

# 2. Store sessions
r.hset('session:token', mapping={...})
r.expire('session:token', 900)

# 3. Track active users
r.sadd('active_users', user_id)

# 4. Rate limiting
r.incr(f'rate_limit:{user_id}')

# 5. Rankings
r.zadd('rankings', {user_id: score})
```

### **Golden Rules**:

1. ⏰ **Always set expiry** on cached data
2. 📦 **Keep values small** (KB not MB)
3. 🔑 **Use consistent key names**
4. ✅ **Handle cache misses** gracefully
5. 🚀 **Use pipelines** for multiple commands

---

**Document Complete!**  
**Total Operations Documented**: 30+  
**Difficulty**: 🟢 Beginner-friendly  
**Ready for Development**: ✅ YES

**See Also**:
- [25-BACKEND-IMPLEMENTATION.md](25-BACKEND-IMPLEMENTATION.md) - Using Redis in FastAPI
- [42-VERIFICATION-CHECKLISTS.md](42-VERIFICATION-CHECKLISTS.md) - Testing Redis
- [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md) - Redis configuration
