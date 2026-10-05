# IDRM Release Notes

## v3.0.0 — 2026-05-24

**Multi-Platform Disaster Response System — Major Version**

This release is a complete platform overhaul. The architecture, runtime stack, deployment approach, and frontend model have all changed substantially from v2.

---

### Breaking Changes (v2 → v3)

#### Runtime Stack Replaced

| Component | v2 | v3 | Impact |
|-----------|----|----|--------|
| JavaScript runtime | Node.js + npm | **Bun** | All `npm install` → `bun install`; `npm run` → `bun run` |
| Python environment | `python -m venv` | **Miniconda** (conda) | All venv workflows replaced with conda environments |
| Geospatial service | Java + GeoServer | **Python geospatial** (GeoPandas/Shapely) | Geospatial logic is now a Python module *inside the FastAPI monolith (port 8000)* — not a separate Java service |

**Migration**: Existing Node.js/venv setups are incompatible. Run `conda env create -f backend/environment.yml` and `bun install` in each frontend directory.

#### Architecture Changed

- **v2**: Loosely coupled services, each independently deployed
- **v3**: **Modular Monolith** — single FastAPI process on port 8000 with clean internal module boundaries. The logical service separation (auth, services, geo, analytics, notifications) exists at the code level, not the deployment level.

This decision (ADR-006) was made to reduce operational complexity at the MVP stage. Module boundaries are maintained to allow future microservice extraction.

#### Frontend Model Changed

- **v2**: Single frontend (HTML/Tailwind, port 5173)
- **v3**: **Three frontends** — HTML/Tailwind (5173, citizens), React SPA (5174, admin/coordinators), React Native (Expo, iOS + Android field workers)

All three frontends share the same backend API. CORS is configured to accept all three origins.

---

### New Features

#### Three Frontend Platforms

**HTML/Tailwind (Port 5173)** — Citizen-facing web app
- Progressive enhancement — works without JavaScript
- Optimized for low-bandwidth emergency conditions
- Leaflet.js interactive map for service requests
- Real-time status updates via WebSocket

**React SPA (Port 5174)** — Admin/coordinator dashboard
- Complex analytics dashboards with Recharts
- Bulk service request management
- Organization verification workflows
- Role-based access control UI

**React Native (Expo)** — Mobile app (iOS + Android)
- Offline-first capability for field workers
- GPS integration for automatic location tagging
- Push notifications via Expo Notifications
- QR code scanning for service verification

#### Bun API Gateway (Port 3000)

New gateway layer between NGINX and FastAPI:
- Rate limiting via Redis INCR (per IP, per endpoint)
- JWT pre-validation (reduces backend load)
- Unified CORS for all three frontends
- WebSocket server on port 3001 (Bun native)
- Security headers (CSP, HSTS, X-Frame-Options)
- Request/response logging

Performance: 3–4× faster than equivalent Node.js gateway, ~30% less memory.

#### Redis Integration (New in v3)

Redis 7.2 added as a required infrastructure component:
- **Session management**: `session:{user_id}` (7-day TTL)
- **Token blacklisting**: `blacklist:{jti}` (matched to token TTL)
- **API caching**: Response memoization with per-endpoint TTLs
- **Rate limiting**: Sliding window counters
- **Real-time pub/sub**: WebSocket event routing across services
- **WebSocket tracking**: Active connection registry

#### Python Geospatial Module (inside the monolith, port 8000)

Java/GeoServer removed. Replaced with Python-native geospatial stack:
- **GeoPandas**: Spatial data manipulation
- **Shapely**: Geometry operations
- **GDAL/PROJ**: Coordinate transformations
- **PostGIS**: Persistent spatial storage (4.7× faster spatial queries than MongoDB)

Key operations:
- Radius search (`ST_DWithin`)
- Bounding box queries (`ST_MakeEnvelope`)
- K-means clustering for heatmaps
- Distance calculation (`ST_Distance` on `geography` type)
- GeoJSON export for frontend map rendering

#### MAD Management System — 🔒 Post-MVP (planned)

**Planned (Post-MVP)** module for Misuse, Abuse, and Discrepancy detection — overlaps the Auditor credibility-scoring, which is also deferred:
- Credibility scoring based on behavioral signals
- Admin-controlled blacklist/whitelist management
- Automatic alert escalation to DM Authority
- Full audit trail (all actions logged to `audit_logs` table)

#### Multi-Tier Deployment

New deployment options with cost guidance:
- **Tier 1** (~$96/month): Single DigitalOcean Droplet for < 10,000 users
- **Tier 2** (~$192/month): Scaled Droplet for < 50,000 users
- **Tier 3** ($500–1,000/month): Multi-server + load balancer for < 200,000 users

Blue-green production deployments via GitHub Actions (zero downtime).

---

### Improvements

#### API Design

- All state-changing operations use POST (not PUT/DELETE) for consistent CSRF handling
- Rate limit headers (`X-RateLimit-*`) on all responses
- Consistent error response format: `{ "status": "error", "error": { "code", "message", "field" } }`
- URL-based API versioning (`/api/v1/`) — `/api/v2/` path reserved for future
- 37 endpoints total across auth, services, users, organizations, geospatial, analytics, admin

#### Security Hardening (Security Review)

- JWT access tokens: 15-minute TTL (down from 30 minutes in v2)
- Access token sent as `Authorization: Bearer` (the API contract); the web client may store it in an httpOnly cookie that the gateway also reads — avoids localStorage XSS exposure
- bcrypt cost factor: 12 (explicitly enforced, not default)
- SameSite=Lax cookie attribute — CSRF protection
- Login rate limit: 5 attempts per 15 minutes per IP
- All admin endpoints additionally require audit logging
- Container vulnerability scanning (Trivy) in CI/CD pipeline

#### Developer Experience

- Hot reload: < 100ms for all 5 services (native Ubuntu, no Docker in dev)
- 5-terminal development workflow with automation script (`dev-start-v3.sh`)
- Prerequisites verification script (`verify-prerequisites-v3.sh`)
- Auto-generated Swagger UI at `http://localhost:8000/docs`
- 3-scale mock data: unit test (10 users), integration (100 users), full (1,500 users)

#### Testing

- Coverage target: 80% overall, 95% for auth and service request critical paths
- Integration tests use real PostgreSQL + Redis (no mocks)
- Test pyramid: 70% unit, 20% integration, 10% E2E
- Locust load testing scripts included
- CI/CD runs full test suite on every PR with coverage gate

---

### Removed

| Removed | Reason | Replacement |
|---------|--------|-------------|
| Java | Eliminated GeoServer dependency | Python geospatial (GeoPandas) |
| GeoServer | Complex, Java-based, hard to maintain | Python geo module inside the monolith (port 8000) |
| Node.js | Replaced by faster runtime | Bun |
| npm | Replaced | bun (install, run, test, add) |
| `python -m venv` | Cannot manage binary geo deps | Miniconda conda environments |
| Single frontend | Limited to one user segment | Three platform frontends |
| Mixed HTTP methods (PUT/PATCH/DELETE) | CSRF complexity | POST-only for state changes |

---

### Migration Guide (v2 → v3)

#### Environment Setup

```bash
# Remove old Node.js environment (if present)
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Remove old venv
rm -rf .venv/

# Install Miniconda
# (see COMPLETE-SETUP-GUIDE.md for full instructions)
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp
pip install --break-system-packages -r backend/requirements.txt
```

#### Dependency Installation

```bash
# Old (v2)
npm install
npm run dev

# New (v3) — in each frontend directory
bun install
bun run dev
```

#### Starting Services

```bash
# Old (v2) — single frontend
python -m venv .venv && source .venv/bin/activate
uvicorn app.main:app --port 8000 &
npm run dev    # Single frontend on 5173

# New (v3) — 5-terminal approach
# See COMPLETE-SETUP-GUIDE.md → Section 4
./dev-start-v3.sh
```

#### Database Changes

```sql
-- New in v3: Redis session tracking column
ALTER TABLE users ADD COLUMN last_login_ip INET;
ALTER TABLE users ADD COLUMN preferences JSONB NOT NULL DEFAULT '{}'::jsonb;

-- New table: audit_logs (replaces scattered logging)
CREATE TABLE audit_logs (...);  -- See COMPLETE-DATABASE-GUIDE.md

-- PostGIS spatial index (required for v3 geospatial features)
CREATE INDEX idx_service_requests_location ON service_requests USING GIST (location);
```

Run `alembic upgrade head` to apply all migrations.

---

### Architecture Decision Records (ADRs) in v3

| ADR | Decision | Status |
|-----|---------|--------|
| ADR-001 | Bun over Node.js for API Gateway | Adopted |
| ADR-002 | Python/FastAPI over Node.js for backend | Adopted |
| ADR-003 | PostgreSQL + PostGIS over MongoDB | Adopted |
| ADR-004 | Python geospatial over Java GeoServer | Adopted |
| ADR-005 | Miniconda over venv | Adopted |
| ADR-006 | Modular Monolith over Microservices | Adopted |
| ADR-007 | REST over GraphQL | Adopted |
| ADR-008 | Redis over Memcached | Adopted |
| ADR-009 | Async/Await throughout | Adopted |
| ADR-010 | JWT over session cookies | Adopted |
| ADR-011 | bcrypt cost=12 | Adopted |
| ADR-012 | Three-tier environments (dev/staging/prod) | Adopted |

Full ADR rationale: [docs/IDRM-ARCHITECTURE-GUIDE.md](docs/IDRM-ARCHITECTURE-GUIDE.md)

---

## v2.0.0 — 2025-09-01

Initial multi-service platform with:
- Single HTML/Tailwind frontend
- Node.js/npm runtime
- Python venv environment management
- Java/GeoServer geospatial layer
- Basic JWT authentication
- PostgreSQL + PostGIS database

---

## v1.0.0 — 2025-01-15

Initial prototype:
- Proof of concept disaster response coordination
- Static HTML prototype
- Basic Python backend
- Manual deployment
