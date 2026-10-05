> *Type: Document (specification) · Audience: Architects, developers · Status: Archived — v1 historical generation*

# IDRM Web Platform Engineering Specification

> Simplified web-only architecture using Bun + Vanilla JS frontend and Python + PostgreSQL backend

<!-- IDRM-CLEANUP doc=v1-20-webplatform status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-1 web-platform architecture — mixes MVP web-UI ideas with microservices/gateway/Docker/WebSocket (**FFP**).
> Current source of truth: monolith `docs/mvp/20`, web UI `docs/mvp/60`. *Legend:* ✅ covered · ⚠ superseded · ⊘ dropped/FFP.
>
> | Snippet | Section | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v1-20§arch` | Architecture Overview | `docs/mvp/20` (monolith); microservices → `docs/ffp/20` | MVP/FFP | ⚠ |
> | `v1-20§fe` | Frontend (Web Only) · Page Structure · API Client | `docs/mvp/60` (HTML+Tailwind+JS) | MVP | ⚠ |
> | `v1-20§be` | Backend | `docs/mvp/20` (FastAPI) | MVP | ⚠ |
> | `v1-20§ws` | WebSocket Manager | deep real-time → FFP `81` | FFP | ⊘ |
> | `v1-20§gw` | API Gateway Structure | APISIX → `docs/ffp/20` + `api-gateway` spoke | FFP | ⊘ |
> | `v1-20§ms` | Python Microservice Structure | `docs/ffp/20` | FFP | ⊘ |
> | `v1-20§dc` | Docker Compose | native systemd (ADR-006); containers → FFP | FFP | ⊘ |
> | `v1-20§setup` | Setup · Development · Production Build | `docs/mvp/80` + `guides/mvp`; prod build → FFP CI/CD | MVP/FFP | ⚠ |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────┐
│      Web Browser (Client)               │
│   HTML + CSS + Vanilla JS + Leaflet     │
└─────────────────────────────────────────┘
                  ↓ HTTPS
┌─────────────────────────────────────────┐
│         NGINX (Reverse Proxy)           │
│      Static Files + SSL + WAF           │
└─────────────────────────────────────────┘
        ↓                    ↓
┌───────────────┐    ┌──────────────────┐
│  Static Web   │    │  API Gateway     │
│  Files (Bun)  │    │  (Bun/Express)   │
└───────────────┘    └──────────────────┘
                            ↓
                    ┌──────────────────┐
                    │  Redis Cache     │
                    └──────────────────┘
                            ↓
                ┌──────────────────────────┐
                │  Python Microservices    │
                │  (FastAPI)               │
                └──────────────────────────┘
                            ↓
        ┌───────────────────┴────────────────┐
        ↓                                    ↓
┌──────────────────┐              ┌──────────────────┐
│  PostgreSQL 16   │              │   GeoServer      │
│  + PostGIS 3.4   │←─────────────│   (WMS/WFS)      │
└──────────────────┘              └──────────────────┘
```

### How It Works

**1. Client Layer (Browser)**
- Pure HTML/CSS/JavaScript (no frameworks)
- Leaflet.js for interactive maps
- TailwindCSS for styling
- Socket.io client for real-time updates
- Built and bundled with Bun + Vite

**2. Web Server Layer (NGINX)**
- Serves static files (HTML, CSS, JS, images)
- Terminates SSL/TLS
- Reverse proxy to API Gateway
- Web Application Firewall (WAF)
- Caching static assets

**3. API Gateway Layer (Bun + Express)**
- Handles all HTTP requests
- JWT authentication
- WebSocket connections (Socket.io)
- Request routing to microservices
- Rate limiting
- Session management via Redis

**4. Business Logic Layer (Python FastAPI)**
- Service management microservice
- Geospatial analysis microservice
- Analytics microservice
- Financial tracking microservice
- Privacy/ReVV microservice
- Each service is independent and scalable

**5. Data Layer**
- PostgreSQL + PostGIS for all data
- Redis for caching and sessions
- GeoServer for map tile serving

### Request Flow Example

**User Creates Service Request:**
```
1. Browser → User fills form on /create-request.html
2. JS validates input → Collects location via Leaflet map
3. Fetch API → POST /api/v1/services/requests
4. NGINX → Forwards to API Gateway
5. API Gateway → Validates JWT token
6. API Gateway → Routes to Service Management microservice
7. Service Mgmt → Validates data, saves to PostgreSQL
8. Service Mgmt → Returns success response
9. API Gateway → Broadcasts via WebSocket to coordinators
10. Browser → Shows success message, updates map
```

**Real-time Update Flow:**
```
1. Provider updates status in backend
2. Python service → Publishes to Redis pub/sub
3. API Gateway → Listens to Redis, emits Socket.io event
4. Browser → Socket.io client receives event
5. JS → Updates map marker, shows notification
```

---

# Technology Stack

## Frontend (Web Only)

### Core Technologies
- **HTML5** - Semantic markup
- **CSS3 + TailwindCSS 3.x** - Utility-first styling
- **Vanilla JavaScript (ES6+)** - No frameworks
- **Bun 1.x** - Build tool and dev server
- **Vite 5.x** - Fast development server and bundler

### Mapping & Geospatial
- **Leaflet 1.9** - Interactive maps (MANDATORY)
- **Leaflet.markercluster** - Marker clustering
- **Leaflet.draw** - Drawing tools
- **Leaflet.routing** - Route calculation

### Communication
- **Socket.io Client 4.x** - Real-time updates
- **Axios** - HTTP client (alternative to fetch)

### Utilities
- **Day.js** - Date/time manipulation
- **Chart.js** - Data visualization
- **Alpine.js** (optional) - Lightweight reactivity

## Backend

### API Gateway
- **Bun 1.x** - Runtime
- **Express.js 4.x** - Web framework
- **Socket.io 4.x** - WebSocket server
- **Passport.js** - Authentication
- **Helmet.js** - Security headers
- **Express-validator** - Input validation
- **Winston** - Logging

### Python Microservices
- **Python 3.11** - Language
- **FastAPI 0.104+** - Framework
- **SQLAlchemy 2.0** - ORM
- **GeoAlchemy2** - PostGIS extension
- **Pydantic** - Data validation
- **Alembic** - Database migrations
- **Celery 5.x** - Background tasks

### Database & Caching
- **PostgreSQL 16** - Primary database
- **PostGIS 3.4** - Geospatial extension
- **Redis 7.2** - Cache and sessions

### Infrastructure
- **NGINX 1.24** - Web server and reverse proxy
- **GeoServer 2.24** - Map tile server
- **Docker & Docker Compose** - Containerization

---

# Project Structure

```
idrm-web/
├── frontend/
│   ├── src/
│   │   ├── index.html
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── config/
│   │   │   │   └── api.js
│   │   │   ├── auth/
│   │   │   │   ├── login.js
│   │   │   │   └── session.js
│   │   │   ├── map/
│   │   │   │   ├── map-manager.js
│   │   │   │   ├── layers.js
│   │   │   │   ├── markers.js
│   │   │   │   └── realtime.js
│   │   │   ├── services/
│   │   │   │   ├── service-list.js
│   │   │   │   ├── service-create.js
│   │   │   │   └── service-detail.js
│   │   │   ├── providers/
│   │   │   │   └── provider-map.js
│   │   │   ├── donations/
│   │   │   │   └── donation-form.js
│   │   │   └── utils/
│   │   │       ├── api-client.js
│   │   │       ├── websocket.js
│   │   │       ├── validation.js
│   │   │       └── helpers.js
│   │   ├── css/
│   │   │   ├── main.css
│   │   │   └── components/
│   │   ├── pages/
│   │   │   ├── index.html
│   │   │   ├── map.html
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   ├── services/
│   │   │   │   ├── list.html
│   │   │   │   ├── create.html
│   │   │   │   └── detail.html
│   │   │   ├── dashboard/
│   │   │   │   ├── citizen.html
│   │   │   │   ├── provider.html
│   │   │   │   └── coordinator.html
│   │   │   └── donations/
│   │   │       ├── donate.html
│   │   │       └── track.html
│   │   └── assets/
│   │       ├── images/
│   │       ├── icons/
│   │       └── fonts/
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── backend/
│   ├── api-gateway/
│   │   ├── src/
│   │   │   ├── index.js
│   │   │   ├── routes/
│   │   │   ├── middleware/
│   │   │   └── websocket/
│   │   └── package.json
│   │
│   └── services/
│       ├── service-management/
│       │   ├── app/
│       │   │   ├── main.py
│       │   │   ├── api/
│       │   │   ├── models/
│       │   │   ├── schemas/
│       │   │   └── services/
│       │   └── pyproject.toml
│       │
│       ├── geospatial/
│       ├── analytics/
│       ├── financial/
│       └── privacy/
│
├── infrastructure/
│   ├── nginx/
│   ├── postgres/
│   ├── redis/
│   └── geoserver/
│
└── docker-compose.yml
```

---

# Frontend Development

## Page Structure

Each HTML page follows this structure:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDRM - Page Title</title>
    <link rel="stylesheet" href="/css/main.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav id="navbar"></nav>
    
    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <!-- Page-specific content -->
    </main>
    
    <!-- Footer -->
    <footer id="footer"></footer>
    
    <!-- Scripts -->
    <script type="module" src="/js/main.js"></script>
    <script type="module" src="/js/pages/current-page.js"></script>
</body>
</html>
```

## API Client

```javascript
// frontend/src/js/utils/api-client.js
class APIClient {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/v1';
    this.token = localStorage.getItem('auth_token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (response.status === 401) {
        this.handleUnauthorized();
        throw new Error('Unauthorized');
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Request failed');
      }

      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth_token');
  }

  handleUnauthorized() {
    this.clearToken();
    window.location.href = '/pages/login.html';
  }
}

export const apiClient = new APIClient();
```

## WebSocket Manager

```javascript
// frontend/src/js/utils/websocket.js
import { io } from 'socket.io-client';

class WebSocketManager {
  constructor() {
    this.socket = null;
    this.connected = false;
  }

  connect(token) {
    this.socket = io(import.meta.env.VITE_WS_URL || 'http://localhost:3000', {
      auth: { token },
      transports: ['websocket'],
    });

    this.socket.on('connect', () => {
      this.connected = true;
      console.log('WebSocket connected');
    });

    this.socket.on('disconnect', () => {
      this.connected = false;
      console.log('WebSocket disconnected');
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  on(event, callback) {
    if (this.socket) {
      this.socket.on(event, callback);
    }
  }

  emit(event, data) {
    if (this.socket && this.connected) {
      this.socket.emit(event, data);
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }
}

export const wsManager = new WebSocketManager();
```

---

# Backend Development

## API Gateway Structure

```javascript
// backend/api-gateway/src/index.js
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { createServer } from 'http';
import { Server } from 'socket.io';
import authRoutes from './routes/auth.js';
import servicesRoutes from './routes/services.js';
import { authMiddleware } from './middleware/auth.js';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
    credentials: true,
  },
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/services', authMiddleware, servicesRoutes);

// WebSocket
io.use((socket, next) => {
  const token = socket.handshake.auth.token;
  // Verify token
  next();
});

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('service:subscribe', (serviceId) => {
    socket.join(`service:${serviceId}`);
  });
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
```

## Python Microservice Structure

```python
# backend/services/service-management/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title="IDRM Service Management")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

---

# Deployment

## Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_DB: idrm
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  geoserver:
    image: kartoza/geoserver:2.24.0
    environment:
      GEOSERVER_ADMIN_PASSWORD: ${GEOSERVER_PASSWORD}
    ports:
      - "8080:8080"
    depends_on:
      - postgres

  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/idrm
      REDIS_URL: redis://redis:6379
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "3000:3000"
    depends_on:
      - postgres
      - redis

  service-management:
    build:
      context: ./backend/services/service-management
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/idrm
    ports:
      - "8001:8000"
    depends_on:
      - postgres

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"

  nginx:
    image: nginx:1.24-alpine
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./frontend/dist:/usr/share/nginx/html
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api-gateway
      - frontend

volumes:
  postgres_data:
```

---

# Development Workflow

## Setup

```bash
# Clone repository
git clone <repository-url>
cd idrm-web

# Install frontend dependencies
cd frontend
bun install

# Install API gateway dependencies
cd ../backend/api-gateway
bun install

# Install Python service dependencies
cd ../services/service-management
poetry install

# Setup database
docker-compose up -d postgres redis geoserver

# Run migrations
cd backend/services/service-management
alembic upgrade head
```

## Development

```bash
# Terminal 1: Frontend dev server
cd frontend
bun run dev

# Terminal 2: API Gateway
cd backend/api-gateway
bun run --watch src/index.js

# Terminal 3: Python service
cd backend/services/service-management
poetry run uvicorn app.main:app --reload
```

## Production Build

```bash
# Build frontend
cd frontend
bun run build

# Start all services
docker-compose up -d
```

---

# Security Checklist

- ✅ HTTPS only in production
- ✅ JWT token authentication
- ✅ Token stored in localStorage (httpOnly cookies for enhanced security)
- ✅ CORS configured properly
- ✅ Rate limiting on API Gateway
- ✅ Input validation on client and server
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (sanitize user inputs)
- ✅ CSRF tokens for state-changing operations
- ✅ Content Security Policy headers
- ✅ Redis session expiry
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Audit logging for sensitive operations

---

**This specification covers the complete web-only IDRM platform using Bun for frontend tooling and Python for backend services.**
