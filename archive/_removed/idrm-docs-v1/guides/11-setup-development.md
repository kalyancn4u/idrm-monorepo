> *Type: Guide (novice / how-to) · Audience: Developers · Status: Archived — v1 historical generation*

# IDRM Platform Setup - Development Environment (Monolith)

<!-- IDRM-CLEANUP doc=v1-g11-dev status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — dev setup → superseded (MVP)
> Current MVP dev setup = [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + the installer `../../../scripts/setup-idrm-ubuntu.sh`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

> Complete guide for setting up IDRM platform in development mode with manual installation (no Docker)

## 🎯 Goal

Set up a fully functional IDRM development environment on a single Ubuntu server with:
- All services installed directly (no containers)
- Optimal for learning, debugging, and local development
- Easy to restart and troubleshoot individual services

## ⚠️ Important Notes

- **DO NOT use this setup in production**
- Database and services are exposed without containerization
- Suitable for: Local development, learning, debugging
- Not suitable for: Production, public-facing deployments

## 📋 Prerequisites

Before starting, complete ALL steps in `setup-prerequisites.md`:
- ✅ Ubuntu 22.04+ installed
- ✅ Bun installed
- ✅ Python 3.11+ installed
- ✅ PostgreSQL 16 + PostGIS installed
- ✅ Redis installed
- ✅ NGINX installed
- ✅ Java 11 installed
- ✅ System updated

---

## Table of Contents

1. [Directory Structure](#directory-structure)
2. [Database Setup](#database-setup)
3. [GeoServer Setup](#geoserver-setup)
4. [Backend Services Setup](#backend-services-setup)
5. [API Gateway Setup](#api-gateway-setup)
6. [Frontend Setup](#frontend-setup)
7. [NGINX Configuration](#nginx-configuration)
8. [Service Management](#service-management)
9. [Verification](#verification)
10. [Troubleshooting](#troubleshooting)

---

## Directory Structure

### Create Project Directory

```bash
# Create main project directory
sudo mkdir -p /var/www/idrm
sudo chown -R $USER:$USER /var/www/idrm
cd /var/www/idrm

# Create subdirectories
mkdir -p {backend,frontend,infrastructure,logs,data}
mkdir -p backend/{api-gateway,services}
mkdir -p backend/services/{service-management,geospatial,analytics,financial,privacy}
mkdir -p infrastructure/{nginx,postgres,redis,geoserver}
mkdir -p logs/{api-gateway,services,nginx}
```

**Final Structure**:
```
/var/www/idrm/
├── backend/
│   ├── api-gateway/
│   └── services/
│       ├── service-management/
│       ├── geospatial/
│       ├── analytics/
│       ├── financial/
│       └── privacy/
├── frontend/
├── infrastructure/
│   ├── nginx/
│   ├── postgres/
│   ├── redis/
│   └── geoserver/
├── logs/
└── data/
```

---

## Database Setup

### 1. Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# In psql console, run:
```

```sql
-- Create database user
CREATE USER idrm_user WITH PASSWORD 'your_secure_password_here';

-- Create database
CREATE DATABASE idrm_db OWNER idrm_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;

-- Connect to database
\c idrm_db

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS
SELECT PostGIS_Version();

-- Exit
\q
```

### 2. Configure PostgreSQL for Development

```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/16/main/postgresql.conf
```

**Update these settings**:
```conf
# Listen on localhost
listen_addresses = 'localhost'

# Connection settings
max_connections = 100
shared_buffers = 256MB

# Enable logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = 'all'
```

```bash
# Edit pg_hba.conf for local access
sudo nano /etc/postgresql/16/main/pg_hba.conf
```

**Add this line** (DEVELOPMENT ONLY):
```conf
# Local development access
local   all             idrm_user                               md5
host    all             idrm_user       127.0.0.1/32            md5
host    all             idrm_user       ::1/128                 md5
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql

# Verify connection
psql -U idrm_user -d idrm_db -h localhost
# Enter password when prompted
# Type \q to exit
```

### 3. Create Database Schema

```bash
# Save this as infrastructure/postgres/schema.sql
cat > /var/www/idrm/infrastructure/postgres/schema.sql << 'EOF'
-- IDRM Database Schema
-- Version: 1.0

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service requests table with PostGIS
CREATE TABLE IF NOT EXISTS service_requests (
    id VARCHAR(20) PRIMARY KEY,
    user_id VARCHAR(20) REFERENCES users(id),
    type VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    description TEXT,
    location GEOMETRY(Point, 4326) NOT NULL,
    address VARCHAR(500),
    landmark VARCHAR(255),
    contact JSONB,
    details JSONB,
    is_anonymous BOOLEAN DEFAULT false,
    revv_id VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_type ON service_requests(type);
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at DESC);

-- Providers table
CREATE TABLE IF NOT EXISTS providers (
    id VARCHAR(20) PRIMARY KEY,
    organization_name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    services_offered JSONB,
    current_location GEOMETRY(Point, 4326),
    service_area GEOMETRY(Polygon, 4326),
    capacity INTEGER,
    availability_status VARCHAR(50) DEFAULT 'available',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_providers_location ON providers USING GIST(current_location);
CREATE INDEX idx_providers_service_area ON providers USING GIST(service_area);

-- Disaster zones table
CREATE TABLE IF NOT EXISTS disaster_zones (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    disaster_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50),
    affected_area GEOMETRY(MultiPolygon, 4326) NOT NULL,
    center_point GEOMETRY(Point, 4326),
    is_active BOOLEAN DEFAULT true,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disaster_zones_area ON disaster_zones USING GIST(affected_area);
CREATE INDEX idx_disaster_zones_active ON disaster_zones(is_active);

-- Donations table
CREATE TABLE IF NOT EXISTS donations (
    id VARCHAR(20) PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE,
    amount DECIMAL(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    donor_name VARCHAR(255),
    donor_email VARCHAR(255),
    donor_phone VARCHAR(20),
    is_anonymous BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'pending',
    disaster_id VARCHAR(20),
    purpose VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(20),
    ip_address VARCHAR(45),
    user_agent TEXT,
    details JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);
EOF

# Apply schema
psql -U idrm_user -d idrm_db -h localhost -f /var/www/idrm/infrastructure/postgres/schema.sql
```

---

## GeoServer Setup

### 1. Download and Install GeoServer

```bash
cd /var/www/idrm/infrastructure/geoserver

# Download GeoServer 2.24.0
wget https://sourceforge.net/projects/geoserver/files/GeoServer/2.24.0/geoserver-2.24.0-bin.zip

# Unzip
unzip geoserver-2.24.0-bin.zip
mv geoserver-2.24.0 geoserver

# Set permissions
chmod +x geoserver/bin/*.sh
```

### 2. Configure GeoServer

```bash
# Set GEOSERVER_HOME
echo 'export GEOSERVER_HOME=/var/www/idrm/infrastructure/geoserver/geoserver' >> ~/.bashrc
source ~/.bashrc

# Set Java options
cat > geoserver/bin/setenv.sh << 'EOF'
export JAVA_OPTS="-Xms2G -Xmx4G -XX:MaxPermSize=512M -XX:+UseParallelGC"
EOF

chmod +x geoserver/bin/setenv.sh
```

### 3. Start GeoServer

```bash
# Start GeoServer
cd /var/www/idrm/infrastructure/geoserver/geoserver
./bin/startup.sh

# Check if running
curl -I http://localhost:8080/geoserver/web/

# Access web interface
# URL: http://localhost:8080/geoserver/web/
# Default credentials: admin / geoserver
```

### 4. Create systemd Service for GeoServer

```bash
sudo nano /etc/systemd/system/geoserver.service
```

**Add**:
```ini
[Unit]
Description=GeoServer
After=network.target

[Service]
Type=forking
User=<your-username>
Group=<your-username>
Environment="JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64"
Environment="GEOSERVER_HOME=/var/www/idrm/infrastructure/geoserver/geoserver"
ExecStart=/var/www/idrm/infrastructure/geoserver/geoserver/bin/startup.sh
ExecStop=/var/www/idrm/infrastructure/geoserver/geoserver/bin/shutdown.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
# Replace <your-username> with actual username
sudo sed -i "s/<your-username>/$USER/g" /etc/systemd/system/geoserver.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable geoserver
sudo systemctl start geoserver
sudo systemctl status geoserver
```

---

## Backend Services Setup

### 1. Service Management Microservice

```bash
cd /var/www/idrm/backend/services/service-management

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Poetry
pip install poetry

# Create pyproject.toml
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "idrm-service-management"
version = "1.0.0"
description = "IDRM Service Management Microservice"
authors = ["IDRM Team"]

[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
uvicorn = {extras = ["standard"], version = "^0.24.0"}
sqlalchemy = "^2.0.0"
geoalchemy2 = "^0.14.0"
psycopg2-binary = "^2.9.0"
pydantic = "^2.5.0"
python-dotenv = "^1.0.0"
alembic = "^1.12.0"
redis = "^5.0.0"
celery = "^5.3.0"
shapely = "^2.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
EOF

# Install dependencies
poetry install

# Create directory structure
mkdir -p app/{api/v1/endpoints,core,models,schemas,services,repositories}
touch app/__init__.py
touch app/main.py
```

### 2. Create FastAPI Application

```bash
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="IDRM Service Management",
    description="Service Request Management Microservice",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "service-management"}

@app.get("/")
async def root():
    return {"message": "IDRM Service Management API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
EOF
```

### 3. Create Environment File

```bash
cat > .env << 'EOF'
DATABASE_URL=postgresql://idrm_user:your_secure_password_here@localhost:5432/idrm_db
REDIS_URL=redis://localhost:6379
SERVICE_PORT=8001
LOG_LEVEL=INFO
EOF

# Secure the .env file
chmod 600 .env
```

### 4. Test Service

```bash
# Activate venv
source venv/bin/activate

# Run service
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# In another terminal, test:
curl http://localhost:8001/health
# Should return: {"status":"healthy","service":"service-management"}
```

### 5. Repeat for Other Microservices

**Copy structure for**:
- Geospatial Service (port 8002)
- Analytics Service (port 8003)
- Financial Service (port 8004)
- Privacy Service (port 8005)

```bash
# Quick setup for geospatial service
cd /var/www/idrm/backend/services
cp -r service-management geospatial
cd geospatial
sed -i 's/8001/8002/g' app/main.py
sed -i 's/Service Management/Geospatial/g' app/main.py
sed -i 's/SERVICE_PORT=8001/SERVICE_PORT=8002/g' .env
```

---

## API Gateway Setup

### 1. Create API Gateway

```bash
cd /var/www/idrm/backend/api-gateway

# Initialize Bun project
bun init -y

# Install dependencies
bun add express socket.io cors helmet morgan winston passport passport-jwt jsonwebtoken bcrypt joi express-validator ioredis pg

# Create directory structure
mkdir -p src/{routes,middleware,websocket,utils,config}
```

### 2. Create Main Application

```bash
cat > src/index.js << 'EOF'
import express from 'express';
import { createServer } from 'http';
import { Server } from 'socket.io';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: '*',  // Configure properly in production
    credentials: true,
  },
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    service: 'api-gateway',
    runtime: 'bun',
    version: Bun.version
  });
});

// WebSocket
io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);
  
  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
  });
});

const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  console.log(`API Gateway running on Bun ${Bun.version} - Port ${PORT}`);
});
EOF
```

### 3. Create Environment File

```bash
cat > .env << 'EOF'
PORT=3000
NODE_ENV=development
DB_HOST=localhost
DB_PORT=5432
DB_NAME=idrm_db
DB_USER=idrm_user
DB_PASSWORD=your_secure_password_here
REDIS_HOST=localhost
REDIS_PORT=6379
JWT_SECRET=CHANGE_ME_RANDOM_STRING_64_CHARS
JWT_EXPIRATION=3600
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
EOF

chmod 600 .env
```

### 4. Test API Gateway

```bash
# Run with Bun
bun run --watch src/index.js

# Test
curl http://localhost:3000/health
```

---

## Frontend Setup

### 1. Create Frontend Project

```bash
cd /var/www/idrm/frontend

# Initialize with Bun
bun init -y

# Install dependencies
bun add -d vite tailwindcss autoprefixer postcss
bun add leaflet socket.io-client axios dayjs chart.js validator dompurify

# Create directory structure
mkdir -p src/{js/{auth,map,services,utils},css,pages,assets}
```

### 2. Initialize Vite

```bash
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite';

export default defineConfig({
  root: './src',
  build: {
    outDir: '../dist',
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    host: true,
  },
});
EOF
```

### 3. Initialize Tailwind CSS

```bash
# Create Tailwind config
bunx tailwindcss init -p

cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{html,js}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
```

### 4. Create Main HTML

```bash
cat > src/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IDRM Platform - Integrated Disaster Response Management</title>
    <link rel="stylesheet" href="/css/main.css">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
</head>
<body class="bg-gray-50">
    <div id="app">
        <h1 class="text-4xl font-bold text-center mt-20">
            IDRM Platform - Development Environment
        </h1>
        <p class="text-center text-gray-600 mt-4">
            Integrated Disaster Response Management System
        </p>
    </div>
    <script type="module" src="/js/main.js"></script>
</body>
</html>
EOF
```

### 5. Create CSS

```bash
cat > src/css/main.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  font-family: system-ui, -apple-system, sans-serif;
}
EOF
```

### 6. Create Main JS

```bash
cat > src/js/main.js << 'EOF'
console.log('IDRM Platform initialized');
console.log('Environment: Development');
console.log('Runtime: Bun', Bun?.version || 'Browser');

// API client will be added here
EOF
```

### 7. Update package.json

```bash
cat > package.json << 'EOF'
{
  "name": "idrm-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  },
  "dependencies": {
    "leaflet": "^1.9.4",
    "socket.io-client": "^4.6.0",
    "axios": "^1.6.0",
    "dayjs": "^1.11.10",
    "chart.js": "^4.4.0",
    "validator": "^13.11.0",
    "dompurify": "^3.0.6"
  }
}
EOF

bun install
```

### 8. Test Frontend

```bash
# Run dev server
bun run dev

# Access http://localhost:5173
```

---

## NGINX Configuration

### 1. Create NGINX Config

```bash
sudo nano /etc/nginx/sites-available/idrm-dev
```

**Add**:
```nginx
server {
    listen 80;
    server_name localhost;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API Gateway
    location /api {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # WebSocket
    location /socket.io {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # GeoServer
    location /geoserver {
        proxy_pass http://localhost:8080/geoserver;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Enable Site

```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/idrm-dev /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart NGINX
sudo systemctl restart nginx
```

---

## Service Management

### Create Process Manager Scripts

```bash
# Create start-all script
cat > /var/www/idrm/start-all.sh << 'EOF'
#!/bin/bash

echo "Starting IDRM Development Environment..."

# Start PostgreSQL
sudo systemctl start postgresql
echo "✓ PostgreSQL started"

# Start Redis
sudo systemctl start redis-server
echo "✓ Redis started"

# Start GeoServer
sudo systemctl start geoserver
echo "✓ GeoServer started"

# Start API Gateway
cd /var/www/idrm/backend/api-gateway
bun run --watch src/index.js > /var/www/idrm/logs/api-gateway/output.log 2>&1 &
echo $! > /var/www/idrm/logs/api-gateway/pid
echo "✓ API Gateway started (PID: $(cat /var/www/idrm/logs/api-gateway/pid))"

# Start Service Management
cd /var/www/idrm/backend/services/service-management
source venv/bin/activate
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8001 > /var/www/idrm/logs/services/service-management.log 2>&1 &
echo $! > /var/www/idrm/logs/services/service-management.pid
echo "✓ Service Management started"

# Start Frontend
cd /var/www/idrm/frontend
bun run dev > /var/www/idrm/logs/frontend.log 2>&1 &
echo $! > /var/www/idrm/logs/frontend.pid
echo "✓ Frontend started"

echo ""
echo "All services started!"
echo "Frontend: http://localhost:5173"
echo "API Gateway: http://localhost:3000"
echo "GeoServer: http://localhost:8080/geoserver"
EOF

chmod +x /var/www/idrm/start-all.sh
```

```bash
# Create stop-all script
cat > /var/www/idrm/stop-all.sh << 'EOF'
#!/bin/bash

echo "Stopping IDRM Development Environment..."

# Stop Frontend
if [ -f /var/www/idrm/logs/frontend.pid ]; then
    kill $(cat /var/www/idrm/logs/frontend.pid) 2>/dev/null
    rm /var/www/idrm/logs/frontend.pid
    echo "✓ Frontend stopped"
fi

# Stop API Gateway
if [ -f /var/www/idrm/logs/api-gateway/pid ]; then
    kill $(cat /var/www/idrm/logs/api-gateway/pid) 2>/dev/null
    rm /var/www/idrm/logs/api-gateway/pid
    echo "✓ API Gateway stopped"
fi

# Stop Service Management
if [ -f /var/www/idrm/logs/services/service-management.pid ]; then
    kill $(cat /var/www/idrm/logs/services/service-management.pid) 2>/dev/null
    rm /var/www/idrm/logs/services/service-management.pid
    echo "✓ Service Management stopped"
fi

# Stop GeoServer
sudo systemctl stop geoserver
echo "✓ GeoServer stopped"

echo "All services stopped!"
EOF

chmod +x /var/www/idrm/stop-all.sh
```

---

## Verification

### Test All Services

```bash
# Start all services
/var/www/idrm/start-all.sh

# Wait 30 seconds for services to start
sleep 30

# Test each service
echo "Testing services..."

# PostgreSQL
psql -U idrm_user -d idrm_db -h localhost -c "SELECT PostGIS_Version();"

# Redis
redis-cli ping

# API Gateway
curl http://localhost:3000/health

# Service Management
curl http://localhost:8001/health

# GeoServer
curl -I http://localhost:8080/geoserver/web/

# Frontend
curl -I http://localhost:5173

# NGINX
curl -I http://localhost
```

**Expected Output**:
```
✓ PostgreSQL: Returns PostGIS version
✓ Redis: PONG
✓ API Gateway: {"status":"healthy"}
✓ Service Management: {"status":"healthy"}
✓ GeoServer: HTTP 200 OK
✓ Frontend: HTTP 200 OK
✓ NGINX: HTTP 200 OK
```

---

## Troubleshooting

### Common Issues

**Issue 1: Port already in use**
```bash
# Find process using port 3000
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>
```

**Issue 2: PostgreSQL connection refused**
```bash
# Check if running
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Restart
sudo systemctl restart postgresql
```

**Issue 3: GeoServer not accessible**
```bash
# Check if running
sudo systemctl status geoserver

# Check logs
tail -f /var/www/idrm/infrastructure/geoserver/geoserver/logs/geoserver.log

# Restart
sudo systemctl restart geoserver
```

**Issue 4: Bun command not found**
```bash
# Add to PATH
echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Next Steps

1. **Development**: Start building features
2. **Testing**: Test all endpoints and workflows
3. **Staging**: When ready, move to `idrm-instructions_setup_staging.md`
4. **Production**: Finally deploy using `idrm-instructions_setup_production.md`

---

**Development environment ready! Start coding! 🚀**
