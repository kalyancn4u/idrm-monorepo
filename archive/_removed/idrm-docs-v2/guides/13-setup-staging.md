> *Type: Guide (novice / how-to) · Audience: DevOps · Status: Archived — v2 historical generation*

# IDRM Staging Environment Setup v2.0

<!-- IDRM-CLEANUP doc=v2-g13-staging status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — staging = FFP
> Separate staging environments are **FFP** (multi-env CI/CD) → [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md).
> MVP = single native Ubuntu server (ADR-006). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Docker-Based Deployment with Python Geospatial Service

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Environment**: Staging (Pre-Production)  
**Stack**: Python Geospatial (NO Java GeoServer) + Bun + Docker

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Installation Steps](#installation-steps)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [Verification](#verification)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### What is Staging?

Staging is a **production-like environment** for:
- Testing new features before production
- QA and integration testing
- Performance testing
- Client demos
- Pre-deployment validation

### Key Differences from v1.0

**REMOVED** ❌:
- Java GeoServer (kartoza/geoserver Docker image)
- Node.js backend
- Python venv

**ADDED** ✅:
- Python Geospatial Service (FastAPI)
- Bun API Gateway
- Miniconda-based Python containers
- 7-service architecture

### Time Estimate

- **Fresh Install**: 1-2 hours
- **Existing System Update**: 30-45 minutes

---

## ✅ Prerequisites

### Hardware Requirements

```
CPU:    8 cores minimum
RAM:    16-32 GB
Storage: 200 GB SSD
Network: 100 Mbps minimum
```

### Software Requirements

- [ ] Ubuntu 22.04/24.04 LTS
- [ ] Docker 24.0+
- [ ] Docker Compose 2.20+
- [ ] Git 2.34+
- [ ] 200GB free disk space

### Verify Prerequisites

```bash
# Check OS
lsb_release -a
# Should show: Ubuntu 22.04 or 24.04

# Check Docker
docker --version
# Should show: Docker version 24.x or higher

# Check Docker Compose
docker compose version
# Should show: Docker Compose version v2.20.x or higher

# Check disk space
df -h
# Should show: 200GB+ available

# Check Docker daemon
sudo systemctl status docker
# Should show: active (running)
```

---

## 🏗️ Architecture

### Service Overview

```
┌─────────────────────────────────────────────────┐
│              NGINX (Port 80/443)                │
│         Reverse Proxy + Static Files            │
└─────────────────┬───────────────────────────────┘
                  ↓
        ┌─────────┴─────────┐
        ↓                   ↓
┌──────────────────┐  ┌──────────────────────┐
│  Bun API Gateway │  │ Python Geospatial    │
│   (Port 3000)    │  │   Service (8002)     │
│                  │  │   [REPLACES GEOSERVER]│
└────────┬─────────┘  └──────────────────────┘
         ↓
┌────────────────────────────────────────────────┐
│         Python Microservices (FastAPI)         │
│  Port 8000: Auth                               │
│  Port 8001: Service Management                 │
│  Port 8003: Analytics                          │
│  Port 8004: Notifications                      │
└───────────────┬────────────────────────────────┘
                ↓
        ┌───────┴────────┐
        ↓                ↓
┌──────────────┐  ┌──────────────────┐
│  PostgreSQL  │  │     Redis        │
│  + PostGIS   │  │     Cache        │
│  (Port 5432) │  │   (Port 6379)    │
└──────────────┘  └──────────────────┘
```

### Container List

| Container | Image | Purpose | Port |
|-----------|-------|---------|------|
| nginx | nginx:1.24-alpine | Reverse proxy | 80, 443 |
| api-gateway | custom (Bun) | API routing | 3000 |
| geospatial-service | custom (Python) | Map tiles, GeoJSON | 8002 |
| auth-service | custom (Python) | Authentication | 8000 |
| service-mgmt | custom (Python) | Service CRUD | 8001 |
| analytics | custom (Python) | Analytics | 8003 |
| notifications | custom (Python) | Notifications | 8004 |
| postgres | postgis/postgis:16-3.4 | Database | 5432 |
| redis | redis:7.2-alpine | Cache | 6379 |

**Total**: 9 containers

---

## 📦 Installation Steps

### Step 1: Prepare the Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker (if not already installed)
curl -fsSL https://get.docker.com | sh

# Install Docker Compose plugin
sudo apt install -y docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Verify
docker --version
docker compose version
```

---

### Step 2: Clone Repository

```bash
# Clone IDRM repository
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp

# Checkout staging branch
git checkout staging

# Verify directory structure
ls -la
# Should show: backend/, frontend/, docker-compose.staging.yml, etc.
```

---

### Step 3: Project Structure

Ensure your project has this structure:

```
idrm-mvp/
├── backend/
│   ├── services/
│   │   ├── auth/
│   │   │   ├── Dockerfile
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   └── ...
│   │   ├── service_mgmt/
│   │   │   ├── Dockerfile
│   │   │   └── ...
│   │   ├── geospatial/          # ⭐ NEW - Replaces GeoServer
│   │   │   ├── Dockerfile
│   │   │   ├── main.py
│   │   │   ├── requirements.txt
│   │   │   ├── tiles.py
│   │   │   └── ...
│   │   ├── analytics/
│   │   └── notifications/
│   └── database/
│       └── init/
│           └── 01_schema.sql
├── frontend/
│   ├── html-tailwind/           # Primary frontend
│   ├── react-spa/               # Secondary frontend
│   ├── Dockerfile.bun
│   └── ...
├── nginx/
│   └── staging.conf
├── docker-compose.staging.yml
├── .env.staging.example
└── README.md
```

---

## ⚙️ Configuration

### Step 4: Create Environment File

```bash
# Copy example environment file
cp .env.staging.example .env.staging

# Generate secure passwords
openssl rand -base64 32  # For database
openssl rand -base64 32  # For Redis
openssl rand -hex 64     # For JWT secret

# Edit environment file
nano .env.staging
```

**Environment Variables** (`.env.staging`):

```bash
# ============================================
# IDRM Staging Environment
# ============================================

# ------------------
# PostgreSQL + PostGIS
# ------------------
POSTGRES_DB=idrm_staging
POSTGRES_USER=idrm_staging_user
POSTGRES_PASSWORD=REPLACE_WITH_SECURE_PASSWORD_32_CHARS

# Database URLs
DATABASE_URL=postgresql+asyncpg://idrm_staging_user:REPLACE_WITH_SECURE_PASSWORD_32_CHARS@postgres:5432/idrm_staging
DATABASE_URL_SYNC=postgresql://idrm_staging_user:REPLACE_WITH_SECURE_PASSWORD_32_CHARS@postgres:5432/idrm_staging

# ------------------
# Redis
# ------------------
REDIS_PASSWORD=REPLACE_WITH_SECURE_PASSWORD_32_CHARS
REDIS_URL=redis://:REPLACE_WITH_SECURE_PASSWORD_32_CHARS@redis:6379/0

# ------------------
# JWT Authentication
# ------------------
JWT_SECRET_KEY=REPLACE_WITH_HEX_64_CHARS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ------------------
# Service Ports
# ------------------
AUTH_SERVICE_PORT=8000
SERVICE_MGMT_PORT=8001
GEOSPATIAL_SERVICE_PORT=8002
ANALYTICS_SERVICE_PORT=8003
NOTIFICATION_SERVICE_PORT=8004
API_GATEWAY_PORT=3000

# ------------------
# Geospatial Service
# ------------------
TILE_CACHE_DIR=/var/cache/tiles
MAX_TILE_CACHE_SIZE_MB=1000
ENABLE_TILE_CACHING=true

# ------------------
# Environment
# ------------------
ENVIRONMENT=staging
DEBUG=False
LOG_LEVEL=INFO

# ------------------
# CORS (for frontend)
# ------------------
ALLOWED_ORIGINS=https://staging.yourdomain.com,http://localhost:5173
```

---

### Step 5: Docker Compose File

**docker-compose.staging.yml**:

```yaml
version: '3.8'

services:
  # ==========================================
  # PostgreSQL + PostGIS
  # ==========================================
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres-staging
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./backend/database/init:/docker-entrypoint-initdb.d:ro
    networks:
      - idrm-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  # ==========================================
  # Redis Cache
  # ==========================================
  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis-staging
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
      --appendfsync everysec
    volumes:
      - redis-data:/data
    networks:
      - idrm-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # ==========================================
  # Python Geospatial Service
  # ⭐ REPLACES Java GeoServer
  # ==========================================
  geospatial-service:
    build:
      context: ./backend/services/geospatial
      dockerfile: Dockerfile
    container_name: idrm-geospatial-staging
    environment:
      DATABASE_URL: ${DATABASE_URL_SYNC}
      REDIS_URL: ${REDIS_URL}
      PORT: ${GEOSPATIAL_SERVICE_PORT}
      TILE_CACHE_DIR: ${TILE_CACHE_DIR}
      MAX_TILE_CACHE_SIZE_MB: ${MAX_TILE_CACHE_SIZE_MB}
      LOG_LEVEL: ${LOG_LEVEL}
    volumes:
      - tile-cache:/var/cache/tiles
      - ./backend/services/geospatial:/app:ro
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G

  # ==========================================
  # Auth Service (Python/FastAPI)
  # ==========================================
  auth-service:
    build:
      context: ./backend/services/auth
      dockerfile: Dockerfile
    container_name: idrm-auth-staging
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      JWT_ALGORITHM: ${JWT_ALGORITHM}
      ACCESS_TOKEN_EXPIRE_MINUTES: ${ACCESS_TOKEN_EXPIRE_MINUTES}
      PORT: ${AUTH_SERVICE_PORT}
      LOG_LEVEL: ${LOG_LEVEL}
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3

  # ==========================================
  # Service Management (Python/FastAPI)
  # ==========================================
  service-mgmt:
    build:
      context: ./backend/services/service_mgmt
      dockerfile: Dockerfile
    container_name: idrm-service-mgmt-staging
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      PORT: ${SERVICE_MGMT_PORT}
      LOG_LEVEL: ${LOG_LEVEL}
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 15s
      timeout: 5s
      retries: 3

  # ==========================================
  # Analytics Service (Python/FastAPI)
  # ==========================================
  analytics:
    build:
      context: ./backend/services/analytics
      dockerfile: Dockerfile
    container_name: idrm-analytics-staging
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      PORT: ${ANALYTICS_SERVICE_PORT}
      LOG_LEVEL: ${LOG_LEVEL}
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped

  # ==========================================
  # Notification Service (Python/FastAPI)
  # ==========================================
  notifications:
    build:
      context: ./backend/services/notifications
      dockerfile: Dockerfile
    container_name: idrm-notifications-staging
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      PORT: ${NOTIFICATION_SERVICE_PORT}
      LOG_LEVEL: ${LOG_LEVEL}
    networks:
      - idrm-network
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  # ==========================================
  # Bun API Gateway
  # ==========================================
  api-gateway:
    build:
      context: ./frontend
      dockerfile: Dockerfile.bun
      args:
        BUN_VERSION: 1.0.0
    container_name: idrm-api-gateway-staging
    environment:
      PORT: ${API_GATEWAY_PORT}
      AUTH_SERVICE_URL: http://auth-service:8000
      SERVICE_MGMT_URL: http://service-mgmt:8001
      GEOSPATIAL_URL: http://geospatial-service:8002
      ANALYTICS_URL: http://analytics:8003
      NOTIFICATION_URL: http://notifications:8004
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
      LOG_LEVEL: ${LOG_LEVEL}
    networks:
      - idrm-network
    depends_on:
      - auth-service
      - service-mgmt
      - geospatial-service
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # ==========================================
  # NGINX Reverse Proxy
  # ==========================================
  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx-staging
    volumes:
      - ./nginx/staging.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/html-tailwind/dist:/usr/share/nginx/html:ro
      - nginx-logs:/var/log/nginx
      - nginx-cache:/var/cache/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - idrm-network
    depends_on:
      - api-gateway
      - geospatial-service
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 256M

volumes:
  postgres-data:
    driver: local
  redis-data:
    driver: local
  tile-cache:
    driver: local
  nginx-logs:
    driver: local
  nginx-cache:
    driver: local

networks:
  idrm-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16
```

---

### Step 6: NGINX Configuration

**nginx/staging.conf**:

```nginx
# Upstream definitions
upstream api_gateway {
    least_conn;
    server api-gateway:3000 max_fails=3 fail_timeout=30s;
}

upstream geospatial_service {
    server geospatial-service:8002 max_fails=3 fail_timeout=30s;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=20r/m;
limit_req_zone $binary_remote_addr zone=geo_limit:10m rate=500r/m;

# Cache for tiles
proxy_cache_path /var/cache/nginx/tiles levels=1:2 keys_zone=tile_cache:10m max_size=1g inactive=7d use_temp_path=off;

server {
    listen 80;
    server_name _;

    client_max_body_size 20M;
    client_body_timeout 30s;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Logging
    access_log /var/log/nginx/access.log combined;
    error_log /var/log/nginx/error.log warn;

    # API Gateway (authenticated endpoints)
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://api_gateway/;
        proxy_http_version 1.1;
        
        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        
        # Standard headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
        
        # Bypass cache
        proxy_cache_bypass $http_upgrade;
    }

    # Authentication endpoints (stricter rate limit)
    location /api/auth/ {
        limit_req zone=auth_limit burst=5 nodelay;
        
        proxy_pass http://api_gateway/auth/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Python Geospatial Service
    # ⭐ REPLACES /geoserver/ endpoint
    location /geo/ {
        limit_req zone=geo_limit burst=100 nodelay;
        
        proxy_pass http://geospatial_service/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Cache tiles
        proxy_cache tile_cache;
        proxy_cache_valid 200 1h;
        proxy_cache_valid 404 1m;
        proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
        proxy_cache_background_update on;
        proxy_cache_lock on;
        
        # Cache bypass for debugging
        proxy_cache_bypass $http_pragma $http_authorization;
        
        # Add cache status header
        add_header X-Cache-Status $upstream_cache_status;
    }

    # Static files (Frontend)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }

    # Health check endpoint
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

---

## 🚀 Deployment

### Step 7: Build Images

```bash
# Build all images
docker compose -f docker-compose.staging.yml build

# Or build specific service
docker compose -f docker-compose.staging.yml build geospatial-service

# Check built images
docker images | grep idrm
```

---

### Step 8: Start Services

```bash
# Start all services
docker compose -f docker-compose.staging.yml up -d

# View logs
docker compose -f docker-compose.staging.yml logs -f

# View specific service logs
docker compose -f docker-compose.staging.yml logs -f geospatial-service

# Check status
docker compose -f docker-compose.staging.yml ps
```

**Expected Output**:
```
NAME                        STATUS              PORTS
idrm-postgres-staging       Up (healthy)        5432/tcp
idrm-redis-staging          Up (healthy)        6379/tcp
idrm-geospatial-staging     Up (healthy)        8002/tcp
idrm-auth-staging           Up (healthy)        8000/tcp
idrm-service-mgmt-staging   Up (healthy)        8001/tcp
idrm-analytics-staging      Up                  8003/tcp
idrm-notifications-staging  Up                  8004/tcp
idrm-api-gateway-staging    Up (healthy)        3000/tcp
idrm-nginx-staging          Up (healthy)        0.0.0.0:80->80/tcp
```

---

### Step 9: Run Database Migrations

```bash
# Run Alembic migrations
docker compose -f docker-compose.staging.yml exec auth-service \
    alembic upgrade head

# Verify database schema
docker compose -f docker-compose.staging.yml exec postgres \
    psql -U idrm_staging_user -d idrm_staging -c "\dt"
```

---

## ✅ Verification

### Step 10: Health Checks

```bash
# Test NGINX
curl -I http://localhost
# Expected: HTTP/1.1 200 OK

# Test API Gateway
curl http://localhost/api/health
# Expected: {"status": "healthy"}

# Test Python Geospatial Service
curl http://localhost/geo/health
# Expected: {"status": "healthy", "service": "geospatial"}

# Test tile endpoint
curl -I http://localhost/geo/tiles/5/15/12.png
# Expected: HTTP/1.1 200 OK, Content-Type: image/png

# Test GeoJSON endpoint
curl http://localhost/geo/services.geojson
# Expected: {"type": "FeatureCollection", "features": [...]}
```

---

### Step 11: Verify All Services

**Comprehensive Test Script**:

```bash
#!/bin/bash
echo "=== IDRM Staging Verification ==="
echo ""

# PostgreSQL
echo "PostgreSQL:"
docker compose -f docker-compose.staging.yml exec postgres pg_isready -U idrm_staging_user
echo ""

# Redis
echo "Redis:"
docker compose -f docker-compose.staging.yml exec redis redis-cli -a $REDIS_PASSWORD ping
echo ""

# Python services
echo "Auth Service:"
curl -s http://localhost/api/health | jq .
echo ""

echo "Geospatial Service:"
curl -s http://localhost/geo/health | jq .
echo ""

echo "Container Status:"
docker compose -f docker-compose.staging.yml ps
echo ""

echo "=== Verification Complete ==="
```

**Save and run**:
```bash
chmod +x verify-staging.sh
./verify-staging.sh
```

---

## 🔧 Management Commands

### View Logs

```bash
# All services
docker compose -f docker-compose.staging.yml logs -f

# Specific service
docker compose -f docker-compose.staging.yml logs -f geospatial-service

# Last 100 lines
docker compose -f docker-compose.staging.yml logs --tail=100

# Follow with timestamps
docker compose -f docker-compose.staging.yml logs -f --timestamps
```

---

### Restart Services

```bash
# Restart all
docker compose -f docker-compose.staging.yml restart

# Restart specific service
docker compose -f docker-compose.staging.yml restart geospatial-service

# Restart with rebuild
docker compose -f docker-compose.staging.yml up -d --build geospatial-service
```

---

### Stop/Start

```bash
# Stop all
docker compose -f docker-compose.staging.yml stop

# Start all
docker compose -f docker-compose.staging.yml start

# Stop and remove
docker compose -f docker-compose.staging.yml down

# Stop and remove volumes (⚠️ destroys data)
docker compose -f docker-compose.staging.yml down -v
```

---

### Update Deployment

```bash
# Pull latest code
git pull origin staging

# Rebuild and restart
docker compose -f docker-compose.staging.yml up -d --build

# Run migrations
docker compose -f docker-compose.staging.yml exec auth-service \
    alembic upgrade head
```

---

## 🐛 Troubleshooting

### Issue 1: Geospatial Service Won't Start

**Symptom**:
```
Error: ModuleNotFoundError: No module named 'geopandas'
```

**Solution**:
```bash
# Check Dockerfile has correct dependencies
cat backend/services/geospatial/requirements.txt

# Rebuild with no cache
docker compose -f docker-compose.staging.yml build --no-cache geospatial-service

# Restart
docker compose -f docker-compose.staging.yml up -d geospatial-service
```

---

### Issue 2: Database Connection Failed

**Symptom**:
```
FATAL: password authentication failed for user "idrm_staging_user"
```

**Solution**:
```bash
# Check environment variables
docker compose -f docker-compose.staging.yml config

# Verify .env.staging has correct password
cat .env.staging | grep POSTGRES_PASSWORD

# Restart database
docker compose -f docker-compose.staging.yml restart postgres
```

---

### Issue 3: Tile Generation Fails

**Symptom**:
```
Error generating tile: GDAL not found
```

**Solution**:
```bash
# Check geospatial service logs
docker compose -f docker-compose.staging.yml logs geospatial-service

# Verify GDAL installation in container
docker compose -f docker-compose.staging.yml exec geospatial-service \
    python -c "from osgeo import gdal; print(gdal.__version__)"

# If missing, rebuild
docker compose -f docker-compose.staging.yml build --no-cache geospatial-service
```

---

### Issue 4: High Memory Usage

**Symptom**: Server runs out of memory

**Solution**:
```bash
# Check resource usage
docker stats

# Reduce memory limits in docker-compose.yml
# Example: Change postgres memory limit from 2G to 1G

# Restart with new limits
docker compose -f docker-compose.staging.yml up -d
```

---

### Issue 5: Port Already in Use

**Symptom**:
```
Error: bind: address already in use
```

**Solution**:
```bash
# Find process using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop apache2  # or nginx, etc.

# Or change port in docker-compose.yml
# ports:
#   - "8080:80"  # Use 8080 instead of 80
```

---

## 📊 Monitoring

### Container Stats

```bash
# Real-time stats
docker stats

# Specific container
docker stats idrm-geospatial-staging

# One-time snapshot
docker stats --no-stream
```

---

### Disk Usage

```bash
# Check Docker disk usage
docker system df

# Clean up unused images
docker image prune -a

# Clean up volumes (⚠️ careful!)
docker volume prune
```

---

## 🔄 Backup & Restore

### Backup Database

```bash
# Backup PostgreSQL
docker compose -f docker-compose.staging.yml exec postgres \
    pg_dump -U idrm_staging_user idrm_staging | gzip > backup_$(date +%Y%m%d).sql.gz

# Verify backup
ls -lh backup_*.sql.gz
```

---

### Restore Database

```bash
# Restore from backup
gunzip -c backup_20260510.sql.gz | \
    docker compose -f docker-compose.staging.yml exec -T postgres \
    psql -U idrm_staging_user -d idrm_staging
```

---

## 📝 Summary Checklist

### Pre-Deployment ✅
- [ ] Prerequisites met (Docker, 16GB RAM, 200GB storage)
- [ ] `.env.staging` created with secure passwords
- [ ] Project structure verified
- [ ] Docker Compose file reviewed
- [ ] NGINX configuration updated

### Deployment ✅
- [ ] Images built successfully
- [ ] All containers started
- [ ] Health checks passing
- [ ] Database migrations completed
- [ ] Verification tests passed

### Post-Deployment ✅
- [ ] API endpoints responding
- [ ] Geospatial tiles generating
- [ ] Frontend accessible
- [ ] Logs checked for errors
- [ ] Backup script configured

---

**Staging environment complete! Ready for testing! 🚀**

**Next Steps**: Configure CI/CD for automated deployments
