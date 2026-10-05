# IDRM Architecture Guide

## Complete System Architecture Reference

**Version**: 3.0
**Last Updated**: May 29, 2026
**Audience**: Tech-literate managers, new team members, architects
**Purpose**: Reader-friendly architecture overview. For the deep-dive, see [IDRM-HLD.md](./development/IDRM-HLD.md).

---

## 📋 Table of Contents

1. [What is IDRM?](#1-what-is-idrm)
2. [Architecture Overview](#2-architecture-overview)
3. [Three Frontend Platforms](#3-three-frontend-platforms)
4. [Technology Stack](#4-technology-stack)
5. [Service Descriptions](#5-service-descriptions)
6. [Port Map](#6-port-map)
7. [How Components Communicate](#7-how-components-communicate)
8. [Data Architecture](#8-data-architecture)
9. [Security Architecture](#9-security-architecture)
10. [Why We Made These Choices (ADRs)](#10-why-we-made-these-choices-adrs)
11. [Deployment Environments](#11-deployment-environments)
12. [Future Technology Evolution](#12-future-technology-evolution)
13. [Further Reading](#13-further-reading)

---

## 1. What is IDRM?

**IDRM** (Integrated Disaster Response Management) is a government-backed, map-driven platform that connects citizens in crisis with NGOs, hospitals, and volunteers — think "Uber for Disaster Relief."

> **Architecture philosophy**: Start with a monolith that supports three frontend platforms and can evolve into microservices without architectural debt.

**Current state (v3)**:

- Single modular FastAPI backend (one process, clean internal boundaries)
- One Bun API Gateway in front
- Three frontend platforms served from the same backend
- PostgreSQL + PostGIS for geospatial data
- Redis for caching, sessions, and real-time pub/sub

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       Ubuntu 22.04/24.04 LTS                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    FRONTEND LAYER (3 Platforms)                   │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  HTML/Tailwind      React SPA         React Native               │  │
│  │  (Vite/Bun)         (Vite/React)      (Expo)                     │  │
│  │  Port 5173          Port 5174         Expo Dev Server            │  │
│  └──────────────────────┬────────────────┬──────────────────────────┘  │
│                         │                │                              │
│                         ↓                ↓                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    API GATEWAY (Bun)                              │  │
│  │                    Port 3000                                      │  │
│  │  - WebSocket server (Port 3001)                                   │  │
│  │  - JWT validation                                                 │  │
│  │  - CORS handling                                                  │  │
│  │  - Rate limiting (via Redis)                                      │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│                         ↓                                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │      MODULAR FASTAPI BACKEND (Python/FastAPI + Miniconda)         │  │
│  │      Port 8000  — Single process, clean internal modules          │  │
│  │                                                                    │  │
│  │  Modules (src/backend/app-python/api/):                           │  │
│  │  ├─ api/auth.py             (Authentication)                      │  │
│  │  ├─ api/services.py         (Service Management)                  │  │
│  │  ├─ api/geo.py              (Geospatial)                          │  │
│  │  ├─ api/analytics.py        (Analytics)                           │  │
│  │  ├─ api/users.py            (User Management)                     │  │
│  │  └─ api/admin.py            (Admin)                               │  │
│  └──────────────────────┬───────────────────────────────────────────┘  │
│                         │                                               │
│  ┌──────────────────────────────────────┬───────────────────────────┐  │
│  │  PostgreSQL 16 + PostGIS 3.4         │   Redis 7.2+              │  │
│  │  (Port 5432)                         │   (Port 6379)             │  │
│  │  Native systemd                      │   Native systemd          │  │
│  └──────────────────────────────────────┴───────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘

Production flow:
User (Web/Mobile) → NGINX → Bun API Gateway → FastAPI Backend → PostgreSQL/Redis
```

> **Monolith vs Microservices**: IDRM v3 uses a **Modular Monolith** — all backend logic runs in one FastAPI process. The service boundaries are clean (separate modules), which means extraction into microservices is possible in the future (Year 2-3) with minimal refactoring. See `archive/MIGRATION-TO-MICROSERVICES-v3.md` for the future migration plan.

---

## 3. Three Frontend Platforms

All three frontends connect to the **same backend API** through the Bun gateway.

| Platform                | Port | Technology                       | Audience                    |
| ----------------------- | ---- | -------------------------------- | --------------------------- |
| **HTML/Tailwind** | 5173 | Vite + Vanilla JS + Tailwind CSS | Citizens (public-facing)    |
| **React SPA**     | 5174 | React 18 + TypeScript + Vite     | Admin dashboards            |
| **React Native**  | Expo | Expo SDK + React Native          | Field workers (iOS/Android) |

**When to use each**:

- **HTML/Tailwind** — When you need something fast and accessible that works in poor connectivity. Progressive enhancement by default.
- **React SPA** — When building complex admin workflows: data visualizations, bulk operations, analytics dashboards.
- **React Native** — For field workers who need GPS, camera, push notifications, and offline-first capability.

---

## 4. Technology Stack

> ⚠️ This is the official v3 stack. No alternatives permitted without an ADR.

| Layer                                | Technology              | Version       | Purpose                                             |
| ------------------------------------ | ----------------------- | ------------- | --------------------------------------------------- |
| **Reverse Proxy**              | NGINX                   | 1.24+         | SSL termination, routing, static files              |
| **API Gateway**                | Bun                     | 1.x           | WebSocket, routing, JWT validation, rate limiting   |
| **Backend Framework**          | FastAPI                 | 0.104+        | REST APIs, async support, auto-generated docs       |
| **Backend Language**           | Python 3.11             | via Miniconda | Business logic, geospatial processing               |
| **Database**                   | PostgreSQL              | 16.x          | Primary data store                                  |
| **Geospatial Extension**       | PostGIS                 | 3.4.x         | Spatial data types, 500+ spatial functions          |
| **Cache / Sessions / Pub-Sub** | Redis                   | 7.2+          | Caching, sessions, real-time notifications          |
| **Python Environment**         | Miniconda               | Latest        | Manages binary geospatial dependencies (GDAL, GEOS) |
| **Frontend Build**             | Bun + Vite              | 1.x / 5.x     | Fast dev and production builds                      |
| **Mobile**                     | Expo (React Native)     | SDK 49+       | iOS + Android from one codebase                     |
| **Containerization**           | Docker / Docker Compose | 24.x+         | Staging and production only (not development)       |

### Key Geospatial Libraries (Python)

```python
geopandas==0.14.1      # Spatial dataframes
shapely==2.0.2         # Geometric operations (point-in-polygon, etc.)
fiona==1.9.5           # Vector file I/O
pyproj==3.6.1          # Coordinate system transformations
gdal==3.8.0            # Geospatial data abstraction
```

---

## 5. Service Descriptions

These are the **logical modules** inside the single FastAPI backend. In the future they can be extracted as separate microservices.

### Auth Module (`/auth`)

Handles user authentication and authorization.

- User registration and email verification
- Login/logout with JWT tokens (access: 1h, refresh: 7d)
- Password reset flow
- Role-based access control (RBAC)

**Key endpoints**: `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout`

### Service Management (`/services`)

The core of IDRM — manages disaster service requests through their full lifecycle.

- Create, read, update, delete service requests
- Service-provider matching (using geospatial proximity)
- State machine: `SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED` (+ `REJECTED`, `CANCELLED`, `EXPIRED`, `DISPUTED`)

**Key endpoints**: `POST /services`, `GET /services`, `POST /services/{id}/accept`

### Geospatial Module (`/geo`)

Replaces Java GeoServer with a lightweight Python service. Serves map data directly from PostGIS.

- Proximity queries (find services within N km)
- Point clustering (K-means via PostGIS)
- GeoJSON feature serving

**Key endpoints**: `GET /geo/nearby`, `GET /geo/cluster`, `POST /geo/within`

### Analytics Module (`/analytics`)

Dashboard statistics and reporting for administrators.

**Key endpoints**: `GET /analytics/dashboard`, `GET /analytics/reports`

### Notifications Module (`/notifications`)

Multi-channel notification delivery.

- Email notifications via SMTP
- Template management (Jinja2)
- Real-time via WebSocket/Redis pub-sub

**Key endpoints**: `GET /notifications`, `PUT /notifications/{id}/read`

### User & Admin Module (`/users`, `/admin`)

User profile management and system administration.

- User management (approve, ban, roles)
- Audit log viewing
- System configuration

---

## 6. Port Map

| Service                | Port     | Notes                          |
| ---------------------- | -------- | ------------------------------ |
| NGINX                  | 80 / 443 | Production reverse proxy       |
| Bun API Gateway        | 3000     | All API traffic enters here    |
| Bun WebSocket          | 3001     | Real-time updates              |
| FastAPI Backend        | 8000     | Single modular backend process |
| HTML/Tailwind frontend | 5173     | Dev server (Vite + Bun)        |
| React SPA frontend     | 5174     | Dev server (Vite)              |
| React Native           | Expo     | Expo dev server (auto-port)    |
| PostgreSQL             | 5432     | Primary database               |
| Redis                  | 6379     | Cache and pub/sub              |

> **In production**: Users only access port 443 (HTTPS). NGINX routes internally to Bun on 3000, which routes to FastAPI on 8000.

---

## 7. How Components Communicate

### Standard Request-Response Flow

```
User/Mobile → NGINX → Bun Gateway → FastAPI Backend → PostgreSQL/Redis → Response
```

1. Request arrives at NGINX (SSL termination)
2. NGINX routes `/api/*` traffic to Bun on port 3000
3. Bun validates the JWT token, checks rate limits
4. Bun forwards the request to FastAPI on port 8000
5. FastAPI processes business logic, queries PostgreSQL
6. Response bubbles back through Bun → NGINX → User

### Real-Time Event Flow (WebSocket)

```
Service updated → FastAPI → Redis Pub/Sub → Bun WebSocket Server → Connected Clients
```

1. A service request status changes in FastAPI
2. FastAPI publishes an event to Redis channel `service_updates`
3. Bun WebSocket server is subscribed to that channel
4. Bun broadcasts the event to all connected WebSocket clients
5. Frontends update their UI in real time

### Service-to-Service Requests (Within the Monolith)

Since it's a monolith, service-to-service calls are just Python function calls — no HTTP overhead. When we migrate to microservices, these become HTTP calls.

---

## 8. Data Architecture

### Database Schema Overview

```
users
├─ user_roles (role assignments)
└─ user_permissions (fine-grained)

service_requests  ← core entity
├─ service_history (status changes audit trail)
├─ service_assignments (provider assignments)
└─ service_feedback (completion ratings)

service_providers
├─ provider_capacity (available slots)
└─ provider_service_areas (PostGIS polygons — where they operate)

disaster_events
├─ event_boundaries (PostGIS geometry)
└─ event_updates (status updates)

audit_log (all sensitive actions — immutable)
notifications_log (delivery history)
```

### Geospatial Data Model

PostGIS uses WGS 84 (SRID 4326) for all geometry:

```sql
-- Point geometry (service request location)
location GEOMETRY(Point, 4326)
-- Example: POINT(80.2707 13.0827)  — Chennai

-- Polygon geometry (service provider's coverage area)
area GEOMETRY(Polygon, 4326)

-- Spatial index (GIST) for fast proximity queries
CREATE INDEX idx_service_location
ON service_requests USING GIST(location);

-- Find services within 5km of a point
SELECT id, ST_Distance(location::geography,
    ST_MakePoint(80.2707, 13.0827)::geography) AS distance_m
FROM service_requests
WHERE ST_DWithin(location::geography,
    ST_MakePoint(80.2707, 13.0827)::geography, 5000)
ORDER BY distance_m;
```

### Redis Key Patterns

```
session:{user_id}                    → JWT token data (1h TTL)
rate:{ip}:{endpoint}                 → Request counter (1min TTL)
cache:services:active                → Active services JSON (5min TTL)
cache:providers:nearby:{lat}:{lon}   → Nearby providers JSON (2min TTL)
ws:connections                       → Set of active WebSocket connection IDs
```

---

## 9. Security Architecture

### Authentication Flow

1. User submits credentials → FastAPI Auth module verifies (bcrypt cost=12)
2. FastAPI generates JWT access token (15 min) + refresh token (7d)
3. Token sent as `Authorization: Bearer`; stored in an httpOnly cookie (web) or secure storage (mobile)
4. Every subsequent request: Bun validates the JWT *before* forwarding to FastAPI
5. Token revocation: short expiry + Redis blacklist for immediate revocation

### Role Hierarchy

```
System Admin  → full access
Event Admin   → manage disaster events
Executive     → view analytics
Manager       → manage providers
Organizer     → coordinate services
Volunteer     → accept and complete requests
Participant   → submit service requests
Individual    → view public information
```

### Security Layers

| Layer       | Mechanism                                                |
| ----------- | -------------------------------------------------------- |
| Network     | HTTPS only (TLS 1.3), UFW firewall                       |
| Gateway     | JWT validation, rate limiting, security headers          |
| Application | Pydantic input validation, RBAC, SQL ORM                 |
| Data        | bcrypt password hashing, audit logging, PII minimization |
| Transport   | All inter-service calls over internal network only       |

**NGINX Security Headers**:

```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## 10. Why We Made These Choices (ADRs)

Architecture Decision Records explain the *why* behind every major technology choice.

### ADR-001: Bun over Node.js

**Benchmarks** (our testing, 10,000 requests):

- Node.js 20: 25,000 req/s, 250MB RAM, 800ms startup
- Bun 1.x: 90,000 req/s, 175MB RAM, 200ms startup

**Result**: 3.6x faster, 30% less memory, 4x faster startup. Built-in TypeScript, bundler, and test runner remove tooling overhead. **Accepted with high confidence.**

### ADR-002: Python + FastAPI over Node.js (backend)

Python has the best geospatial library ecosystem (GDAL, Shapely, GeoPandas, Fiona). Geospatial operations are 3.7x faster in Python vs Node.js/Turf.js. FastAPI provides async/await, Pydantic validation, and auto-generated OpenAPI docs. Also positions the project for future ML/data science work. **Accepted with high confidence.**

### ADR-003: PostgreSQL + PostGIS over MongoDB

PostGIS spatial queries are **4.7x faster** than MongoDB (180ms vs 850ms for 10,000-record proximity search). PostGIS has 1,000+ spatial functions vs MongoDB's 34 spatial operators. PostgreSQL's ACID guarantees are critical for financial transactions (donations, fund allocations). **Accepted with very high confidence.**

### ADR-004: Python Geospatial Service over Java GeoServer

GeoServer requires Java runtime (512MB–1GB memory minimum, 30–45s startup). The Python service uses 100–200MB and starts in 2–3 seconds. Same language as the rest of the stack = faster development. We only need the subset of GeoServer's features that we can build ourselves. **Accepted** (may add GeoServer in Year 2 if WMS/WFS standards compliance is needed).

### ADR-005: Miniconda over venv/Poetry

GDAL, GEOS, and PROJ have complex C binary dependencies. With `venv + pip install gdal` you get hours of troubleshooting. With `conda install gdal` everything installs in 5 minutes. Miniconda is the only practical choice for geospatial Python development. **Accepted with very high confidence.**

### ADR-006: Modular Monolith over Microservices (MVP)

A modular monolith is simpler to build, deploy, and debug. Disaster response context requires reliability over complexity. For a 2–5 person team, microservices add network overhead and deployment complexity without enough benefit. Clean module boundaries mean we can *extract* microservices later without rewrites. **Accepted** — see `MIGRATION-TO-MICROSERVICES-v3.md` for the future plan.

### ADR-007: REST over GraphQL / gRPC

IDRM has simple, well-defined resources — REST is sufficient. GraphQL adds complexity without a clear MVP benefit. HTTP caching works out of the box with REST. gRPC is considered for future inter-service calls if latency becomes a bottleneck. **Accepted.**

### ADR-008: Redis over Memcached

Memcached is simple key-value only. Redis adds data structures (lists, sets, sorted sets), pub/sub, persistence, and atomic operations. IDRM uses all five Redis capabilities: sessions, API caching, rate limiting, real-time pub/sub, and WebSocket connection tracking. Only Redis supports all five. **Accepted with very high confidence.**

### ADR-009: Async/Await throughout (FastAPI)

Under 1,000 concurrent users, synchronous Django/Flask would need 1,000 threads (massive memory). FastAPI with asyncio handles 10,000 concurrent connections with ~500MB memory. Critical for disaster scenarios where traffic spikes by 10x overnight. **Accepted — essential.**

### ADR-010: JWT over Session Cookies

JWT is stateless — no server-side session database lookups. Works across all three platforms (web, SPA, mobile) uniformly. Short expiry (1h) mitigates the inability to revoke tokens immediately; Redis blacklist handles immediate revocation when needed. **Accepted.**

### ADR-011: bcrypt cost factor 12

Cost 10 = ~100ms per hash (too fast, weaker against brute force). Cost 12 = ~250ms (OWASP recommended). Cost 14 = ~1,000ms (too slow, hurts UX). Factor 12 is the industry standard — battle-tested, simple, correct. **Accepted.**

### ADR-012: Three-tier environment strategy

- **Development**: Native Ubuntu (no Docker) — fast iteration, easy debugging
- **Staging**: Docker Compose — production parity, catches environment issues before they go live
- **Production**: Docker + security hardening — isolation, rollback, monitoring

**Accepted — optimal for each environment's needs.**

---

## 11. Deployment Environments

### Development (Native Ubuntu)

No Docker. All services run directly on the host for fast iteration:

```bash
# Terminal 1: Backend (FastAPI — Modular Monolith)
conda activate idrm-mvp
cd src/backend/app-python && uvicorn main:app --reload --port 8000

# Terminal 2: API Gateway
cd src/backend/api-gateway && bun run dev   # Port 3000

# Terminal 3: HTML/Tailwind frontend
cd src/frontend/web-html && bun run dev   # Port 5173

# Terminal 4: React SPA
cd src/frontend/web-react && bun run dev   # Port 5174

# Terminal 5: React Native (optional)
cd src/frontend/mobile-expo && npx expo start

# Database/cache run as native systemd services
sudo systemctl start postgresql redis-server
```

### Staging (Docker Compose)

All services containerized. See `docs/IDRM-DEPLOYMENT-GUIDE.md` → Staging section.

```bash
docker compose -f docker/staging/docker-compose.yml up -d
```

### Production (Docker + Security)

Blue-green deployment via CI/CD. Adds SSL, firewall, monitoring, automated backups. See `docs/IDRM-DEPLOYMENT-GUIDE.md` → Production section.

**Production Tiers**:

| Tier            | Users        | Resources                        | Cost/mo     |
| --------------- | ------------ | -------------------------------- | ----------- |
| MVP (Tier 1)    | 500–1,000   | Single server: 8 vCPU, 16GB RAM  | ~$96        |
| Growth (Tier 2) | 2,000–5,000 | 2 app servers + load balancer    | ~$250       |
| Scale (Tier 3)  | 10,000+      | Auto-scaling cluster, DB replica | $500–2,000 |

**When to scale**: CPU > 70% sustained, or p95 response times > 500ms.

---

## 12. Future Technology Evolution

These are planned infrastructure upgrades — not needed now, but identified in advance so the team knows the exact triggers. Each is deliberately deferred; adopting them too early adds operational complexity without proportional benefit.

| Planned Upgrade                             | Current State                                       | Adopt When                                                                           | Why Wait                                                                                                                      |
| ------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **Kubernetes**                        | Docker Compose                                      | >100,000 DAU or >10,000 concurrent users                                             | Docker Compose handles 10k users; Kubernetes adds significant operational overhead without benefit at MVP scale               |
| **Message Queue** (RabbitMQ or Kafka) | Direct Python function calls (monolith)             | After microservices extraction, when inter-service HTTP latency becomes a bottleneck | Zero network overhead in the monolith; message queues add broker complexity that isn't justified until services are separated |
| **CDN for Map Tiles**                 | Python geospatial service serves tiles from PostGIS | >1M tile requests/day                                                                | Monthly CDN cost not justified at MVP traffic; PostGIS with spatial indexes handles early-scale tile serving adequately       |

### Kubernetes

Docker Compose is the current production deployment tool. Kubernetes earns its operational complexity when:

- Daily active users exceed **100,000**, or
- Sustained concurrent users exceed **10,000**

Below those thresholds, adding more servers behind a load balancer (Tier 2/3 from §11) achieves the same horizontal scaling with far simpler operations. The team also needs Kubernetes expertise before it's introduced — the tooling curve is steep.

### Message Queue (RabbitMQ / Kafka)

In the current monolith, all "service-to-service" calls are plain Python function calls — zero network latency, zero broker. After microservices extraction, services communicate over HTTP. A message queue only becomes worthwhile if that HTTP inter-service latency itself becomes a measured bottleneck. For disaster-response workloads (event-driven, latency-tolerant) direct HTTP between services is sufficient for years.

Extraction order when the time comes: Geospatial → Notifications → Analytics. See `start-here/COMPLETE-MONITORING-GUIDE.md` → Scaling Guide.

### CDN for Map Tiles

The Python geospatial module generates and serves map tiles directly from PostGIS. A CDN (Cloudflare or CloudFront) would cache frequently-requested tiles at the edge — useful for global distribution at high volume. The crossover point where CDN cost beats compute cost is approximately **>1M tile requests/day**. Until then, the geospatial service with PostGIS GIST indexes handles the load at lower cost.

> Full microservices migration runbook: `archive/MIGRATION-TO-MICROSERVICES-v3.md`

---

## 13. Further Reading

| Document                                                                            | What it covers                                                                       |
| ----------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| [IDRM-HLD.md](./development/IDRM-HLD.md)                                               | Deep-dive: all data flows, sequence diagrams, infrastructure, security design (93KB) |
| [IDRM-LLD.md](./development/IDRM-LLD.md)                                               | Low-level: API specs, DB schema, class diagrams, test strategy (95KB)                |
| [IDRM-PRD.md](./development/IDRM-PRD.md)                                               | Product requirements: features, user types, timelines, budgets (82KB)                |
| [IDRM-FS.md](./development/IDRM-FS.md)                                                 | Functional spec: what the system does from a user perspective                        |
| [../start-here/COMPLETE-API-SPECS-GUIDE.md](../start-here/COMPLETE-API-SPECS-GUIDE.md) | API contracts for frontend developers                                                |
| [../start-here/COMPLETE-DATABASE-GUIDE.md](../start-here/COMPLETE-DATABASE-GUIDE.md)   | Database schema + query reference                                                    |
| [./diagrams/](./diagrams/)                                                             | Mermaid diagrams: components, data flow, entity classes, use cases                   |
| [../CLAUDE.md](../CLAUDE.md)                                                           | AI context file: quick API reference and dev commands                                |

---

*This guide was merged from `301-monolith-architecture-v3.md`, `10-SYSTEM-ARCHITECTURE.md`, `11-ARCHITECTURE-DECISIONS.md`, and `IDRM-V3-CLARIFICATIONS-AND-DECISIONS.md`.*
