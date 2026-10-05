> *Type: Document (specification) · Audience: Product, developers · Status: Archived — v2 historical generation*

# IDRM MVP: Product Requirements Document v2.0

<!-- IDRM-CLEANUP doc=v2-10-prd status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — gen-2 PRD → canonical `docs/mvp/10`
> Aligns with the current MVP PRD. Canonical = [`../../../../docs/mvp/10-requirements-prd.md`](../../../../docs/mvp/10-requirements-prd.md);
> functional detail → `docs/mvp/11`; for section-level PRD mapping see the v0 Section Map
> [`../../idrm-docs-v0/docs/10-requirements-prd.md`](../../idrm-docs-v0/docs/10-requirements-prd.md). No unique MVP
> requirements. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Integrated Disaster Response Management Platform - Technical Specification

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Status**: Final Architecture - Ready for Implementation

---

## 📋 Executive Summary

The **Integrated Disaster Response Management (IDRM)** platform is a unified, map-driven, privacy-first digital system designed to enable timely, coordinated, and transparent disaster response across India. This document outlines the **final technical architecture** for the Minimum Viable Product (MVP) deployment.

### Key Changes from v1.0
- ✅ **Python-only backend** (removed Java GeoServer)
- ✅ **Miniconda** for Python environment management
- ✅ **Bun** as API Gateway (replaced Node.js)
- ✅ **Three frontend interfaces**: HTML/Tailwind (primary), React (web), React Native (mobile)
- ✅ **Python geospatial service** replacing Java GeoServer
- ✅ Simplified, consistent technology stack

---

## 1. Product Vision

IDRM serves as a **national-scale digital nervous system** for disaster response in India, connecting:
- Information flow (real-time updates)
- Logistics (resource tracking)
- People (service requests & providers)
- Accountability (transparent auditing)

**Analogy**: Like the human body with a neural network (information) and circulatory system (resources).

---

## 2. Core Problem Statement

Disaster response in India suffers from:
- ❌ Fragmented information across stakeholders
- ❌ Delayed coordination between agencies
- ❌ Limited transparency in resource allocation
- ❌ No unified digital coordination platform
- ❌ Privacy concerns for vulnerable populations
- ❌ Difficulty tracking service delivery and outcomes

**IDRM Solution**: One unified platform addressing all these challenges.

---

## 3. Technology Stack (FINAL)

### 3.1 Official MVP Stack

```
┌─────────────────────────────────────────────────┐
│         NGINX Reverse Proxy (Port 80/443)       │
│  SSL Termination | Rate Limiting | Load Balance │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌──────────────────┐      ┌──────────────────────┐
│  Bun API Gateway │      │ Python Microservices │
│   (Port 3000)    │◄────►│   (FastAPI + Conda)  │
│                  │      │                      │
│  - WebSockets    │      │  Port 8000: Auth     │
│  - JWT Routing   │      │  Port 8001: Services │
│  - CORS          │      │  Port 8002: Geo API  │
│  - Rate Limits   │      │  Port 8003: Analytics│
└──────────────────┘      │  Port 8004: Notify   │
        ↓                 └──────────────────────┘
        ↓                           ↓
┌──────────────────┐      ┌──────────────────────┐
│   Redis Cache    │      │ PostgreSQL + PostGIS │
│   (Port 6379)    │      │    (Port 5432)       │
│                  │      │                      │
│  - Sessions      │      │  - Service Requests  │
│  - JWT Blacklist │      │  - User Accounts     │
│  - Rate Limits   │      │  - Geospatial Data   │
│  - Pub/Sub       │      │  - Audit Logs        │
└──────────────────┘      └──────────────────────┘

Frontend Interfaces (Multi-Platform):
┌─────────────────┬─────────────────┬──────────────────┐
│ HTML/Tailwind   │ React SPA       │ React Native App │
│ (Primary Web)   │ (Advanced Web)  │ (iOS + Android)  │
│ Port 5173       │ Port 5174       │ Expo Dev         │
└─────────────────┴─────────────────┴──────────────────┘
```

### 3.2 Technology Rationale

| Technology | Version | Purpose | Why This Choice |
|------------|---------|---------|-----------------|
| **NGINX** | 1.24+ | Reverse proxy, SSL | Industry standard, high performance |
| **Bun** | 1.x | API Gateway, WebSocket | 3-4x faster than Node.js, built-in TS |
| **Python** | 3.11 | Backend microservices | Best for geospatial, data science |
| **Miniconda** | latest | Python env manager | Superior for geospatial libraries |
| **FastAPI** | 0.104+ | Web framework | Modern, fast, auto-docs |
| **PostgreSQL** | 16 | Primary database | ACID, reliability, performance |
| **PostGIS** | 3.4 | Spatial extension | Best-in-class geospatial DB |
| **Redis** | 7.2+ | Cache & sessions | Sub-ms latency, pub/sub |
| **GeoPandas** | 0.14+ | Geospatial processing | Python GeoServer replacement |
| **Tailwind CSS** | 3.x | Styling framework | Utility-first, responsive |
| **React** | 18.x | Web SPA (optional) | Component-based, rich UI |
| **React Native** | 0.72+ | Mobile apps | Cross-platform iOS/Android |

### 3.3 What We Removed (from v1.0)

- ❌ **Node.js** → Replaced with Bun (faster)
- ❌ **Java GeoServer** → Replaced with Python geospatial service
- ❌ **venv** → Replaced with Miniconda (better for geospatial)
- ❌ **Single frontend** → Expanded to three interfaces

---

## 4. System Architecture

### 4.1 Layered Architecture

```
┌─────────────────────────────────────────────────┐
│  Presentation Layer (Multi-Platform Clients)    │
│  ┌──────────────┬───────────────┬─────────────┐ │
│  │ HTML/Tailwind│  React SPA    │ React Native│ │
│  │ (Primary)    │  (Advanced)   │ (Mobile)    │ │
│  └──────────────┴───────────────┴─────────────┘ │
└─────────────────────────────────────────────────┘
                      ↓ HTTPS
┌─────────────────────────────────────────────────┐
│    NGINX (Reverse Proxy, WAF, Cache, SSL)       │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│       API Gateway Layer (Bun/Express-like)      │
│   WebSocket Server | JWT Auth | CORS | Routing │
└─────────────────────────────────────────────────┘
        ↓                    ↓
┌───────────────┐    ┌──────────────────────────┐
│  Redis Cache  │    │  Python Geospatial API   │
│  (Sessions)   │    │  (Replaces GeoServer)    │
└───────────────┘    └──────────────────────────┘
        ↓                    ↓
┌─────────────────────────────────────────────────┐
│   Business Logic Layer (Python/FastAPI)         │
│  Auth | Service Mgmt | Analytics | Notifications│
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│     Data Layer (PostgreSQL + PostGIS)           │
│   Users | Services | Geospatial | Audit Logs   │
└─────────────────────────────────────────────────┘
```

### 4.2 Python Microservices Architecture

All services run in **Miniconda environment** (idrm-mvp):

```python
# Service architecture
backend/
├── services/
│   ├── auth/              # Port 8000
│   │   ├── main.py       # JWT, registration, login
│   │   ├── models.py     # User, Session
│   │   └── schemas.py    # Pydantic models
│   │
│   ├── service_mgmt/      # Port 8001
│   │   ├── main.py       # CRUD, matching, workflow
│   │   ├── models.py     # ServiceRequest, Provider
│   │   └── workflow.py   # State machine
│   │
│   ├── geospatial/        # Port 8002 ⭐ REPLACES GEOSERVER
│   │   ├── main.py       # Map tiles, GeoJSON, spatial queries
│   │   ├── tiles.py      # Raster tile generation
│   │   ├── vector.py     # Vector tile generation
│   │   └── queries.py    # ST_DWithin, clustering
│   │
│   ├── analytics/         # Port 8003
│   │   ├── main.py       # Dashboards, reports
│   │   ├── metrics.py    # Data aggregation
│   │   └── export.py     # CSV, PDF generation
│   │
│   └── notifications/     # Port 8004
│       ├── main.py       # Email, SMS, push
│       ├── templates/    # Email templates
│       └── queue.py      # Message queue
```

---

## 5. Frontend Architecture (Three Interfaces)

### 5.1 Primary Interface: HTML/CSS/JS + Tailwind

**Purpose**: Main public-facing web interface  
**Technology**: Pure vanilla JavaScript + Tailwind CSS  
**Target Users**: General public, field workers

**Why Vanilla JS**:
- ✅ Lightweight (no build step in production)
- ✅ Fast initial load
- ✅ Works on low-end devices
- ✅ Easy to understand and maintain
- ✅ Progressive enhancement

**Structure**:
```
frontend/html-tailwind/
├── index.html              # Landing page
├── pages/
│   ├── login.html         # Authentication
│   ├── dashboard.html     # User dashboard
│   ├── map.html           # Main map interface
│   ├── service-request.html
│   ├── service-list.html
│   └── profile.html
├── css/
│   ├── tailwind.config.js # Tailwind configuration
│   └── custom.css         # Custom styles
├── js/
│   ├── app.js             # Main application
│   ├── api.js             # API client
│   ├── map.js             # Leaflet integration
│   ├── auth.js            # Authentication
│   └── utils.js           # Utilities
└── assets/
    ├── icons/
    └── images/
```

**Key Libraries**:
```html
<!-- Tailwind CSS for styling -->
<script src="https://cdn.tailwindcss.com"></script>

<!-- Leaflet for maps -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Optional: Alpine.js for reactivity (lightweight) -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
```

**Example Page Structure**:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDRM - Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body class="bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-blue-600 text-white p-4">
        <div class="container mx-auto">
            <h1 class="text-2xl font-bold">IDRM Platform</h1>
        </div>
    </nav>

    <!-- Main Content -->
    <main class="container mx-auto p-4">
        <div id="map" class="h-96 rounded-lg shadow-lg"></div>
    </main>

    <script src="/js/api.js"></script>
    <script src="/js/map.js"></script>
    <script src="/js/app.js"></script>
</body>
</html>
```

---

### 5.2 Secondary Interface: React SPA

**Purpose**: Advanced web interface with rich interactions  
**Technology**: React 18 + Vite + Tailwind CSS  
**Target Users**: Admin users, analysts, power users

**Why React**:
- ✅ Rich component ecosystem
- ✅ Complex state management
- ✅ Advanced data visualization
- ✅ Better for admin dashboards
- ✅ TypeScript support

**Structure**:
```
frontend/react-spa/
├── src/
│   ├── components/
│   │   ├── Map/
│   │   │   ├── MapContainer.tsx
│   │   │   ├── ServiceMarker.tsx
│   │   │   └── MapFilters.tsx
│   │   ├── Dashboard/
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── StatsCard.tsx
│   │   │   └── Chart.tsx
│   │   ├── Services/
│   │   │   ├── ServiceList.tsx
│   │   │   ├── ServiceForm.tsx
│   │   │   └── ServiceDetail.tsx
│   │   └── common/
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       └── Modal.tsx
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── MapView.tsx
│   │   ├── Analytics.tsx
│   │   └── Admin.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useServices.ts
│   │   └── useWebSocket.ts
│   ├── services/
│   │   ├── api.ts            # API client
│   │   ├── auth.ts           # Authentication
│   │   └── websocket.ts      # WebSocket client
│   ├── store/
│   │   ├── authSlice.ts      # Redux/Zustand
│   │   └── servicesSlice.ts
│   ├── App.tsx
│   └── main.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

**Tech Stack**:
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "react-leaflet": "^4.2.1",
    "zustand": "^4.4.7",
    "axios": "^1.6.2",
    "recharts": "^2.10.0",
    "@headlessui/react": "^1.7.17"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.16"
  }
}
```

---

### 5.3 Tertiary Interface: React Native Mobile App

**Purpose**: Native mobile experience for iOS and Android  
**Technology**: React Native + Expo + NativeWind (Tailwind for RN)  
**Target Users**: Field workers, emergency responders

**Why React Native**:
- ✅ Single codebase for iOS & Android
- ✅ Native performance
- ✅ Access to device features (GPS, camera, notifications)
- ✅ Offline capabilities
- ✅ Push notifications

**Structure**:
```
frontend/mobile-app/
├── app/
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/
│   │   ├── index.tsx         # Dashboard
│   │   ├── map.tsx           # Map view
│   │   ├── services.tsx      # Service list
│   │   └── profile.tsx
│   └── service/
│       ├── [id].tsx          # Service detail
│       └── create.tsx        # Create service
├── components/
│   ├── Map/
│   │   ├── MapView.tsx       # react-native-maps
│   │   └── ServiceMarker.tsx
│   ├── Services/
│   │   ├── ServiceCard.tsx
│   │   └── ServiceForm.tsx
│   └── common/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── Card.tsx
├── hooks/
│   ├── useLocation.ts        # GPS tracking
│   ├── useNotifications.ts   # Push notifications
│   └── useOfflineSync.ts     # Offline data sync
├── services/
│   ├── api.ts
│   ├── storage.ts            # AsyncStorage
│   └── location.ts           # Expo Location
├── app.json
├── package.json
└── tailwind.config.js
```

**Tech Stack**:
```json
{
  "dependencies": {
    "expo": "~49.0.0",
    "react-native": "0.72.6",
    "react-native-maps": "^1.8.0",
    "expo-location": "~16.1.0",
    "expo-notifications": "~0.20.0",
    "expo-camera": "~13.4.0",
    "@react-navigation/native": "^6.1.9",
    "nativewind": "^2.0.11",
    "zustand": "^4.4.7",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "tailwindcss": "^3.3.0"
  }
}
```

**Native Features**:
```typescript
// GPS Location
import * as Location from 'expo-location';

const getLocation = async () => {
  let { status } = await Location.requestForegroundPermissionsAsync();
  if (status !== 'granted') return;
  
  let location = await Location.getCurrentPositionAsync({});
  return location.coords;
};

// Push Notifications
import * as Notifications from 'expo-notifications';

const sendNotification = async (title: string, body: string) => {
  await Notifications.scheduleNotificationAsync({
    content: { title, body },
    trigger: null,
  });
};

// Camera for Evidence
import { Camera } from 'expo-camera';

const takePhoto = async () => {
  const photo = await camera.takePictureAsync();
  return photo.uri;
};
```

---

## 6. Python Geospatial Service (Replaces Java GeoServer)

### 6.1 Service Overview

**Port**: 8002  
**Purpose**: Serve map tiles and geospatial data from PostGIS  
**Replaces**: Java GeoServer (kartoza/geoserver Docker image)

### 6.2 Core Libraries

```python
# requirements.txt (geospatial service)
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Geospatial core
geopandas==0.14.1          # GeoDataFrames
shapely==2.0.2             # Geometric operations
fiona==1.9.5               # Vector I/O
pyproj==3.6.1              # Coordinate transforms
rasterio==1.3.9            # Raster operations (optional)

# Database
sqlalchemy==2.0.23
geoalchemy2==0.14.2
psycopg2-binary==2.9.9
asyncpg==0.29.0

# Map tiles
mercantile==1.2.1          # Web mercator utilities
mapbox-vector-tile==2.0.1  # MVT encoding
Pillow==10.1.0             # Image generation

# Caching
redis==5.0.1
```

### 6.3 Installation (Miniconda)

```bash
# Create environment
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

# Install geospatial via conda (better dependency resolution)
conda install -c conda-forge -y \
    geopandas \
    shapely \
    fiona \
    pyproj \
    rasterio \
    gdal

# Install FastAPI and database via pip
pip install fastapi uvicorn sqlalchemy geoalchemy2 asyncpg \
    psycopg2-binary redis pillow mercantile mapbox-vector-tile
```

### 6.4 API Endpoints

```python
# Geospatial Service API (Port 8002)

# Map Tiles (WMS-like)
GET /tiles/{z}/{x}/{y}.png          # Raster tiles (256x256)
GET /vector-tiles/{z}/{x}/{y}.mvt   # Vector tiles (Mapbox)

# Feature Serving (WFS-like)
GET /services.geojson               # All services as GeoJSON
GET /services/{id}.geojson          # Single service
GET /boundaries.geojson             # Admin boundaries

# Spatial Queries
POST /nearby                        # Find services near point
POST /within                        # Find services in polygon
POST /cluster                       # K-means clustering
POST /heatmap                       # Density heatmap data

# Styling
GET /style/services.json            # Mapbox GL style spec

# Health
GET /health                         # Service health check
```

### 6.5 Implementation Example

```python
# backend/services/geospatial/main.py
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import geopandas as gpd
from sqlalchemy import create_engine, text
import mercantile
from PIL import Image, ImageDraw
from io import BytesIO
import os

app = FastAPI(title="IDRM Geospatial Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL_SYNC")
engine = create_engine(DATABASE_URL)

@app.get("/tiles/{z}/{x}/{y}.png")
async def get_raster_tile(z: int, x: int, y: int):
    """
    Generate raster tile with service markers
    Replaces GeoServer WMS
    """
    bounds = mercantile.bounds(x, y, z)
    
    # Query PostGIS for features in tile
    query = text(f"""
        SELECT 
            id,
            service_type,
            priority,
            ST_X(location) as lng,
            ST_Y(location) as lat
        FROM service_requests
        WHERE location && ST_MakeEnvelope(
            {bounds.west}, {bounds.south},
            {bounds.east}, {bounds.north}, 4326
        )
        LIMIT 1000
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    
    # Create image
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw each service
    for row in results:
        px, py = latlng_to_pixel(row.lat, row.lng, z, x, y)
        color = get_priority_color(row.priority)
        draw.ellipse([px-5, py-5, px+5, py+5], fill=color)
    
    # Return PNG
    buf = BytesIO()
    img.save(buf, format='PNG')
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/services.geojson")
async def get_services_geojson():
    """
    Return services as GeoJSON
    Replaces GeoServer WFS
    """
    gdf = gpd.read_postgis(
        "SELECT * FROM service_requests",
        engine,
        geom_col='location'
    )
    return Response(
        content=gdf.to_json(),
        media_type="application/json"
    )

@app.post("/nearby")
async def find_nearby(lat: float, lng: float, radius_km: float = 5.0):
    """Spatial query: find services near point"""
    query = text(f"""
        SELECT 
            id, service_type, priority, status,
            ST_Distance(
                location::geography,
                ST_MakePoint({lng}, {lat})::geography
            ) / 1000 as distance_km,
            ST_AsGeoJSON(location)::json as geometry
        FROM service_requests
        WHERE ST_DWithin(
            location::geography,
            ST_MakePoint({lng}, {lat})::geography,
            {radius_km * 1000}
        )
        ORDER BY distance_km
        LIMIT 100
    """)
    
    with engine.connect() as conn:
        results = conn.execute(query).fetchall()
    
    features = [{
        "type": "Feature",
        "geometry": row.geometry,
        "properties": {
            "id": str(row.id),
            "service_type": row.service_type,
            "priority": row.priority,
            "status": row.status,
            "distance_km": round(row.distance_km, 2)
        }
    } for row in results]
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def latlng_to_pixel(lat, lng, zoom, tile_x, tile_y):
    """Convert lat/lng to pixel coordinates in tile"""
    import math
    scale = 1 << zoom
    world_x = (lng + 180.0) / 360.0 * scale
    world_y = (1.0 - math.log(math.tan(math.radians(lat)) + 
               1.0 / math.cos(math.radians(lat))) / math.pi) / 2.0 * scale
    pixel_x = (world_x - tile_x) * 256
    pixel_y = (world_y - tile_y) * 256
    return int(pixel_x), int(pixel_y)

def get_priority_color(priority):
    """Map priority to RGB color"""
    colors = {
        'CRITICAL': (220, 38, 38),   # red
        'HIGH': (234, 88, 12),       # orange
        'MEDIUM': (245, 158, 11),    # yellow
        'LOW': (59, 130, 246)        # blue
    }
    return colors.get(priority, (156, 163, 175))
```

---

## 7. Database Schema

### 7.1 Core Tables

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ENUM types
CREATE TYPE service_type AS ENUM (
    'MEDICAL', 'FOOD', 'SHELTER', 'RESCUE', 
    'WATER', 'TRANSPORT', 'SUPPLIES', 'OTHER'
);

CREATE TYPE priority_level AS ENUM (
    'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
);

CREATE TYPE service_status AS ENUM (
    'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED',
    'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'CANCELLED'
);

CREATE TYPE privacy_level AS ENUM (
    'PUBLIC', 'PROTECTED', 'PRIVATE'
);

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    organization_id UUID REFERENCES organizations(id),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    registration_number VARCHAR(100),
    address TEXT,
    location GEOMETRY(Point, 4326),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_organizations_location ON organizations USING GIST(location);

-- Service requests table
CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    requestor_id UUID REFERENCES users(id),
    service_type service_type NOT NULL,
    priority priority_level NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    address TEXT,
    description TEXT,
    privacy_level privacy_level DEFAULT 'PUBLIC',
    status service_status DEFAULT 'SUBMITTED',
    assigned_to UUID REFERENCES users(id),
    disaster_event_id UUID REFERENCES disaster_events(id),
    estimated_completion TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_type ON service_requests(service_type);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);
CREATE INDEX idx_service_requests_event ON service_requests(disaster_event_id);

-- Disaster events table
CREATE TABLE disaster_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20),
    affected_area GEOMETRY(Polygon, 4326),
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'ACTIVE',
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disaster_events_area ON disaster_events USING GIST(affected_area);

-- Service providers table
CREATE TABLE service_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    organization_id UUID REFERENCES organizations(id),
    service_types service_type[],
    coverage_area GEOMETRY(Polygon, 4326),
    capacity INTEGER,
    current_load INTEGER DEFAULT 0,
    is_available BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_service_providers_coverage ON service_providers USING GIST(coverage_area);
CREATE INDEX idx_service_providers_types ON service_providers USING GIN(service_types);

-- Donations table
CREATE TABLE donations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    donor_id UUID REFERENCES users(id),
    amount DECIMAL(15,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    purpose TEXT,
    disaster_event_id UUID REFERENCES disaster_events(id),
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_donations_event ON donations(disaster_event_id);
CREATE INDEX idx_donations_status ON donations(status);

-- Audit logs table
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);
```

---

## 8. API Design

### 8.1 RESTful Endpoints

**Base URL**: `https://api.idrm.gov.in/v1`

```
# Authentication (Auth Service - Port 8000)
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
POST   /auth/logout
POST   /auth/verify-email
POST   /auth/forgot-password
POST   /auth/reset-password

# Users
GET    /users/me
PUT    /users/me
GET    /users/:id
GET    /users
POST   /users
PUT    /users/:id
DELETE /users/:id

# Service Requests (Service Mgmt - Port 8001)
POST   /services
GET    /services
GET    /services/:id
PUT    /services/:id
DELETE /services/:id
POST   /services/:id/assign
PUT    /services/:id/status
GET    /services/nearby
POST   /services/:id/verify

# Organizations
POST   /organizations
GET    /organizations
GET    /organizations/:id
PUT    /organizations/:id
POST   /organizations/:id/verify

# Disaster Events
POST   /events
GET    /events
GET    /events/:id
PUT    /events/:id
GET    /events/:id/services
GET    /events/:id/analytics

# Donations
POST   /donations
GET    /donations
GET    /donations/:id
GET    /donations/summary
POST   /donations/:id/allocate

# Analytics (Analytics Service - Port 8003)
GET    /analytics/dashboard
GET    /analytics/services
GET    /analytics/financial
GET    /analytics/geographic
POST   /analytics/report

# Geospatial (Geo Service - Port 8002)
GET    /geo/tiles/{z}/{x}/{y}.png
GET    /geo/vector-tiles/{z}/{x}/{y}.mvt
GET    /geo/services.geojson
POST   /geo/nearby
POST   /geo/within
POST   /geo/cluster
GET    /geo/style/{layer}.json
```

---

## 9. Deployment Architecture

### 9.1 Development Environment

**Setup**: Native Ubuntu installation (no Docker)

```
Hardware:
- CPU: 4-8 cores
- RAM: 8-16 GB
- Disk: 100 GB SSD

Services (Native):
├── PostgreSQL 16 + PostGIS 3.4 (systemd)
├── Redis 7.2 (systemd)
├── NGINX 1.24 (systemd)
├── Bun 1.x (binary)
└── Python 3.11 (Miniconda: idrm-mvp)
    ├── Auth Service (Port 8000)
    ├── Service Mgmt (Port 8001)
    ├── Geospatial Service (Port 8002)
    ├── Analytics (Port 8003)
    └── Notifications (Port 8004)

Frontends (Development Servers):
├── HTML/Tailwind (Vite - Port 5173)
├── React SPA (Vite - Port 5174)
└── React Native (Expo)
```

### 9.2 Production Environment

**Setup**: Docker Compose on dedicated server

```
Hardware:
- CPU: 16+ cores
- RAM: 32-64 GB
- Disk: 500 GB SSD

Services (Docker):
├── nginx (reverse proxy + SSL)
├── api-gateway (Bun)
├── auth-service (Python/FastAPI)
├── service-mgmt (Python/FastAPI)
├── geospatial-service (Python/FastAPI)
├── analytics (Python/FastAPI)
├── notifications (Python/FastAPI)
├── redis (cache)
└── postgres (PostgreSQL + PostGIS)

Frontends (Static/SSR):
├── HTML/Tailwind (served by NGINX)
├── React SPA (built, served by NGINX)
└── React Native (published to app stores)
```

---

## 10. Security Implementation

### 10.1 Authentication Flow

```
1. User Login → Bun API Gateway
2. Gateway → Auth Service (Python)
3. Auth Service verifies credentials
4. Generate JWT (access + refresh tokens)
5. Store refresh token in Redis
6. Return tokens to client
7. Client includes access token in requests
8. Gateway validates JWT before routing
```

### 10.2 Security Measures

- **JWT**: Short-lived access tokens (15 min), longer refresh tokens (7 days)
- **Password**: Bcrypt hashing (cost 12)
- **HTTPS**: Enforced in production (TLS 1.3)
- **CORS**: Configured per environment
- **Rate Limiting**: Via Redis (100 req/min per user)
- **Input Validation**: Pydantic schemas
- **SQL Injection**: Parameterized queries
- **XSS**: Output encoding
- **CSRF**: Tokens for state-changing operations

---

## 11. Frontend Integration Examples

### 11.1 HTML/Tailwind Map Integration

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
</head>
<body class="bg-gray-50">
    <div id="map" class="h-screen"></div>
    
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Initialize map
        const map = L.map('map').setView([20.5937, 78.9629], 5);
        
        // Base layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        
        // IDRM tiles from Python geospatial service
        L.tileLayer('http://localhost/geo/tiles/{z}/{x}/{y}.png', {
            opacity: 0.7
        }).addTo(map);
        
        // Fetch and display services
        fetch('http://localhost/api/geo/services.geojson')
            .then(r => r.json())
            .then(data => {
                L.geoJSON(data, {
                    pointToLayer: (feature, latlng) => {
                        return L.circleMarker(latlng, {
                            radius: 8,
                            fillColor: getPriorityColor(feature.properties.priority),
                            color: '#fff',
                            weight: 2,
                            fillOpacity: 0.8
                        });
                    }
                }).addTo(map);
            });
        
        function getPriorityColor(priority) {
            const colors = {
                'CRITICAL': '#dc2626',
                'HIGH': '#ea580c',
                'MEDIUM': '#f59e0b',
                'LOW': '#3b82f6'
            };
            return colors[priority] || '#9ca3af';
        }
    </script>
</body>
</html>
```

### 11.2 React Map Component

```typescript
// MapView.tsx
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

export function MapView() {
    const [services, setServices] = useState(null);
    
    useEffect(() => {
        fetch('http://localhost/api/geo/services.geojson')
            .then(r => r.json())
            .then(setServices);
    }, []);
    
    return (
        <MapContainer 
            center={[20.5937, 78.9629]} 
            zoom={5}
            className="h-screen"
        >
            <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <TileLayer url="http://localhost/geo/tiles/{z}/{x}/{y}.png" opacity={0.7} />
            {services && <GeoJSON data={services} />}
        </MapContainer>
    );
}
```

### 11.3 React Native Map

```typescript
// MapScreen.tsx
import MapView, { Marker, PROVIDER_GOOGLE } from 'react-native-maps';
import { useEffect, useState } from 'react';

export function MapScreen() {
    const [services, setServices] = useState([]);
    
    useEffect(() => {
        fetch('http://api.idrm.gov.in/api/geo/services.geojson')
            .then(r => r.json())
            .then(data => {
                const markers = data.features.map(f => ({
                    id: f.properties.id,
                    latitude: f.geometry.coordinates[1],
                    longitude: f.geometry.coordinates[0],
                    priority: f.properties.priority
                }));
                setServices(markers);
            });
    }, []);
    
    return (
        <MapView
            provider={PROVIDER_GOOGLE}
            initialRegion={{
                latitude: 20.5937,
                longitude: 78.9629,
                latitudeDelta: 10,
                longitudeDelta: 10,
            }}
            className="flex-1"
        >
            {services.map(service => (
                <Marker
                    key={service.id}
                    coordinate={{
                        latitude: service.latitude,
                        longitude: service.longitude
                    }}
                    pinColor={getPriorityColor(service.priority)}
                />
            ))}
        </MapView>
    );
}
```

---

## 12. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)
- ✅ Setup development environment
- ✅ Database schema & migrations
- ✅ Auth service (JWT, registration, login)
- ✅ Geospatial service (tiles, GeoJSON)
- ✅ Basic HTML/Tailwind interface

### Phase 2: Core Features (Weeks 5-8)
- ✅ Service CRUD operations
- ✅ Service-provider matching
- ✅ Map integration (all 3 frontends)
- ✅ RBAC implementation
- ✅ Privacy controls

### Phase 3: Advanced Features (Weeks 9-12)
- ✅ Analytics service
- ✅ Notification system
- ✅ React SPA interface
- ✅ React Native mobile app
- ✅ Complete testing

### Phase 4: Production (Weeks 13-16)
- ✅ Docker deployment
- ✅ SSL/Security hardening
- ✅ CI/CD pipeline
- ✅ Monitoring & logging
- ✅ Beta launch

---

## 13. Success Metrics

### Technical Metrics
- API response time: < 300ms (p95)
- Map tile generation: < 100ms
- Database queries: < 50ms (p95)
- System uptime: 99.9%
- Test coverage: > 80%

### Business Metrics
- Users: 10,000+ (Month 6)
- Organizations: 500+ (Month 6)
- Service requests: 50,000+ (Month 6)
- Average response time: < 30 minutes
- Service completion rate: > 85%

---

## 14. Appendices

### A. Technology Comparison

| Aspect | v1.0 (Old) | v2.0 (Current) |
|--------|-----------|----------------|
| API Gateway | Node.js | **Bun** (3-4x faster) |
| Geospatial | Java GeoServer | **Python FastAPI** |
| Python Env | venv | **Miniconda** |
| Frontends | 1 (generic) | **3 (HTML/React/RN)** |
| Mobile | None | **React Native** |
| Deployment | Complex | **Simplified** |

### B. Resource Requirements

```
Development:
- 8-16 GB RAM
- 4-8 CPU cores
- 100 GB storage

Production:
- 32-64 GB RAM
- 16+ CPU cores
- 500 GB storage
```

### C. References

- FastAPI: https://fastapi.tiangolo.com
- PostGIS: https://postgis.net
- GeoPandas: https://geopandas.org
- Leaflet: https://leafletjs.com
- Bun: https://bun.sh
- React: https://react.dev
- React Native: https://reactnative.dev

---

**Document Version**: 2.0  
**Status**: Final - Ready for Implementation  
**Last Updated**: May 10, 2026  
**Classification**: Internal Use

---

**This is the OFFICIAL PRD v2.0 - All documentation must align with this specification.**
