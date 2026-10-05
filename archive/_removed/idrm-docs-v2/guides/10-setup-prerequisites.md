> *Type: Guide (novice / how-to) · Audience: Novices, DevOps · Status: Archived — v2 historical generation*

# IDRM Platform Setup Prerequisites v2.0

<!-- IDRM-CLEANUP doc=v2-g10-prereq status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — setup → current
> MVP setup = [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + installer `../../../scripts/setup-idrm-ubuntu.sh` + [`linux-101`](../../../../guides/mvp/learn/linux-101.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Complete Requirements Checklist - Aligned with PRD v2.0

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Stack**: Bun + Python (Miniconda) + PostgreSQL + PostGIS + Python Geospatial Service

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Required Software](#required-software)
3. [Domain & DNS Setup](#domain--dns-setup)
4. [Access Requirements](#access-requirements)
5. [Pre-Installation Checklist](#pre-installation-checklist)

---

## 🖥️ System Requirements

### Hardware Requirements by Environment

**Development (Native Ubuntu)**:
```
CPU:    4-8 cores
RAM:    8-16 GB
Storage: 100 GB SSD
Network: 100 Mbps
```

**Staging (Docker)**:
```
CPU:    8 cores
RAM:    16-32 GB
Storage: 200 GB SSD
Network: 100 Mbps
```

**Production (Docker + Security)**:
```
CPU:    16+ cores (recommended)
RAM:    32-64 GB (recommended)
Storage: 500 GB NVMe SSD
Network: 1 Gbps
Backup:  500 GB (separate storage)
```

### Operating System

**Supported** ✅:
- Ubuntu 22.04 LTS (Jammy) - **Recommended**
- Ubuntu 24.04 LTS (Noble)
- Debian 12 (Bookworm)

**NOT Supported** ❌:
- CentOS/RHEL (different package management)
- Windows Server
- macOS Server
- Ubuntu < 22.04

### Verify Your System

```bash
# Check OS version
lsb_release -a
# Should show: Ubuntu 22.04 or 24.04

# Check CPU cores
nproc
# Should show: 4+ for dev, 8+ for staging, 16+ for production

# Check RAM
free -h
# Should show: 8GB+ for dev, 16GB+ for staging, 32GB+ for production

# Check disk space
df -h /
# Should show: 100GB+ free for dev, 200GB+ for staging, 500GB+ for production

# Check network interface
ip addr show
```

---

## 📦 Required Software

### Core Stack (FINAL - v2.0)

```
1. ✅ NGINX (Reverse Proxy)
2. ✅ Bun (API Gateway) - NOT Node.js
3. ✅ Python 3.11 via Miniconda - NOT venv
4. ✅ Redis (Cache)
5. ✅ Python Geospatial Service (FastAPI) - NOT Java GeoServer
6. ✅ PostgreSQL 16 + PostGIS 3.4
```

### 1. System Essentials

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install build tools
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
  zip \
  vim \
  nano \
  htop \
  net-tools \
  dnsutils

# Verify
gcc --version
git --version
```

---

### 2. Bun Runtime (MANDATORY)

**Why Bun**: 3-4x faster than Node.js, built-in TypeScript, WebSocket support

```bash
# Install Bun
curl -fsSL https://bun.sh/install | bash

# Add to PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# Make permanent (add to ~/.bashrc)
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc

# Reload shell
source ~/.bashrc

# Verify installation
bun --version
# Should show: 1.x.x or higher

# Test Bun
bun --help
```

**DO NOT INSTALL**: ❌ Node.js, ❌ npm, ❌ yarn, ❌ pnpm

---

### 3. Miniconda + Python 3.11 (MANDATORY)

**Why Miniconda**: Better for geospatial libraries (GDAL, GEOS, PROJ), scientific computing

```bash
# Download Miniconda
cd /tmp
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install Miniconda
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Initialize conda
$HOME/miniconda3/bin/conda init bash

# Reload shell
source ~/.bashrc

# Verify conda installation
conda --version
# Should show: conda 23.x or higher

# Create IDRM environment
conda create -n idrm-mvp python=3.11 -y

# Activate environment
conda activate idrm-mvp

# Verify Python version
python --version
# Should show: Python 3.11.x

# Verify environment
which python
# Should show: /home/user/miniconda3/envs/idrm-mvp/bin/python
```

**DO NOT USE**: ❌ python3-venv, ❌ virtualenv, ❌ pipenv

---

### 4. Python Geospatial Libraries

**Install via Conda** (better dependency resolution):

```bash
# Ensure idrm-mvp environment is active
conda activate idrm-mvp

# Install geospatial core libraries via conda-forge
conda install -c conda-forge -y \
  geopandas=0.14.1 \
  shapely=2.0.2 \
  fiona=1.9.5 \
  pyproj=3.6.1 \
  rasterio=1.3.9 \
  gdal=3.8.0 \
  mercantile=1.2.1

# Verify installations
python -c "import geopandas; print('GeoPandas:', geopandas.__version__)"
python -c "import shapely; print('Shapely:', shapely.__version__)"
python -c "from osgeo import gdal; print('GDAL:', gdal.__version__)"
python -c "import mercantile; print('Mercantile:', mercantile.__version__)"

# Should show all versions without errors
```

**Install FastAPI and Database via pip**:

```bash
# Still in idrm-mvp environment
pip install \
  fastapi==0.104.1 \
  uvicorn[standard]==0.24.0 \
  pydantic==2.5.0 \
  pydantic-settings==2.1.0 \
  sqlalchemy==2.0.23 \
  geoalchemy2==0.14.2 \
  asyncpg==0.29.0 \
  psycopg2-binary==2.9.9 \
  redis==5.0.1 \
  python-jose[cryptography]==3.3.0 \
  passlib[bcrypt]==1.7.4 \
  python-multipart==0.0.6 \
  python-dotenv==1.0.0 \
  httpx==0.25.2 \
  pillow==10.1.0 \
  mapbox-vector-tile==2.0.1 \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1 \
  black==23.11.0 \
  flake8==6.1.0

# Verify FastAPI
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
```

---

### 5. PostgreSQL 16 + PostGIS 3.4

```bash
# Add PostgreSQL repository
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] \
  http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | \
  sudo tee /etc/apt/sources.list.d/pgdg.list

# Update package lists
sudo apt update

# Install PostgreSQL 16 + PostGIS
sudo apt install -y \
  postgresql-16 \
  postgresql-contrib-16 \
  postgresql-16-postgis-3 \
  postgresql-16-postgis-3-scripts \
  postgis

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
# Should show: psql (PostgreSQL) 16.x

# Check PostGIS availability
sudo -u postgres psql -c "SELECT PostGIS_version();" postgres 2>/dev/null || echo "PostGIS will be enabled per-database"
```

---

### 6. Redis 7.2+

```bash
# Install Redis
sudo apt install -y redis-server redis-tools

# Start and enable Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify installation
redis-cli --version
# Should show: redis-cli 7.x or 6.x

# Test Redis
redis-cli ping
# Should return: PONG
```

---

### 7. NGINX 1.24+

```bash
# Install NGINX
sudo apt install -y nginx

# Start and enable NGINX
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify installation
nginx -v
# Should show: nginx version: nginx/1.24.x or higher

# Test NGINX
curl -I http://localhost
# Should return: HTTP/1.1 200 OK
```

---

### 8. Docker (Staging & Production ONLY)

**Not needed for Development** (native setup is faster)

```bash
# Remove old Docker versions
sudo apt remove docker docker-engine docker.io containerd runc 2>/dev/null || true

# Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Verify installation
docker --version
docker compose version

# Test Docker
docker run hello-world
# Should download and run successfully
```

---

## 🌐 Domain & DNS Setup (Production Only)

### Domain Requirements

**You Need**:
1. Registered domain name (e.g., `idrm.gov.in`)
2. Access to DNS management panel
3. Email for SSL certificates

### DNS Configuration

**Required DNS A Records**:

```
Type    Name              Value                TTL
A       @                 <YOUR_SERVER_IP>     3600
A       www               <YOUR_SERVER_IP>     3600
A       api               <YOUR_SERVER_IP>     3600
```

**Optional** (if using subdomains):
```
CNAME   www               yourdomain.com       3600
```

**Example for `idrm.example.com`**:
```bash
# Main domain
A       @                 203.0.113.1          3600

# API subdomain  
A       api               203.0.113.1          3600

# WWW subdomain
CNAME   www               idrm.example.com     3600
```

**Verify DNS Propagation**:

```bash
# Check A record
dig yourdomain.com +short
# Should show: YOUR_SERVER_IP

# Check API subdomain
dig api.yourdomain.com +short
# Should show: YOUR_SERVER_IP

# Check from multiple locations
nslookup yourdomain.com 8.8.8.8
nslookup yourdomain.com 1.1.1.1

# Wait 5-60 minutes for global DNS propagation
```

---

## 🔐 Access Requirements

### 1. SSH Access Setup

**Generate SSH Key** (on your local machine):

```bash
# Generate ED25519 key (more secure than RSA)
ssh-keygen -t ed25519 -C "your_email@example.com" -f ~/.ssh/idrm_key

# Or RSA if ED25519 not supported
ssh-keygen -t rsa -b 4096 -C "your_email@example.com" -f ~/.ssh/idrm_key

# Copy public key to server
ssh-copy-id -i ~/.ssh/idrm_key.pub username@server_ip

# Test connection
ssh -i ~/.ssh/idrm_key username@server_ip
```

**Configure SSH Client** (~/.ssh/config):

```
Host idrm
    HostName your_server_ip
    User your_username
    IdentityFile ~/.ssh/idrm_key
    Port 22
```

**Test**:
```bash
ssh idrm
```

---

### 2. Firewall Configuration

**Required Open Ports**:

| Port | Service | Development | Staging | Production |
|------|---------|-------------|---------|------------|
| 22 | SSH | ✅ Secure | ✅ Secure | ✅ IP Restricted |
| 80 | HTTP | ✅ Open | ✅ Open | ✅ Redirect to 443 |
| 443 | HTTPS | ❌ | ✅ Open | ✅ Open |
| 3000 | Bun Gateway | 🏠 Localhost | 🐳 Internal | 🐳 Internal |
| 5432 | PostgreSQL | 🏠 Localhost | 🐳 Internal | 🐳 Internal |
| 6379 | Redis | 🏠 Localhost | 🐳 Internal | 🐳 Internal |
| 8002 | Python Geo | 🏠 Localhost | 🐳 Internal | 🐳 Internal |

**Legend**:
- ✅ Open = Accessible from internet
- 🏠 Localhost = Only accessible from same machine
- 🐳 Internal = Only accessible within Docker network
- ❌ = Not used

**Production Firewall Setup (UFW)**:

```bash
# Enable firewall
sudo ufw --force enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Check status
sudo ufw status numbered

# Example output:
# Status: active
# 
#      To                         Action      From
#      --                         ------      ----
# [1]  22/tcp                     ALLOW IN    Anywhere
# [2]  80/tcp                     ALLOW IN    Anywhere
# [3]  443/tcp                    ALLOW IN    Anywhere
```

**NEVER EXPOSE** in Production:
- ❌ Port 5432 (PostgreSQL)
- ❌ Port 6379 (Redis)
- ❌ Port 3000 (Bun Gateway - use NGINX proxy)
- ❌ Port 8002 (Python Geospatial - use NGINX proxy)

---

### 3. Sudo Access

```bash
# Verify sudo access
sudo whoami
# Should output: root

# Check sudo group membership
groups $USER
# Should include: sudo or wheel
```

---

## ✅ Pre-Installation Checklist

### System Readiness

**Hardware**:
- [ ] CPU cores meet minimum (4+ dev, 8+ staging, 16+ prod)
- [ ] RAM meets minimum (8GB+ dev, 16GB+ staging, 32GB+ prod)
- [ ] Disk space available (100GB+ dev, 200GB+ staging, 500GB+ prod)
- [ ] Network connectivity stable (100Mbps+ dev/staging, 1Gbps+ prod)

**Operating System**:
- [ ] Ubuntu 22.04 LTS or 24.04 LTS installed
- [ ] System fully updated (`sudo apt update && sudo apt upgrade`)
- [ ] Hostname configured
- [ ] Timezone set correctly
- [ ] Locale configured (en_US.UTF-8 recommended)

**Access**:
- [ ] SSH access configured
- [ ] SSH key authentication working
- [ ] Sudo privileges confirmed
- [ ] Firewall planned (production)

---

### Software Installation Checklist

**Core Stack**:
- [ ] Bun installed (`bun --version` works)
- [ ] Bun in PATH
- [ ] Miniconda installed
- [ ] Conda initialized in bash
- [ ] IDRM conda environment created (`conda env list` shows idrm-mvp)
- [ ] Python 3.11 in conda environment
- [ ] PostgreSQL 16 installed and running
- [ ] PostGIS available
- [ ] Redis installed and running
- [ ] NGINX installed and running

**Geospatial Libraries** (in conda environment):
- [ ] GeoPandas installed
- [ ] Shapely installed
- [ ] GDAL installed
- [ ] Fiona installed
- [ ] PyProj installed
- [ ] Mercantile installed

**Python Packages** (in conda environment):
- [ ] FastAPI installed
- [ ] Uvicorn installed
- [ ] SQLAlchemy installed
- [ ] GeoAlchemy2 installed
- [ ] Pillow installed

**Docker** (Staging/Production only):
- [ ] Docker installed
- [ ] Docker Compose installed
- [ ] User added to docker group
- [ ] Docker service enabled
- [ ] `docker run hello-world` succeeds

---

### Network & Domain (Production)

- [ ] Domain name registered
- [ ] DNS A record created for main domain
- [ ] DNS A record created for api subdomain
- [ ] DNS propagated (verified with `dig`)
- [ ] Email address for Let's Encrypt configured
- [ ] Firewall ports planned

---

### Security Checklist

**Authentication**:
- [ ] SSH key pair generated
- [ ] Public key added to server
- [ ] Password authentication planned to disable
- [ ] Root login planned to disable

**Secrets & Passwords**:
- [ ] Database password generated (32+ characters)
- [ ] Redis password generated (32+ characters)
- [ ] JWT secret generated (64+ characters)
- [ ] Passwords stored securely (password manager)
- [ ] `.env` file template prepared

**Production Security**:
- [ ] Fail2Ban planned (production)
- [ ] UFW firewall planned
- [ ] SSL certificate plan (Let's Encrypt)
- [ ] Backup strategy planned
- [ ] Monitoring plan outlined

---

## 🔑 Environment Variables Template

Create `.env.example` for reference:

```bash
# ============================================
# IDRM Platform Environment Configuration
# ============================================

# ------------------
# Database (PostgreSQL + PostGIS)
# ------------------
DATABASE_URL=postgresql+asyncpg://idrm_user:CHANGE_ME@localhost:5432/idrm_db
DATABASE_URL_SYNC=postgresql://idrm_user:CHANGE_ME@localhost:5432/idrm_db

# ------------------
# Redis Cache
# ------------------
REDIS_URL=redis://:CHANGE_ME@localhost:6379/0
REDIS_PASSWORD=CHANGE_ME

# ------------------
# API Gateway (Bun)
# ------------------
PORT=3000
NODE_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost

# ------------------
# Authentication & Security
# ------------------
JWT_SECRET_KEY=CHANGE_ME_64_CHARS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ------------------
# Python Services
# ------------------
# Auth Service (8000)
AUTH_SERVICE_PORT=8000

# Service Management (8001)
SERVICE_MGMT_PORT=8001

# Geospatial Service (8002)
GEOSPATIAL_SERVICE_PORT=8002
TILE_CACHE_DIR=/var/cache/idrm/tiles
MAX_TILE_CACHE_SIZE_MB=1000

# Analytics Service (8003)
ANALYTICS_SERVICE_PORT=8003

# Notification Service (8004)
NOTIFICATION_SERVICE_PORT=8004

# ------------------
# Frontend Configuration
# ------------------
# HTML/Tailwind (Primary - Port 5173)
VITE_API_URL=http://localhost/api
VITE_GEO_URL=http://localhost/geo

# React SPA (Secondary - Port 5174)
VITE_REACT_API_URL=http://localhost/api

# React Native (Mobile)
EXPO_PUBLIC_API_URL=http://localhost:3000/api

# ------------------
# Email (Production)
# ------------------
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@idrm.gov.in

# ------------------
# Production-Specific
# ------------------
DOMAIN=idrm.example.com
SSL_EMAIL=admin@idrm.example.com
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
```

---

## 🔐 Generate Secure Secrets

```bash
# Generate database password (32 characters)
openssl rand -base64 32

# Generate Redis password (32 characters)
openssl rand -base64 32

# Generate JWT secret (64 characters hex)
openssl rand -hex 64

# Generate UUID (for various IDs)
uuidgen
```

**Example Outputs**:
```bash
Database: kJ8x9mN2pL5qR7sT3vW6yZ1aC4dF8gH0iK2mO5pS8uX=
Redis:    xY7zA2bC5dE8fG1hJ4kL7mN0oP3qR6sT9uV2wX5yZ8aB=
JWT:      a1b2c3d4e5f67890abcdef1234567890abcdef1234567890abcdef1234567890
```

---

## 🧪 Verification Commands

### Quick Health Check

```bash
#!/bin/bash
echo "=== IDRM Prerequisites Verification ==="
echo ""

# System
echo "OS: $(lsb_release -ds)"
echo "Kernel: $(uname -r)"
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $4}') free"
echo ""

# Software versions
echo "=== Installed Software ==="
bun --version 2>/dev/null && echo "✅ Bun" || echo "❌ Bun not installed"
conda --version 2>/dev/null && echo "✅ Conda" || echo "❌ Conda not installed"
python --version 2>/dev/null && echo "✅ Python" || echo "❌ Python not installed"
psql --version 2>/dev/null && echo "✅ PostgreSQL" || echo "❌ PostgreSQL not installed"
redis-cli --version 2>/dev/null && echo "✅ Redis" || echo "❌ Redis not installed"
nginx -v 2>&1 | grep -q nginx && echo "✅ NGINX" || echo "❌ NGINX not installed"
docker --version 2>/dev/null && echo "✅ Docker" || echo "⚠️  Docker not installed (OK for dev)"
echo ""

# Services
echo "=== Service Status ==="
systemctl is-active --quiet postgresql && echo "✅ PostgreSQL running" || echo "❌ PostgreSQL not running"
systemctl is-active --quiet redis-server && echo "✅ Redis running" || echo "❌ Redis not running"
systemctl is-active --quiet nginx && echo "✅ NGINX running" || echo "❌ NGINX not running"
echo ""

# Python environment
echo "=== Python Environment ==="
conda env list | grep -q idrm-mvp && echo "✅ idrm-mvp conda environment exists" || echo "❌ idrm-mvp environment not created"

# Activate and check packages
if conda env list | grep -q idrm-mvp; then
    eval "$(conda shell.bash hook)"
    conda activate idrm-mvp 2>/dev/null
    python -c "import geopandas" 2>/dev/null && echo "✅ GeoPandas installed" || echo "❌ GeoPandas not installed"
    python -c "import fastapi" 2>/dev/null && echo "✅ FastAPI installed" || echo "❌ FastAPI not installed"
fi

echo ""
echo "=== Prerequisites Check Complete ==="
```

**Save and run**:
```bash
chmod +x check-prerequisites.sh
./check-prerequisites.sh
```

---

## 🚨 Common Issues & Solutions

### Issue 1: Bun not in PATH

**Symptom**: `bun: command not found`

**Solution**:
```bash
# Add to ~/.bashrc
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
bun --version
```

---

### Issue 2: Conda environment not activating

**Symptom**: `conda activate idrm-mvp` doesn't work

**Solution**:
```bash
# Initialize conda for bash
conda init bash

# Reload shell
source ~/.bashrc

# Try again
conda activate idrm-mvp
```

---

### Issue 3: GeoPandas import fails

**Symptom**: `ImportError: cannot import name 'GeoDataFrame'`

**Solution**:
```bash
# Ensure you're in conda environment
conda activate idrm-mvp

# Reinstall via conda (better dependency resolution)
conda install -c conda-forge geopandas --force-reinstall -y

# Verify
python -c "import geopandas; print(geopandas.__version__)"
```

---

### Issue 4: PostgreSQL won't start

**Symptom**: `systemctl status postgresql` shows failed

**Solution**:
```bash
# Check logs
sudo journalctl -u postgresql -n 50 --no-pager

# Common fix: corrupt postmaster.pid
sudo rm /var/lib/postgresql/16/main/postmaster.pid

# Restart
sudo systemctl restart postgresql
```

---

### Issue 5: Permission denied (Docker)

**Symptom**: `permission denied while trying to connect to Docker daemon`

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login, or
newgrp docker

# Verify
docker ps
```

---

### Issue 6: Port already in use

**Symptom**: `Address already in use: bind: 0.0.0.0:3000`

**Solution**:
```bash
# Find process using port
sudo lsof -i :3000

# Kill process
sudo kill -9 <PID>

# Or find and kill in one command
sudo fuser -k 3000/tcp
```

---

## 📚 Next Steps

After completing all prerequisites:

1. **Development Setup**: → `idrm-instructions_setup_monolith_v2.md`
2. **Staging Setup**: → `idrm-instructions_setup_staging_v2.md`
3. **Production Setup**: → `idrm-instructions_setup_production_v2.md`

---

## 🆘 Support Resources

**Official Documentation**:
- Bun: https://bun.sh/docs
- Miniconda: https://docs.conda.io/en/latest/miniconda.html
- PostgreSQL: https://www.postgresql.org/docs/16/
- PostGIS: https://postgis.net/documentation/
- Redis: https://redis.io/docs/
- NGINX: https://nginx.org/en/docs/
- GeoPandas: https://geopandas.org/
- FastAPI: https://fastapi.tiangolo.com/

**Community**:
- Stack Overflow
- PostgreSQL Community
- Python Discord/IRC
- IDRM GitHub Issues

---

**Prerequisites Complete? ✅ Proceed to environment-specific setup!** 🚀
