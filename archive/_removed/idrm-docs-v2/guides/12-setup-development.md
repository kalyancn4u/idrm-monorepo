> *Type: Guide (novice / how-to) · Audience: Developers · Status: Archived — v2 historical generation*

# IDRM Development Environment Setup (Monolith)

<!-- IDRM-CLEANUP doc=v2-g12-dev status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — dev setup → current
> MVP dev setup = [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Native Ubuntu Installation - No Docker

---

## 🎯 Goal

Set up a complete IDRM development environment on a **single Ubuntu server** with all services running natively (no Docker). This environment is designed for:

- Learning the architecture
- Local development
- Debugging
- Understanding each component

**Estimated Time:** 2-3 hours

---

## ✅ Prerequisites

Before starting, ensure you have completed `setup-prerequisites.md`:

- [ ] Ubuntu 22.04 or 24.04 LTS
- [ ] Minimum 8 GB RAM (16 GB recommended)
- [ ] 100 GB free disk space
- [ ] Sudo access
- [ ] Internet connection

---

## 📋 What Will Be Installed

| Component | Version | Purpose | Port |
|-----------|---------|---------|------|
| PostgreSQL | 16.x | Primary database | 5432 |
| PostGIS | 3.4.x | Geospatial extension | - |
| Redis | 7.2.x | Cache & sessions | 6379 |
| Python | 3.11.x | Backend services | - |
| Bun | 1.x | API Gateway runtime | - |
| GeoServer | 2.24.x | Map server | 8080 |
| Java OpenJDK | 17 | For GeoServer | - |
| NGINX | 1.24.x | Reverse proxy | 80/443 |

---

## 🚀 Installation Steps

### Step 1: System Preparation (10 minutes)

#### 1.1 Update System
```bash
# Update package lists
sudo apt update

# Upgrade installed packages
sudo apt upgrade -y

# Install essential build tools
sudo apt install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    git \
    gnupg \
    lsb-release \
    unzip \
    zip
```

#### 1.2 Configure Hostname
```bash
# Set hostname (optional but recommended)
sudo hostnamectl set-hostname idrm-dev

# Verify
hostnamectl
```

#### 1.3 Configure Timezone
```bash
# Set timezone (adjust to your location)
sudo timedatectl set-timezone Asia/Kolkata

# Verify
timedatectl
```

---

### Step 2: Install PostgreSQL 16 + PostGIS (15 minutes)

#### 2.1 Add PostgreSQL Repository
```bash
# Import repository key
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Add repository
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | \
    sudo tee /etc/apt/sources.list.d/pgdg.list

# Update package lists
sudo apt update
```

#### 2.2 Install PostgreSQL + PostGIS
```bash
# Install PostgreSQL 16
sudo apt install -y \
    postgresql-16 \
    postgresql-contrib-16 \
    postgresql-server-dev-16 \
    postgresql-client-16

# Install PostGIS
sudo apt install -y \
    postgresql-16-postgis-3 \
    postgresql-16-postgis-3-scripts \
    postgis

# Verify installation
psql --version
# Should show: psql (PostgreSQL) 16.x
```

#### 2.3 Configure PostgreSQL
```bash
# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql

# Switch to postgres user
sudo -u postgres psql
```

#### 2.4 Create IDRM Database and User
```sql
-- In PostgreSQL shell
CREATE USER idrm_user WITH PASSWORD 'idrm_secure_password_2024';
CREATE DATABASE idrm_db OWNER idrm_user;
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;

-- Connect to IDRM database
\c idrm_db

-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify PostGIS
SELECT PostGIS_version();

-- Exit
\q
```

#### 2.5 Configure Local Access
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

# Add this line BEFORE the "local all all peer" line:
# local   idrm_db   idrm_user   md5
# host    idrm_db   idrm_user   127.0.0.1/32   md5

# Reload PostgreSQL
sudo systemctl reload postgresql
```

#### 2.6 Test Connection
```bash
# Test connection
PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db -h localhost -c "SELECT PostGIS_version();"

# Should show PostGIS version
```

---

### Step 3: Install Redis (5 minutes)

#### 3.1 Install Redis Server
```bash
# Install Redis
sudo apt install -y redis-server redis-tools

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Check status
sudo systemctl status redis-server
```

#### 3.2 Configure Redis
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Find and uncomment/modify:
# bind 127.0.0.1 ::1
# requirepass idrm_redis_password_2024
# maxmemory 256mb
# maxmemory-policy allkeys-lru

# Restart Redis
sudo systemctl restart redis-server
```

#### 3.3 Test Redis
```bash
# Test connection
redis-cli ping
# Should return: PONG

# Test with password (if set)
redis-cli -a idrm_redis_password_2024 ping
```

---

### Step 4: Install Python 3.11 Environment (10 minutes)

#### 4.1 Install Python 3.11
```bash
# Add deadsnakes PPA (if not on 24.04)
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip

# Verify
python3.11 --version
```

#### 4.2 Create Virtual Environment
```bash
# Create project directory
mkdir -p ~/idrm-mvp
cd ~/idrm-mvp

# Create virtual environment
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

#### 4.3 Install Python Dependencies
```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
geoalchemy2==0.14.2
psycopg2-binary==2.9.9

# Geospatial
shapely==2.0.2
pyproj==3.6.1

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6

# Redis
redis==5.0.1
aioredis==2.0.1

# Utilities
python-dotenv==1.0.0
httpx==0.25.2

# Development
pytest==7.4.3
pytest-asyncio==0.21.1
black==23.11.0
flake8==6.1.0
EOF

# Install
pip install -r requirements.txt
```

---

### Step 5: Install Bun (5 minutes)

#### 5.1 Install Bun Runtime
```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Add to PATH (add to ~/.bashrc)
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Reload shell
source ~/.bashrc

# Verify
bun --version
```

#### 5.2 Create Bun Project
```bash
cd ~/idrm-mvp

# Create frontend directory
mkdir -p frontend
cd frontend

# Initialize Bun project
bun init -y

# Install dependencies
bun add express
bun add @types/express -d
bun add dotenv
bun add redis
bun add ws  # WebSocket support
```

---

### Step 6: Install Java & GeoServer (20 minutes)

#### 6.1 Install Java OpenJDK 17
```bash
# Install Java
sudo apt install -y openjdk-17-jre openjdk-17-jdk

# Verify
java -version
# Should show: openjdk version "17.x.x"
```

#### 6.2 Download GeoServer
```bash
# Create directory
sudo mkdir -p /opt/geoserver
cd /opt/geoserver

# Download GeoServer 2.24.0
sudo wget https://sourceforge.net/projects/geoserver/files/GeoServer/2.24.0/geoserver-2.24.0-bin.zip

# Extract
sudo unzip geoserver-2.24.0-bin.zip

# Set permissions
sudo chown -R $USER:$USER /opt/geoserver
```

#### 6.3 Configure GeoServer
```bash
# Set Java heap size
export GEOSERVER_OPTS="-Xms512m -Xmx1024m"

# Add to ~/.bashrc
echo 'export GEOSERVER_OPTS="-Xms512m -Xmx1024m"' >> ~/.bashrc
```

#### 6.4 Create GeoServer Service
```bash
# Create systemd service
sudo tee /etc/systemd/system/geoserver.service << 'EOF'
[Unit]
Description=GeoServer
After=network.target

[Service]
Type=simple
User=$USER
Environment="GEOSERVER_HOME=/opt/geoserver"
Environment="GEOSERVER_DATA_DIR=/opt/geoserver/data_dir"
Environment="GEOSERVER_OPTS=-Xms512m -Xmx1024m"
ExecStart=/opt/geoserver/bin/startup.sh
ExecStop=/opt/geoserver/bin/shutdown.sh
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

# Replace $USER with actual username
sudo sed -i "s/\$USER/$USER/g" /etc/systemd/system/geoserver.service

# Reload systemd
sudo systemctl daemon-reload

# Start GeoServer
sudo systemctl start geoserver
sudo systemctl enable geoserver

# Check status
sudo systemctl status geoserver
```

#### 6.5 Verify GeoServer
```bash
# Wait 30 seconds for startup
sleep 30

# Check if running
curl http://localhost:8080/geoserver/web/

# Access in browser: http://localhost:8080/geoserver
# Default credentials: admin / geoserver
```

---

### Step 7: Install NGINX (10 minutes)

#### 7.1 Install NGINX
```bash
# Install NGINX
sudo apt install -y nginx

# Start NGINX
sudo systemctl start nginx
sudo systemctl enable nginx

# Check status
sudo systemctl status nginx
```

#### 7.2 Configure NGINX for Development
```bash
# Create IDRM configuration
sudo tee /etc/nginx/sites-available/idrm-dev << 'EOF'
server {
    listen 80;
    server_name localhost;

    # API Gateway (Bun)
    location /api/ {
        proxy_pass http://localhost:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Python Backend
    location /backend/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # GeoServer
    location /geoserver/ {
        proxy_pass http://localhost:8080/geoserver/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Frontend (Vite dev server)
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/idrm-dev /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Reload NGINX
sudo systemctl reload nginx
```

---

### Step 8: Create Project Structure (15 minutes)

#### 8.1 Clone or Create Project
```bash
cd ~/idrm-mvp

# If cloning from Git
# git clone https://github.com/your-org/idrm-mvp.git .

# Or create structure manually
mkdir -p {backend,frontend,database,docs,scripts}
mkdir -p backend/{app,tests}
mkdir -p backend/app/{api,core,db,models,schemas,services}
mkdir -p frontend/{src,public}
mkdir -p frontend/src/{components,pages,styles,utils}
mkdir -p database/{migrations,seeds}
```

#### 8.2 Create Environment Files
```bash
# Backend .env
cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql+asyncpg://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db

# Redis
REDIS_URL=redis://:idrm_redis_password_2024@localhost:6379/0

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG

# GeoServer
GEOSERVER_URL=http://localhost:8080/geoserver
GEOSERVER_USERNAME=admin
GEOSERVER_PASSWORD=geoserver

# Email (optional for dev)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@idrm.local
EOF

# Frontend .env
cat > frontend/.env << 'EOF'
# API endpoints
VITE_API_URL=http://localhost:3000/api
VITE_BACKEND_URL=http://localhost:8000
VITE_GEOSERVER_URL=http://localhost:8080/geoserver

# Environment
VITE_ENVIRONMENT=development
EOF
```

#### 8.3 Create Backend Bootstrap
```bash
# Create main.py
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IDRM Backend API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "IDRM Backend API",
        "status": "operational",
        "version": "0.1.0"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "environment": "development"
    }
EOF
```

#### 8.4 Create Bun API Gateway
```bash
# Create index.ts
cat > frontend/index.ts << 'EOF'
import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', service: 'api-gateway' });
});

// API routes
app.get('/api/version', (req, res) => {
  res.json({ version: '0.1.0', service: 'IDRM API Gateway' });
});

// WebSocket connection
wss.on('connection', (ws) => {
  console.log('New WebSocket connection');
  
  ws.on('message', (message) => {
    console.log('Received:', message);
    ws.send(JSON.stringify({ echo: message.toString() }));
  });
});

// Start server
server.listen(PORT, () => {
  console.log(`🚀 API Gateway running on http://localhost:${PORT}`);
  console.log(`📡 WebSocket server running`);
});
EOF
```

---

### Step 9: Start Development Services (5 minutes)

#### 9.1 Start Backend
```bash
# Terminal 1: Backend
cd ~/idrm-mvp/backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Should see: Application startup complete
```

#### 9.2 Start API Gateway
```bash
# Terminal 2: API Gateway
cd ~/idrm-mvp/frontend
bun run index.ts

# Should see: API Gateway running on http://localhost:3000
```

#### 9.3 Start Frontend Dev Server (Optional)
```bash
# Terminal 3: Frontend
cd ~/idrm-mvp/frontend
bun vite

# Should see: Local: http://localhost:5173
```

---

### Step 10: Verification (10 minutes)

#### 10.1 Check All Services
```bash
# PostgreSQL
PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db -h localhost -c "SELECT 1;"

# Redis
redis-cli -a idrm_redis_password_2024 ping

# GeoServer
curl http://localhost:8080/geoserver/web/ | grep -o "GeoServer"

# Backend API
curl http://localhost:8000/health

# API Gateway
curl http://localhost:3000/health

# NGINX
curl http://localhost/backend/health
```

#### 10.2 Test Database Connection
```bash
cd ~/idrm-mvp/backend
source ../venv/bin/activate

# Test script
python << 'EOF'
import asyncpg
import asyncio

async def test_db():
    conn = await asyncpg.connect(
        'postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db'
    )
    version = await conn.fetchval('SELECT version()')
    postgis = await conn.fetchval('SELECT PostGIS_version()')
    print(f"✓ PostgreSQL: {version[:30]}...")
    print(f"✓ PostGIS: {postgis}")
    await conn.close()

asyncio.run(test_db())
EOF
```

#### 10.3 Service Status Summary
```bash
# Create status check script
cat > ~/idrm-mvp/scripts/status.sh << 'EOF'
#!/bin/bash
echo "=== IDRM Development Environment Status ==="
echo ""

# PostgreSQL
if systemctl is-active --quiet postgresql; then
    echo "✓ PostgreSQL: Running"
else
    echo "✗ PostgreSQL: Not running"
fi

# Redis
if systemctl is-active --quiet redis-server; then
    echo "✓ Redis: Running"
else
    echo "✗ Redis: Not running"
fi

# GeoServer
if systemctl is-active --quiet geoserver; then
    echo "✓ GeoServer: Running"
else
    echo "✗ GeoServer: Not running"
fi

# NGINX
if systemctl is-active --quiet nginx; then
    echo "✓ NGINX: Running"
else
    echo "✗ NGINX: Not running"
fi

# Backend API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✓ Backend API: Running"
else
    echo "✗ Backend API: Not running"
fi

# API Gateway
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✓ API Gateway: Running"
else
    echo "✗ API Gateway: Not running"
fi

echo ""
echo "=== Port Status ==="
netstat -tuln | grep -E ':(5432|6379|8080|8000|3000|80)' || echo "No services listening"
EOF

chmod +x ~/idrm-mvp/scripts/status.sh
~/idrm-mvp/scripts/status.sh
```

---

## 🎯 Development Workflow

### Daily Startup

```bash
# 1. Ensure system services are running
sudo systemctl status postgresql redis-server geoserver nginx

# 2. Start backend
cd ~/idrm-mvp/backend
source ../venv/bin/activate
uvicorn app.main:app --reload --port 8000 &

# 3. Start API gateway
cd ~/idrm-mvp/frontend
bun run index.ts &

# 4. Start frontend dev server (optional)
bun vite
```

### Access Points

- **Frontend**: http://localhost (via NGINX) or http://localhost:5173 (direct)
- **API Gateway**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **GeoServer**: http://localhost:8080/geoserver

---

## 🛠️ Troubleshooting

### PostgreSQL Won't Start
```bash
# Check logs
sudo journalctl -u postgresql -n 50

# Check port
sudo lsof -i :5432

# Restart
sudo systemctl restart postgresql
```

### Redis Connection Refused
```bash
# Check if running
sudo systemctl status redis-server

# Check config
sudo nano /etc/redis/redis.conf

# Restart
sudo systemctl restart redis-server
```

### GeoServer Not Accessible
```bash
# Check if running
sudo systemctl status geoserver

# Check logs
tail -f /opt/geoserver/logs/geoserver.log

# Restart
sudo systemctl restart geoserver
```

### Port Already in Use
```bash
# Find process
sudo lsof -i :<PORT>

# Kill if safe
sudo kill -9 <PID>
```

---

## 📚 Next Steps

1. **Database Schema**: Create initial schema and migrations
2. **Backend Development**: Implement API endpoints
3. **Frontend Development**: Build UI with Tailwind CSS
4. **Integration**: Connect all components
5. **Testing**: Write and run tests

**Continue to**: Application development guides in `docs/`

---

## ✅ Success Checklist

- [ ] PostgreSQL 16 + PostGIS installed and running
- [ ] Redis installed and running
- [ ] Python 3.11 environment set up
- [ ] Bun runtime installed
- [ ] GeoServer running on port 8080
- [ ] NGINX configured and running
- [ ] Project structure created
- [ ] Environment variables configured
- [ ] Backend API responding
- [ ] API Gateway responding
- [ ] All services verified with status script

**Development environment ready for coding! 🚀**
