> *Type: Document (specification) · Audience: Architects · Status: Archived — v2 historical generation*

# IDRM MVP: Final Corrected Architecture

<!-- IDRM-CLEANUP doc=v2-21-corrected status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — architecture variant → `docs/mvp/20`
> One of v2's several architecture drafts (see also `20-architecture-monolith`, `22-architecture-lightweight`,
> `23-...HLD`). Current source of truth = [`../../../../docs/mvp/20-architecture-system.md`](../../../../docs/mvp/20-architecture-system.md)
> + ADRs `docs/mvp/21`. MVP-aligned (native monolith). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Pure Python Stack (No Java GeoServer)

---

## ✅ **Official MVP Technology Stack**

### **Core Stack (FINAL)**

```
┌─────────────────────────────────────────────────┐
│              NGINX Reverse Proxy                 │
│  (Port 80/443 - Routes all incoming traffic)    │
└─────────────────────────────────────────────────┘
                      ↓
        ┌─────────────┴─────────────┐
        ↓                           ↓
┌──────────────────┐      ┌──────────────────────┐
│  Bun API Gateway │      │ Python Microservices │
│   (Port 3000)    │◄────►│   (FastAPI)          │
│                  │      │   - Auth Service     │
│  - WebSockets    │      │   - Service Mgmt     │
│  - Auth Routing  │      │   - Geospatial API   │
│  - Rate Limiting │      │   - Analytics        │
└──────────────────┘      │   - Notifications    │
        ↓                 └──────────────────────┘
        ↓                           ↓
┌──────────────────┐      ┌──────────────────────┐
│   Redis Cache    │      │ PostgreSQL + PostGIS │
│   (Port 6379)    │      │    (Port 5432)       │
│                  │      │                      │
│  - Sessions      │      │  - User Data         │
│  - Rate Limits   │      │  - Service Requests  │
│  - Pub/Sub       │      │  - Geospatial Data   │
└──────────────────┘      └──────────────────────┘
```

---

## 🎯 **Technology Breakdown**

### 1. **NGINX (Reverse Proxy)**
**Version**: 1.24+  
**Port**: 80 (HTTP), 443 (HTTPS)  
**Purpose**:
- Routes traffic to Bun or Python services
- SSL/TLS termination
- Static file serving
- Rate limiting
- Security headers
- Load balancing (future)

**Why**: Industry standard, high performance, security features

---

### 2. **Bun (API Gateway)**
**Version**: 1.x  
**Port**: 3000  
**Language**: TypeScript/JavaScript  
**Purpose**:
- API Gateway (routes to Python microservices)
- WebSocket server (real-time notifications)
- JWT token validation
- Request routing
- CORS handling
- Rate limiting (with Redis)

**Why**: 3-4x faster than Node.js, built-in TypeScript, WebSocket support

**NOT Used For**:
- ❌ Business logic (that's Python)
- ❌ Database operations (that's Python)
- ❌ Geospatial processing (that's Python)

---

### 3. **Python Microservices (Miniconda)**
**Version**: Python 3.11  
**Environment**: Miniconda (NOT venv)  
**Framework**: FastAPI  
**Ports**: 8000-8009 (one per service)

#### **Microservices Architecture**:

**A. Auth Service** (Port 8000)
- User registration/login
- JWT token generation
- Password hashing (bcrypt)
- Email verification

**B. Service Management** (Port 8001)
- Service CRUD operations
- Service-provider matching
- Workflow state machine
- Status updates

**C. Geospatial Service** (Port 8002) ⭐ **REPLACES JAVA GEOSERVER**
- Map tile serving (WMS-like)
- Vector tile generation
- Spatial queries (ST_DWithin, etc.)
- GeoJSON API
- Feature serving (WFS-like)
- Distance calculations
- Clustering

**D. Analytics Service** (Port 8003)
- Dashboard metrics
- Report generation
- Data aggregation
- Export functionality

**E. Notification Service** (Port 8004)
- Email notifications
- Push notifications (future)
- SMS integration (future)
- Template management

**Why Miniconda**: Better for geospatial libraries, easier dependency management, scientific computing ecosystem

---

### 4. **Redis Cache**
**Version**: 7.2+  
**Port**: 6379  
**Purpose**:
- Session storage
- JWT token blacklist
- Rate limiting counters
- Pub/Sub for notifications
- Caching frequently-accessed data

**Why**: Sub-millisecond latency, built for caching

---

### 5. **Python Geospatial Service** ⭐ **KEY CHANGE**
**Replaces**: Java GeoServer  
**Technology**: FastAPI + GeoPandas + Shapely  
**Purpose**: Serve map data from PostGIS

#### **Libraries Used**:
```python
# Core geospatial
geopandas==0.14.1      # Geospatial data frames
shapely==2.0.2         # Geometric operations
fiona==1.9.5           # Vector data I/O
rasterio==1.3.9        # Raster data (if needed)
pyproj==3.6.1          # Coordinate transformations

# Map tile generation
mercantile==1.2.1      # Web mercator tile utilities
mapbox-vector-tile==2.0.1  # Vector tile encoding

# FastAPI + Database
fastapi==0.104.1
geoalchemy2==0.14.2    # SQLAlchemy geospatial
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
```

#### **Endpoints Provided**:
```python
# WMS-like endpoints (map tiles)
GET /geo/tiles/{z}/{x}/{y}.png          # Raster tiles
GET /geo/vector-tiles/{z}/{x}/{y}.mvt   # Vector tiles

# WFS-like endpoints (features)
GET /geo/features                        # GeoJSON features
GET /geo/services                        # Service locations as GeoJSON
GET /geo/boundaries                      # Administrative boundaries

# Spatial queries
POST /geo/nearby                         # Find features near point
POST /geo/within                         # Find features within polygon
POST /geo/cluster                        # Cluster points

# Styling
GET /geo/style/{layer}.json             # Mapbox GL style
```

#### **Why Not Java GeoServer**:
- ❌ Requires Java runtime (extra dependency)
- ❌ Heavy resource usage (512MB-1GB)
- ❌ Complex configuration
- ❌ Overkill for MVP
- ✅ Python geospatial stack is sufficient
- ✅ Faster development (same language)
- ✅ Better integration with PostGIS
- ✅ Lighter resource footprint

---

### 6. **PostgreSQL + PostGIS**
**Version**: PostgreSQL 16, PostGIS 3.4  
**Port**: 5432  
**Purpose**:
- Primary database
- Geospatial data storage
- Spatial indexing (GIST)
- Spatial operations (ST_* functions)

**Key PostGIS Functions**:
```sql
-- Distance queries
ST_DWithin(location, point, radius)

-- Clustering
ST_ClusterKMeans(location, num_clusters)

-- GeoJSON export
ST_AsGeoJSON(location)

-- Bounding box
ST_MakeEnvelope(xmin, ymin, xmax, ymax, 4326)

-- Transform coordinates
ST_Transform(location, target_srid)
```

---

## 🏗️ **Service Architecture**

### **Request Flow**

```
1. User Request → NGINX (Port 80/443)
   ↓
2. NGINX → Routes based on path:
   - /api/auth/*     → Bun API Gateway → Auth Service (Python)
   - /api/services/* → Bun API Gateway → Service Mgmt (Python)
   - /api/geo/*      → Bun API Gateway → Geospatial Service (Python)
   - /api/analytics/* → Bun API Gateway → Analytics Service (Python)
   - /ws/*           → Bun WebSocket Server
   - /static/*       → NGINX (direct)
   ↓
3. Python Services → PostgreSQL + PostGIS
   ↓
4. Python Services → Redis (for caching)
   ↓
5. Response → Bun → NGINX → User
```

---

## 📦 **Development vs. Production**

### **Development (Native Installation)**
```
Services:
├── NGINX .............. Native (systemd)
├── Bun ................ Native binary
├── Python Services .... Miniconda environment
├── Redis .............. Native (systemd)
└── PostgreSQL+PostGIS . Native (systemd)

No Docker, No Java, All Python
```

### **Staging/Production (Docker)**
```
Services:
├── nginx .............. Docker container
├── api-gateway ........ Bun Docker container
├── auth-service ....... Python Docker container
├── service-mgmt ....... Python Docker container
├── geospatial-service . Python Docker container
├── analytics .......... Python Docker container
├── redis .............. Docker container
└── postgres ........... PostGIS Docker container

All Dockerized, No Java
```

---

## 🔧 **Python Environment Management**

### **Miniconda Setup (REQUIRED)**

```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# Create IDRM environment
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

# Install geospatial libraries (these work better with conda)
conda install -c conda-forge geopandas shapely fiona pyproj -y

# Install remaining via pip
pip install fastapi uvicorn sqlalchemy geoalchemy2 redis
```

**Why Miniconda over venv**:
- ✅ Better for geospatial libraries (GDAL, GEOS, PROJ)
- ✅ Handles binary dependencies automatically
- ✅ Scientific computing ecosystem
- ✅ Cross-platform consistency

---

## 🗺️ **Map Rendering Strategy**

### **Frontend (Leaflet)**
```javascript
// Leaflet map with Python-served tiles
const map = L.map('map');

// Base layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// IDRM data layer (from Python Geospatial Service)
L.tileLayer('/api/geo/tiles/{z}/{x}/{y}.png').addTo(map);

// Vector features (GeoJSON)
fetch('/api/geo/services')
  .then(r => r.json())
  .then(geojson => {
    L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 8,
          color: getPriorityColor(feature.properties.priority)
        });
      }
    }).addTo(map);
  });
```

### **Backend (Python Tile Generation)**
```python
# Python geospatial service
from fastapi import FastAPI
import geopandas as gpd
from sqlalchemy import create_engine
from io import BytesIO
from PIL import Image, ImageDraw

app = FastAPI()

@app.get("/geo/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    # Get tile bounds
    bounds = mercantile.bounds(x, y, z)
    
    # Query PostGIS for features in bounds
    engine = create_engine(DATABASE_URL)
    gdf = gpd.read_postgis(
        f"""
        SELECT * FROM service_requests 
        WHERE location && ST_MakeEnvelope(
            {bounds.west}, {bounds.south}, 
            {bounds.east}, {bounds.north}, 4326
        )
        """,
        engine,
        geom_col='location'
    )
    
    # Render to PNG tile
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    for idx, row in gdf.iterrows():
        # Convert lat/lng to pixel coordinates
        px, py = latlng_to_pixel(row.geometry.y, row.geometry.x, z, x, y)
        # Draw point
        draw.ellipse([px-5, py-5, px+5, py+5], fill='red')
    
    # Return PNG
    buf = BytesIO()
    img.save(buf, format='PNG')
    return Response(content=buf.getvalue(), media_type="image/png")
```

---

## 📊 **Resource Requirements**

### **Development Environment**
```
CPU:  4 cores (8 recommended)
RAM:  8 GB (16 GB recommended)
Disk: 100 GB SSD

Services Running:
- PostgreSQL: 200-500 MB
- Redis: 50-100 MB
- Python Services (5): 100 MB each = 500 MB
- Bun: 50 MB
- NGINX: 20 MB

Total: ~1.3 GB RAM
```

### **Production Environment**
```
CPU:  8 cores (16 recommended)
RAM:  32 GB (64 GB recommended)
Disk: 500 GB SSD

Services (Docker):
- PostgreSQL: 1-2 GB
- Redis: 256-512 MB
- Python Services (5): 256 MB each = 1.3 GB
- Bun: 128 MB
- NGINX: 64 MB

Total: ~3-4 GB RAM (with headroom)
```

---

## ✅ **Final MVP Stack Summary**

```
┌────────────────────────────────────────┐
│  Technology          Version   Purpose │
├────────────────────────────────────────┤
│  NGINX               1.24+     Proxy   │
│  Bun                 1.x       Gateway │
│  Python (Miniconda)  3.11      Backend │
│  FastAPI             0.104+    Web API │
│  PostgreSQL          16        Database│
│  PostGIS             3.4       Spatial │
│  Redis               7.2+      Cache   │
│  GeoPandas           0.14+     Geospatial│
│  Leaflet (Frontend)  1.9       Maps    │
└────────────────────────────────────────┘

NO Java, NO GeoServer, ALL Python
```

---

## 🚀 **Benefits of This Stack**

1. **Pure Python Backend**: Single language, easier development
2. **Lighter Weight**: No Java runtime, less memory
3. **Faster Development**: Same language for all services
4. **Better Integration**: Python ↔ PostGIS direct connection
5. **Modern Stack**: Bun + FastAPI = cutting-edge performance
6. **Scalable**: Microservices ready to scale independently

---

**This is the FINAL, CORRECTED architecture. All documents will follow this stack!**
