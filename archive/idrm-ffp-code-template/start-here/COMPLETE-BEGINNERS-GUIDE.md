# IDRM Complete Beginners Guide

## From Zero to Full-Stack Developer — Understanding and Building IDRM v3

**Version**: 3.0
**Audience**: Complete beginners to experienced developers
**Primary Source**: `docs/IDRM-DEVELOPMENT-GUIDE.md`

> **v3 Stack Notice**: This guide uses **Bun** (not npm/Node.js), **Miniconda** (not `python -m venv`), and a **Python geospatial service** (not Java/GeoServer). Any older references to npm, venv, or GeoServer describe v2 patterns that are no longer used.

---

## Table of Contents

1. [What is IDRM?](#1-what-is-idrm)
2. [Real-World Examples](#2-real-world-examples)
3. [Technology Stack Explained](#3-technology-stack-explained)
4. [Architecture for Beginners](#4-architecture-for-beginners)
5. [Choose Your Learning Path](#5-choose-your-learning-path)
6. [Getting Your Environment Running](#6-getting-your-environment-running)
7. [Building Your First Feature](#7-building-your-first-feature)
8. [Understanding the Codebase](#8-understanding-the-codebase)
9. [Testing Basics](#9-testing-basics)
10. [Next Steps and Resources](#10-next-steps-and-resources)

---

## 1. What is IDRM?

**IDRM** = **Integrated Disaster Response Management**

Think of it as **"Uber for disaster relief"** — connecting people who need help with organizations that can provide it, all tracked on an interactive map.

```
Uber:
  1. You need a ride
  2. Open app, request ride
  3. Driver accepts
  4. Track driver on map
  5. Driver arrives, ride completes

IDRM:
  1. Citizen needs help (flood/earthquake/fire)
  2. Create request on map
  3. NGO/Hospital accepts
  4. Track provider on map
  5. Service delivered, verified, rated
```

### What IDRM Does

**For Citizens** (people who need help):

- Create a service request on an interactive map
- Choose privacy level (public or private)
- Track the responding organization in real-time
- Verify service completion and rate the response

**For Service Providers** (NGOs, hospitals, volunteer groups):

- See nearby requests on a map
- Accept, fulfill, and mark complete
- View analytics on their service history

**For Coordinators** (government officials):

- Real-time dashboard of all active requests
- Approve critical requests, manage organizations
- Generate reports for disaster response planning

### Why Government Cares

During disasters (Mumbai floods, Chennai cyclone), traditional systems fail:

- Phone lines overloaded
- No way to match need with available resources
- No tracking or accountability
- No data for future planning

IDRM solves all of this with a digital platform.

---

## 2. Real-World Examples

### Mumbai Floods 2024

```
10:00 AM — Citizen A (Kurla):
  "I need medical help, chest pain"
  Creates MEDICAL request (CRITICAL priority)
  Location: 19.07°N, 72.88°E

          ↓ System matches nearest hospital

Sion Hospital:
  Accepts → Ambulance dispatched → ETA 15 min

          ↓ Real-time tracking

Citizen A:
  Sees ambulance approaching on map
  Ambulance arrives in 12 minutes
  Service completed and verified
  Rates 5 stars

Total time: 12 minutes | Lives saved: 1
```

### Chennai Cyclone 2025

```
6:00 PM — Mass event:
  150 SHELTER requests
  75 FOOD requests
  50 MEDICAL requests
  Total: 275 requests in 1 hour

IDRM auto-matching algorithm:
  ├─ Sort by priority (CRITICAL first)
  ├─ Match by distance (nearest provider)
  ├─ Balance load across providers
  └─ 25 NGOs + 10 hospitals activated

Result:
  245 of 275 requests fulfilled (89%)
  Average response time: 28 minutes
```

---

## 3. Technology Stack Explained

### The Full Stack

```
What Users See (Three Frontends):
├─ HTML/Tailwind (Port 5173) — Citizens, general public
│   Simple, fast, works everywhere, no JS required
│
├─ React SPA (Port 5174) — Coordinators, admins
│   Rich dashboards, complex workflows, charts
│
└─ React Native (Expo) — Field workers, providers
    iOS + Android, offline-first, GPS + camera

What Powers It (Backend):
├─ Bun API Gateway (Port 3000)
│   Rate limiting, CORS, JWT pre-validation, WebSocket
│
└─ FastAPI Backend (Port 8000)
    Business logic, database, geospatial calculations

Where Data Lives:
├─ PostgreSQL 16 + PostGIS 3.4 (Port 5432)
│   All permanent data + geospatial queries
│
└─ Redis 7.2 (Port 6379)
    Sessions, caching, real-time pub/sub
```

### Why These Technologies?

**Why Python + FastAPI?**

```
✅ Fast to develop
✅ Best geospatial libraries (GeoPandas, Shapely, GDAL)
✅ Automatic Swagger API docs
✅ Type safety with Pydantic
✅ Async support (handles many concurrent users)
```

**Why PostgreSQL + PostGIS?**

```
✅ Best geospatial database in the world
✅ Free and open-source
✅ ACID transactions (reliable)
✅ "Find all requests within 10km" — one SQL query
✅ Used by Uber, Instagram, Spotify
```

**Why Bun (not Node.js/npm)?**

```
✅ 3-4× faster than Node.js
✅ Built-in TypeScript support
✅ Built-in bundler, test runner
✅ 30% less memory
✅ Handles WebSockets natively
```

**Why Miniconda (not venv)?**

```
✅ Manages binary dependencies (GDAL, GEOS, PROJ)
✅ Without Miniconda, geospatial libraries fail to install
✅ Reproducible environments via environment.yml
✅ Industry standard for data/ML work
```

**Why Three Frontends?**

```
HTML/Tailwind: Works for anyone, anywhere, any device
React SPA:     Complex admin tools need React's power
React Native:  Field workers need offline + GPS + camera
```

---

## 4. Architecture for Beginners

### The "Restaurant" Analogy

Think of IDRM like a restaurant:

```
┌─────────────────────────────────────────────────────┐
│                    IDRM Restaurant                   │
│                                                      │
│  Customers (Users)                                   │
│  ├─ Walk-in (HTML/Tailwind web)                      │
│  ├─ Phone order (React SPA admin)                    │
│  └─ App order (React Native mobile)                  │
│                                                      │
│  Waiter (Bun API Gateway)                            │
│  ├─ Takes orders (routes requests)                   │
│  ├─ Checks ID (JWT validation)                       │
│  └─ Prevents abuse (rate limiting)                   │
│                                                      │
│  Chef (FastAPI Backend)                              │
│  ├─ Cooks food (processes business logic)            │
│  ├─ Knows recipes (geospatial matching)              │
│  └─ Logs orders (audit trail)                        │
│                                                      │
│  Storage:                                            │
│  ├─ Filing cabinet (PostgreSQL) — permanent records  │
│  └─ Desk workspace (Redis) — quick temporary notes  │
└─────────────────────────────────────────────────────┘
```

### How a Request Flows

```
Citizen opens app → picks location on map → submits MEDICAL request
  ↓
HTML/Tailwind frontend sends: POST http://localhost:3000/api/v1/services
  ↓
Bun Gateway checks: Rate limit OK? JWT valid?
  ↓
FastAPI Backend:
  - Validates input (service_type, coordinates, description)
  - Stores in PostgreSQL with PostGIS geometry
  - Runs spatial query: find organizations within 25km that handle MEDICAL
  - Sends WebSocket event: "new CRITICAL request at coordinates X,Y"
  - Creates notification for nearest 3 providers
  ↓
Provider's app receives WebSocket push notification
  ↓
Provider accepts → status changes to ACCEPTED → requestor notified
```

### Modular Monolith (Important!)

The backend is **one FastAPI app** (not 8 separate services). It has clean internal modules:

- `app/api/v1/auth.py` — authentication
- `app/api/v1/services.py` — service requests
- `app/api/v1/geo.py` — geospatial calculations
- `app/api/v1/analytics.py` — reports and dashboards

All modules run in **one process on port 8000**. This makes development simpler and deployment more reliable. Modules can be extracted into separate services later if needed.

---

## 5. Choose Your Learning Path

### Decision Tree

```
Have you coded before?
├─ NO → Path A: Complete Beginner
├─ YES (1-2 years) → Path B: Junior Developer
└─ YES (3+ years) → Path C: Experienced Developer

What do you want to build?
├─ Web pages → Focus on HTML/Tailwind + Python backend
├─ Admin tools → Focus on React SPA + Python backend
└─ Mobile app → Focus on React Native + Python backend

What's your strongest skill?
├─ Python → Start from backend, read frontend
├─ JavaScript/TypeScript → Start from frontend, read API
└─ Neither → Start from Part A below
```

### Path A: Complete Beginner (16 weeks)

```
Week 1-2:  Learn Python basics (https://python.org/about/gettingstarted/)
Week 3-4:  Learn HTML + CSS basics (https://developer.mozilla.org/en-US/)
Week 5-6:  Set up development environment (this guide)
Week 7-8:  Build first API endpoint (backend)
Week 9-10: Build first web page that calls the API (frontend)
Week 11-12: Add geospatial features (map + location)
Week 13-14: Add authentication (login/logout)
Week 15-16: Deploy to staging
```

### Path B: Junior Developer (8 weeks)

```
Week 1:   Set up environment + read architecture guide
Week 2:   Backend — understand models, schemas, CRUD patterns
Week 3:   Backend — implement 2-3 endpoints with tests
Week 4:   Frontend — understand how HTML/Tailwind calls the API
Week 5:   Full-stack — build one complete feature end-to-end
Week 6:   Geospatial — understand PostGIS, add map feature
Week 7:   Auth + security — understand JWT, sessions, RBAC
Week 8:   Deploy to staging + code review
```

### Path C: Experienced Developer (2 weeks)

```
Day 1:   Read CLAUDE.md (architecture overview + API quick reference)
Day 2:   Read IDRM-ARCHITECTURE-GUIDE.md (ADRs, design decisions)
Day 3:   Set up dev environment, run all 5 services
Day 4-5: Implement first feature (pick from GitHub issues)
Week 2:  Review CI/CD, deployment pipeline, write tests
```

---

## 6. Getting Your Environment Running

### Prerequisites Summary

```bash
# Install Bun (not npm!)
curl -fsSL https://bun.sh/install | bash

# Install Miniconda (not venv!)
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc

# Install PostgreSQL 16 + PostGIS
sudo apt install postgresql-16 postgresql-16-postgis-3

# Install Redis
sudo apt install redis-server

# Start system services
sudo systemctl start postgresql redis
```

Full detailed installation: [COMPLETE-SETUP-GUIDE.md](COMPLETE-SETUP-GUIDE.md) or [docs/IDRM-DEVELOPMENT-GUIDE.md](../docs/IDRM-DEVELOPMENT-GUIDE.md)

### Start All Services (5 Terminals)

```bash
# Terminal 1 — Backend
cd src/backend/app-python && conda activate idrm-mvp
uvicorn main:app --reload --port 8000

# Terminal 2 — API Gateway
cd src/backend/api-gateway && bun run dev

# Terminal 3 — HTML/Tailwind (citizens web)
cd src/frontend/web-html && bun run dev

# Terminal 4 — React SPA (admin)
cd src/frontend/web-react && bun run dev

# Terminal 5 — React Native (mobile)
cd src/frontend/mobile-expo && npx expo start
```

### Verify It Works

```bash
# Backend healthy?
curl http://localhost:8000/health
# Expected: {"status": "healthy"}

# API Gateway routing?
curl http://localhost:3000/health
# Expected: {"status": "ok", "gateway": "running"}

# Open in browser
# Citizens web:  http://localhost:5173
# Admin SPA:     http://localhost:5174
# API Swagger:   http://localhost:8000/docs
```

---

## 7. Building Your First Feature

### Example: "Display active service requests on a map"

**Step 1: Backend API** (already exists — verify it works)

```bash
# Get active service requests
curl -H "Authorization: Bearer {token}" \
  http://localhost:3000/api/v1/services?status=SUBMITTED,ACCEPTED
```

**Step 2: Frontend (HTML/Tailwind) — display on map**

```html
<!-- src/frontend/web-html/src/pages/app/map.html -->
<div id="map" style="height: 500px;"></div>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script>
const map = L.map('map').setView([17.3850, 78.4867], 12);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'OpenStreetMap contributors'
}).addTo(map);

async function loadActiveRequests() {
    const token = localStorage.getItem('access_token');
    const response = await fetch('/api/v1/services?status=SUBMITTED,ACCEPTED', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();

    data.data.forEach(service => {
        const [lon, lat] = service.location.coordinates;
        const color = service.priority === 'CRITICAL' ? 'red' : 'orange';
        L.circleMarker([lat, lon], { color, radius: 8 })
            .addTo(map)
            .bindPopup(`
                <b>${service.service_type}</b><br>
                Priority: ${service.priority}<br>
                Status: ${service.status}
            `);
    });
}

loadActiveRequests();
</script>
```

**Step 3: Test manually**

1. Navigate to http://localhost:5173/pages/app/map.html
2. Verify markers appear for each active request
3. Check browser console for errors

**Step 4: Write a test**

```python
# tests/test_api/test_services.py
async def test_get_active_services_returns_submitted_and_accepted(client, auth_headers, db_with_services):
    response = await client.get(
        "/api/v1/services?status=SUBMITTED,ACCEPTED",
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    for service in data:
        assert service["status"] in ["SUBMITTED", "ACCEPTED"]
```

---

## 8. Understanding the Codebase

### Where to Find Things

```
src/backend/app-python/
  main.py              ← FastAPI app + startup events
  api/
    auth.py            ← POST /auth/login, /register, /logout
    services.py        ← GET/POST /services, /services/{id}/*
    geo.py             ← GET /geo/nearby, /geo/cluster
    analytics.py       ← GET /analytics/dashboard, /reports
  dbmodels/
    user.py            ← SQLAlchemy User table
    service.py         ← SQLAlchemy ServiceRequest table
  schemas/
    service.py         ← Pydantic: ServiceCreate, ServiceResponse
  services/
    service_matching.py ← Business logic: find nearest provider
    geospatial.py      ← PostGIS wrapper functions
  core/
    config.py          ← Settings loaded from .env
    security.py        ← JWT creation and verification
    database.py        ← DB session management
    redis.py           ← Redis client
```

### Reading a Full Request Cycle

When `POST /api/v1/services` arrives:

```python
# 1. api/v1/services.py — route handler
@router.post("/", response_model=ServiceResponse, status_code=201)
async def create_service(
    data: ServiceCreate,          # Pydantic validates JSON body
    current_user: User = Depends(get_current_user),  # JWT check
    db: Session = Depends(get_db)
):
    # 2. services/service_matching.py — business logic
    service = await service_matching.create_and_match(db, data, current_user.user_id)

    # 3. Publish WebSocket event
    await publish_service_update(str(service.service_id), "service.created", {...})

    return service

# 4. crud/service.py — database write
async def create(db, service_create, requestor_id):
    db_service = ServiceRequest(
        requestor_id=requestor_id,
        location=f"SRID=4326;POINT({service_create.location.coordinates[0]} {service_create.location.coordinates[1]})",
        ...
    )
    db.add(db_service)
    db.commit()
    return db_service
```

### Common Patterns

**Adding a new endpoint**:

1. Add Pydantic schema to `src/backend/app-python/schemas/`
2. Add business logic to `src/backend/app-python/services/`
3. Add route to `src/backend/app-python/api/`
4. Register route in `src/backend/app-python/api/router.py`
5. Write test in `tests/test_api/`

**Debugging**:

- Backend logs: watch Terminal 1 (uvicorn output)
- API errors: check `http://localhost:8000/docs` — test there first
- DB queries: `psql -U idrm_user -d idrm_db` → run queries manually
- Redis state: `redis-cli keys "*"` → inspect live keys

---

## 9. Testing Basics

### Run Tests

```bash
# All backend tests
conda activate idrm-mvp
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/backend/app-python --cov-report=html
# Open: htmlcov/index.html

# Frontend tests
cd src/frontend/web-html    && bun test
cd src/frontend/web-react   && bun test
```

### Write Your First Test

```python
# tests/test_api/test_auth.py

class TestRegister:
    async def test_valid_registration_succeeds(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "SecurePass123!",
            "full_name": "Test User",
            "role": "CITIZEN"
        })
        assert response.status_code == 201
        assert response.json()["data"]["email"] == "test@example.com"
        assert "password" not in response.json()["data"]  # Never return password!

    async def test_weak_password_rejected(self, client):
        response = await client.post("/api/v1/auth/register", json={
            "email": "test2@example.com",
            "password": "weak",
            "full_name": "Test User"
        })
        assert response.status_code == 400
```

**Coverage target**: 80% minimum. 95% for auth and service request paths.

---

## 10. Next Steps and Resources

### Suggested Learning Order

1. **Day 1**: Read this guide + [CLAUDE.md](../CLAUDE.md)
2. **Day 2**: Set up environment, run all 5 services
3. **Day 3**: Read [IDRM-ARCHITECTURE-GUIDE.md](../docs/IDRM-ARCHITECTURE-GUIDE.md) — especially the ADRs (why each technology was chosen)
4. **Week 1**: Implement one small backend endpoint (e.g., GET /services/{id}/history)
5. **Week 2**: Implement the matching frontend component

### Key Documents

| Document                                                           | When to Read                              |
| ------------------------------------------------------------------ | ----------------------------------------- |
| [CLAUDE.md](../CLAUDE.md)                                             | Daily reference — API examples, commands |
| [COMPLETE-SETUP-GUIDE.md](COMPLETE-SETUP-GUIDE.md)                    | First time setup                          |
| [COMPLETE-API-SPECS-GUIDE.md](COMPLETE-API-SPECS-GUIDE.md)            | Building or calling any API               |
| [COMPLETE-DATABASE-GUIDE.md](COMPLETE-DATABASE-GUIDE.md)              | Database queries, schema                  |
| [COMPLETE-DevSecOps-GUIDE.md](COMPLETE-DevSecOps-GUIDE.md)            | Writing tests, code review                |
| [docs/IDRM-ARCHITECTURE-GUIDE.md](../docs/IDRM-ARCHITECTURE-GUIDE.md) | Understanding system design               |
| [docs/IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md)     | Deploying to staging/production           |

### External Learning Resources

| Topic               | Resource                                     |
| ------------------- | -------------------------------------------- |
| FastAPI             | https://fastapi.tiangolo.com/tutorial/       |
| SQLAlchemy          | https://docs.sqlalchemy.org/en/20/tutorial/  |
| PostGIS             | https://postgis.net/workshops/postgis-intro/ |
| Bun                 | https://bun.sh/docs                          |
| React               | https://react.dev/learn                      |
| React Native / Expo | https://docs.expo.dev/                       |
| Tailwind CSS        | https://tailwindcss.com/docs                 |

### Getting Help

1. Check the API docs at `http://localhost:8000/docs` — test endpoints there first
2. Read the error message carefully — FastAPI error messages are very informative
3. Check logs in the terminal for each service
4. Search the codebase: `grep -r "function_name" backend/`
5. Read the relevant guide in `docs/` or `start-here/`

---

**You're ready to start building IDRM!**

The system is designed to save lives during disasters. Every line of code you write matters.
