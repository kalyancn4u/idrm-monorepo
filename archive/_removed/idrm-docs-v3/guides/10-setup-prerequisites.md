# IDRM v3 · Prerequisites & Installation

<!-- IDRM-CLEANUP doc=v3-g10-prereq status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — setup → current
> MVP setup = [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + installer `../../../scripts/setup-idrm-ubuntu.sh` + [`linux-101`](../../../../guides/mvp/learn/linux-101.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: Novices, DevOps · Status: Archived — v3 historical generation*
*Consolidated from: 01-PREREQUISITES.md, setup-prerequisites-v3.md*

## Contents
- [IDRM: Prerequisites & Installation Guide](#idrm-prerequisites--installation-guide)
- [IDRM Platform Setup Prerequisites v3.0](#idrm-platform-setup-prerequisites-v30)

---

## IDRM: Prerequisites & Installation Guide

### Complete Software Requirements for All Environments

**Version**: 3.0 Consolidated  
**Audience**: Technical users (developers, DevOps)  
**Reading Time**: 20-30 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Overview](#1-overview)
2. [Hardware Requirements](#2-hardware-requirements)
3. [Operating System](#3-operating-system)
4. [Core Software Stack](#4-core-software-stack)
5. [Installation Instructions](#5-installation-instructions)
6. [Verification & Testing](#6-verification--testing)
7. [Optional Components](#7-optional-components)
8. [Production-Specific Requirements](#8-production-specific-requirements)
9. [Common Issues & Troubleshooting](#9-common-issues--troubleshooting)
10. [Next Steps](#10-next-steps)

---

### 1. **Overview**

#### 1.1 What This Document Covers

This guide helps you install **all required software** for IDRM platform development, staging, or production deployment.

**After completing this guide**, you'll have:
- ✅ Operating system verified
- ✅ All required software installed
- ✅ System verified and ready
- ✅ Clear next steps for your environment

#### 1.2 Technology Stack (v2.0 Final)

**CRITICAL**: This is the **official v2.0 stack**. Do NOT use alternatives!

```
┌─────────────────────────────────────────┐
│     IDRM Technology Stack v2.0          │
├─────────────────────────────────────────┤
│                                         │
│  1. NGINX 1.24+     (Reverse Proxy)    │
│  2. Bun 1.x         (API Gateway)      │
│     ❌ NOT Node.js                      │
│                                         │
│  3. Python 3.11     (Backend Services) │
│     via Miniconda                       │
│     ❌ NOT venv or virtualenv           │
│                                         │
│  4. PostgreSQL 16   (Database)         │
│     + PostGIS 3.4   (Geospatial)       │
│                                         │
│  5. Redis 7.2+      (Cache/Sessions)   │
│                                         │
│  6. Docker 24.x     (Staging/Prod)     │
│     ❌ NOT needed for development       │
│                                         │
└─────────────────────────────────────────┘
```

#### 1.3 Environment-Specific Requirements

| Component | Development | Staging | Production |
|-----------|-------------|---------|------------|
| **NGINX** | ✅ Yes | ✅ Yes | ✅ Yes |
| **Bun** | ✅ Yes | ✅ Yes (in Docker) | ✅ Yes (in Docker) |
| **Python/Miniconda** | ✅ Yes | ✅ Yes (in Docker) | ✅ Yes (in Docker) |
| **PostgreSQL** | ✅ Yes (native) | ✅ Yes (Docker) | ✅ Yes (Docker) |
| **Redis** | ✅ Yes (native) | ✅ Yes (Docker) | ✅ Yes (Docker) |
| **Docker** | ❌ Optional | ✅ Required | ✅ Required |
| **SSL Certificate** | ❌ No | ⚠️ Optional | ✅ Required |
| **Domain Name** | ❌ No | ⚠️ Optional | ✅ Required |

---

### 2. **Hardware Requirements**

#### 2.1 By Environment

##### **Development Environment** (Native Ubuntu)

```
Minimum Requirements:
├─ CPU:     4 cores (Intel i5 or equivalent)
├─ RAM:     8 GB
├─ Storage: 100 GB SSD
└─ Network: 100 Mbps

Recommended:
├─ CPU:     8 cores (Intel i7 or AMD Ryzen 7)
├─ RAM:     16 GB
├─ Storage: 250 GB NVMe SSD
└─ Network: 1 Gbps
```

**Why these specs?**
- PostgreSQL + PostGIS need ~2GB RAM
- Miniconda environment ~1GB RAM
- Bun + services ~2GB RAM
- OS + IDE ~3GB RAM
- **Total**: 8GB minimum, 16GB comfortable

##### **Staging Environment** (Docker)

```
Minimum Requirements:
├─ CPU:     8 cores
├─ RAM:     16 GB
├─ Storage: 200 GB SSD
└─ Network: 100 Mbps

Recommended:
├─ CPU:     16 cores
├─ RAM:     32 GB
├─ Storage: 500 GB NVMe SSD
└─ Network: 1 Gbps
```

**Why these specs?**
- Docker overhead ~2GB RAM
- Multiple containers ~10GB RAM
- Database + cache ~4GB RAM
- **Total**: 16GB minimum, 32GB recommended

##### **Production Environment** (Docker + Security)

```
Minimum Requirements:
├─ CPU:     16 cores
├─ RAM:     32 GB
├─ Storage: 500 GB NVMe SSD
├─ Network: 1 Gbps
└─ Backup:  500 GB (separate storage)

Recommended:
├─ CPU:     32 cores
├─ RAM:     64 GB
├─ Storage: 1 TB NVMe SSD
├─ Network: 10 Gbps
└─ Backup:  1 TB (separate storage + offsite)
```

**Why these specs?**
- 10,000 concurrent users target
- High availability requirements
- Backup and monitoring overhead
- Production safety margins

#### 2.2 Verify Your Hardware

```bash
## Check OS version
lsb_release -a
## Expected: Ubuntu 22.04 or 24.04 LTS

## Check CPU cores
nproc
## Expected: 4+ (dev), 8+ (staging), 16+ (prod)

## Check RAM
free -h
## Expected: 8GB+ (dev), 16GB+ (staging), 32GB+ (prod)

## Check disk space
df -h /
## Expected: 100GB+ (dev), 200GB+ (staging), 500GB+ (prod)

## Check disk type (SSD recommended)
lsblk -d -o name,rota
## rota=0 means SSD, rota=1 means HDD

## Check network interface
ip addr show
ip link show
```

---

### 3. **Operating System**

#### 3.1 Supported Operating Systems

**✅ Officially Supported**:

| OS | Version | Status | Recommended |
|----|---------| -------|-------------|
| **Ubuntu** | 22.04 LTS (Jammy) | ✅ Tested | ⭐ **YES** |
| **Ubuntu** | 24.04 LTS (Noble) | ✅ Tested | ⭐ **YES** |
| **Debian** | 12 (Bookworm) | ✅ Compatible | ⚠️ Advanced users |

**❌ NOT Supported**:
- CentOS / RHEL (different package manager)
- Windows Server (not Linux)
- macOS Server (not Linux)
- Ubuntu < 22.04 (too old)
- Any non-LTS Ubuntu versions

#### 3.2 Why Ubuntu 22.04/24.04?

**Reasons**:
1. **Long Term Support** - 5 years of updates
2. **Package Availability** - All required packages available
3. **Community Support** - Large community, easy to find help
4. **Docker Support** - Official Docker support
5. **Production Ready** - Used by many production systems

#### 3.3 Fresh Installation Recommended

**If possible**, start with a **fresh Ubuntu installation**:
- Clean environment = fewer conflicts
- Known starting point = easier troubleshooting
- Security = no legacy vulnerabilities

**If using existing Ubuntu**:
- Make sure it's up to date: `sudo apt update && sudo apt upgrade`
- Back up important data first
- Be prepared for potential conflicts

#### 3.4 System Updates

```bash
## Update package lists
sudo apt update

## Upgrade all packages
sudo apt upgrade -y

## Remove unused packages
sudo apt autoremove -y

## Clean package cache
sudo apt autoclean

## Reboot if kernel was updated
sudo reboot
```

---

### 4. **Core Software Stack**

#### 4.1 Required Components Overview

```
Installation Order (recommended):

1. System Essentials      (build tools, git, etc.)
   ↓
2. Bun Runtime           (API Gateway)
   ↓
3. Miniconda + Python    (Backend services)
   ↓
4. PostgreSQL + PostGIS  (Database)
   ↓
5. Redis                 (Cache/Sessions)
   ↓
6. NGINX                 (Reverse proxy)
   ↓
7. Docker                (Staging/Production only)
```

**Estimated Total Time**:
- Development: 60-90 minutes
- Staging: 45-60 minutes (Docker simplifies some steps)
- Production: 90-120 minutes (includes security setup)

#### 4.2 Why Each Component?

| Component | Purpose | Why This Choice |
|-----------|---------|-----------------|
| **Bun** | API Gateway, WebSocket | 3-4x faster than Node.js, built-in TypeScript |
| **Python/Miniconda** | Backend services | Better for geospatial libs (GDAL, GEOS) |
| **PostgreSQL + PostGIS** | Database + Geospatial | 4-5x faster geospatial queries than MongoDB |
| **Redis** | Cache, sessions, pub/sub | Industry standard, very fast |
| **NGINX** | Reverse proxy, load balancer | Production-grade, highly efficient |
| **Docker** | Containerization | Consistency across staging/production |

**More Details**: See [11-ARCHITECTURE-DECISIONS.md](11-ARCHITECTURE-DECISIONS.md)

---

### 5. **Installation Instructions**

#### 5.1 System Essentials

**Install build tools and utilities**:

```bash
## Update system first
sudo apt update && sudo apt upgrade -y

## Install essential packages
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
  dnsutils \
  openssl

## Verify key tools
gcc --version        # Should show: gcc (Ubuntu ...)
git --version        # Should show: git version 2.x
curl --version       # Should show: curl 7.x or 8.x
```

**Time**: 5-10 minutes

---

#### 5.2 Bun Runtime Installation

**⚠️ CRITICAL**: Install Bun, **NOT Node.js**!

```bash
## Install Bun (single command)
curl -fsSL https://bun.sh/install | bash

## Configure PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

## Make permanent (add to shell config)
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc

## Reload shell configuration
source ~/.bashrc

## Verify installation
bun --version
## Expected output: 1.x.x or higher

## Test Bun
bun --help
## Should show help text

## Quick test
echo "console.log('Hello from Bun!')" > test.js
bun run test.js
## Should print: Hello from Bun!
rm test.js
```

**Time**: 2-3 minutes

**Troubleshooting**:
- If `bun: command not found` → Reload shell: `source ~/.bashrc`
- If still not found → Check `echo $PATH` includes `.bun/bin`

**DO NOT INSTALL**: ❌ Node.js, ❌ npm, ❌ yarn, ❌ pnpm

---

#### 5.3 Miniconda + Python 3.11

**⚠️ CRITICAL**: Use Miniconda, **NOT venv or virtualenv**!

**Why Miniconda?** Better for geospatial libraries (GDAL, GEOS, PROJ).

```bash
## Download Miniconda installer
cd /tmp
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

## Verify download (optional but recommended)
sha256sum Miniconda3-latest-Linux-x86_64.sh
## Compare with official checksum from https://docs.conda.io/

## Install Miniconda
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

## Initialize conda for bash
$HOME/miniconda3/bin/conda init bash

## Reload shell
source ~/.bashrc

## Verify conda installation
conda --version
## Expected: conda 23.x or 24.x

## Update conda itself
conda update -n base -c defaults conda -y

## Create IDRM environment with Python 3.11
conda create -n idrm-mvp python=3.11 -y

## Activate environment
conda activate idrm-mvp

## Verify Python version
python --version
## Expected: Python 3.11.x

## Verify environment
which python
## Expected: /home/YOUR_USER/miniconda3/envs/idrm-mvp/bin/python
```

**Time**: 5-10 minutes

**Install Geospatial Libraries** (via conda-forge):

```bash
## Make sure idrm-mvp environment is active
conda activate idrm-mvp

## Install geospatial core libraries
conda install -c conda-forge -y \
  geopandas=0.14.1 \
  shapely=2.0.2 \
  fiona=1.9.5 \
  pyproj=3.6.1 \
  rasterio=1.3.9 \
  gdal=3.8.0 \
  mercantile=1.2.1

## Verify geospatial installations
python -c "import geopandas; print('GeoPandas:', geopandas.__version__)"
python -c "import shapely; print('Shapely:', shapely.__version__)"
python -c "from osgeo import gdal; print('GDAL:', gdal.__version__)"
python -c "import mercantile; print('Mercantile:', mercantile.__version__)"

## All should print versions without errors
```

**Time**: 10-15 minutes (conda resolves dependencies)

**Install FastAPI & Database Libraries** (via pip):

```bash
## Still in idrm-mvp environment
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

## Verify FastAPI
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import uvicorn; print('Uvicorn:', uvicorn.__version__)"
python -c "import sqlalchemy; print('SQLAlchemy:', sqlalchemy.__version__)"

## Should all print versions
```

**Time**: 5-10 minutes

**Total Miniconda Setup Time**: 20-35 minutes

**DO NOT USE**: ❌ `python3 -m venv`, ❌ `virtualenv`, ❌ `pipenv`

---

#### 5.4 PostgreSQL 16 + PostGIS 3.4

**Install PostgreSQL 16 with PostGIS extension**:

```bash
## Add PostgreSQL official repository
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/postgresql-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/postgresql-archive-keyring.gpg] \
  http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | \
  sudo tee /etc/apt/sources.list.d/pgdg.list

## Update package lists
sudo apt update

## Install PostgreSQL 16 + PostGIS 3.4
sudo apt install -y \
  postgresql-16 \
  postgresql-contrib-16 \
  postgresql-16-postgis-3 \
  postgresql-16-postgis-3-scripts \
  postgis

## Start and enable PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

## Verify installation
psql --version
## Expected: psql (PostgreSQL) 16.x

## Check PostgreSQL service status
sudo systemctl status postgresql
## Should show: active (running)
```

**Time**: 5-10 minutes

**Configure PostgreSQL for IDRM**:

```bash
## Switch to postgres user
sudo -u postgres psql

## Inside PostgreSQL shell, create database and user:
CREATE DATABASE idrm_db;
CREATE USER idrm_user WITH ENCRYPTED PASSWORD 'idrm_secure_password_2024';
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;

## Enable PostGIS extension
\c idrm_db
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

## Verify PostGIS
SELECT PostGIS_version();
## Should show: 3.4.x

## Grant schema permissions
GRANT ALL ON SCHEMA public TO idrm_user;

## Exit PostgreSQL shell
\q
```

**Configure PostgreSQL for network access** (if needed):

```bash
## Edit postgresql.conf
sudo nano /etc/postgresql/16/main/postgresql.conf

## Find and change:
## listen_addresses = 'localhost'  →  listen_addresses = '*'
## (Only for development; production should use specific IPs)

## Edit pg_hba.conf for password authentication
sudo nano /etc/postgresql/16/main/pg_hba.conf

## Add this line for local connections:
## host    all             all             127.0.0.1/32            scram-sha-256

## Restart PostgreSQL
sudo systemctl restart postgresql
```

**Test database connection**:

```bash
## Connect to database
psql -h localhost -U idrm_user -d idrm_db

## Inside psql:
SELECT version();
SELECT PostGIS_version();
\q

## Should connect successfully and show versions
```

**Time**: 5-10 minutes configuration

**Total PostgreSQL Setup Time**: 10-20 minutes

---

#### 5.5 Redis Installation

```bash
## Install Redis
sudo apt install -y redis-server redis-tools

## Start and enable Redis service
sudo systemctl start redis-server
sudo systemctl enable redis-server

## Verify installation
redis-cli --version
## Expected: redis-cli 7.x (or 6.x on Ubuntu 22.04)

## Check Redis service
sudo systemctl status redis-server
## Should show: active (running)

## Test Redis
redis-cli ping
## Expected output: PONG

## Quick functionality test
redis-cli set test "Hello IDRM"
redis-cli get test
## Should return: "Hello IDRM"

redis-cli del test
## Cleanup test key
```

**Time**: 2-3 minutes

**Configure Redis** (optional, for production):

```bash
## Edit Redis configuration
sudo nano /etc/redis/redis.conf

## Recommended changes:
## 1. Set password (find 'requirepass'):
##    requirepass your_redis_password_here
#
## 2. Bind to localhost only (find 'bind'):
##    bind 127.0.0.1
#
## 3. Set max memory (find 'maxmemory'):
##    maxmemory 2gb
##    maxmemory-policy allkeys-lru

## Restart Redis after changes
sudo systemctl restart redis-server

## Test with password
redis-cli -a your_redis_password_here ping
## Should return: PONG
```

---

#### 5.6 NGINX Installation

```bash
## Install NGINX
sudo apt install -y nginx

## Start and enable NGINX service
sudo systemctl start nginx
sudo systemctl enable nginx

## Verify installation
nginx -v
## Expected: nginx version: nginx/1.24.x or 1.22.x

## Check NGINX service
sudo systemctl status nginx
## Should show: active (running)

## Test NGINX
curl -I http://localhost
## Expected: HTTP/1.1 200 OK

## Or open in browser: http://localhost
## Should show: "Welcome to nginx!"
```

**Time**: 2-3 minutes

**NGINX will be configured later** during environment setup.

---

#### 5.7 Docker Installation (Staging & Production ONLY)

**⚠️ Skip this for Development** (native setup is faster)

```bash
## Remove old Docker versions (if any)
sudo apt remove docker docker-engine docker.io containerd runc 2>/dev/null || true

## Install prerequisites
sudo apt install -y ca-certificates curl gnupg lsb-release

## Add Docker's official GPG key
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

## Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

## Install Docker Engine
sudo apt update
sudo apt install -y \
  docker-ce \
  docker-ce-cli \
  containerd.io \
  docker-buildx-plugin \
  docker-compose-plugin

## Add your user to docker group
sudo usermod -aG docker $USER

## Apply group changes (logout/login or use newgrp)
newgrp docker

## Enable Docker to start on boot
sudo systemctl enable docker

## Verify installation
docker --version
## Expected: Docker version 24.x or higher

docker compose version
## Expected: Docker Compose version v2.x

## Test Docker
docker run hello-world
## Should download and run successfully, print "Hello from Docker!"
```

**Time**: 5-10 minutes

---

### 6. **Verification & Testing**

#### 6.1 Complete System Check

Run this comprehensive verification script:

```bash
#!/bin/bash
## IDRM Prerequisites Verification Script

echo "========================================="
echo "IDRM Prerequisites Verification"
echo "========================================="
echo ""

## Function to check command existence
check_command() {
    if command -v $1 &> /dev/null; then
        echo "✅ $1: $(which $1)"
        $1 $2 2>/dev/null || true
    else
        echo "❌ $1: NOT FOUND"
    fi
    echo ""
}

## System Info
echo "📊 System Information"
echo "-------------------"
lsb_release -a 2>/dev/null
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $2 " total, " $4 " available"}')"
echo ""

## Check all required software
echo "📦 Software Versions"
echo "-------------------"
check_command "gcc" "--version | head -1"
check_command "git" "--version"
check_command "bun" "--version"
check_command "conda" "--version"
check_command "python" "--version"
check_command "psql" "--version"
check_command "redis-cli" "--version"
check_command "nginx" "-v"
check_command "docker" "--version"

## Check Python environment
echo "🐍 Python Environment"
echo "-------------------"
if [ "$CONDA_DEFAULT_ENV" = "idrm-mvp" ]; then
    echo "✅ idrm-mvp environment active"
    python -c "import fastapi, geopandas, sqlalchemy; print('✅ Key libraries installed')" 2>/dev/null || echo "❌ Some Python libraries missing"
else
    echo "⚠️  idrm-mvp environment not active"
    echo "   Run: conda activate idrm-mvp"
fi
echo ""

## Check services
echo "🔧 Service Status"
echo "-------------------"
systemctl is-active postgresql &>/dev/null && echo "✅ PostgreSQL: running" || echo "❌ PostgreSQL: not running"
systemctl is-active redis-server &>/dev/null && echo "✅ Redis: running" || echo "❌ Redis: not running"
systemctl is-active nginx &>/dev/null && echo "✅ NGINX: running" || echo "❌ NGINX: not running"
echo ""

## Network checks
echo "🌐 Network Connectivity"
echo "-------------------"
curl -s -o /dev/null -w "✅ Internet: %{http_code}\n" https://www.google.com || echo "❌ Internet: not accessible"
redis-cli ping &>/dev/null && echo "✅ Redis: responding" || echo "❌ Redis: not responding"
psql -h localhost -U idrm_user -d idrm_db -c "SELECT 1;" &>/dev/null && echo "✅ PostgreSQL: accessible" || echo "⚠️  PostgreSQL: check credentials"
echo ""

echo "========================================="
echo "Verification Complete!"
echo "========================================="
```

**Save and run**:

```bash
## Save script
cat > ~/verify-idrm-prereqs.sh << 'EOF'
[paste script above]
EOF

## Make executable
chmod +x ~/verify-idrm-prereqs.sh

## Run verification
~/verify-idrm-prereqs.sh
```

#### 6.2 Expected Output

**All checks should show ✅**:

```
✅ gcc: installed
✅ git: installed
✅ bun: 1.x.x
✅ conda: 24.x.x
✅ python: 3.11.x
✅ psql: 16.x
✅ redis-cli: 7.x or 6.x
✅ nginx: 1.24.x or 1.22.x
✅ docker: 24.x (if installed)
✅ idrm-mvp environment active
✅ Key libraries installed
✅ PostgreSQL: running
✅ Redis: running
✅ NGINX: running
```

#### 6.3 Quick Individual Tests

**Test Bun**:
```bash
bun --version && echo "✅ Bun OK" || echo "❌ Bun FAIL"
```

**Test Python environment**:
```bash
conda activate idrm-mvp
python -c "import fastapi, geopandas, sqlalchemy; print('✅ Python OK')" || echo "❌ Python FAIL"
```

**Test PostgreSQL**:
```bash
psql -h localhost -U idrm_user -d idrm_db -c "SELECT PostGIS_version();" && echo "✅ PostgreSQL OK" || echo "❌ PostgreSQL FAIL"
```

**Test Redis**:
```bash
redis-cli ping && echo "✅ Redis OK" || echo "❌ Redis FAIL"
```

**Test NGINX**:
```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "200" && echo "✅ NGINX OK" || echo "❌ NGINX FAIL"
```

---

### 7. **Optional Components**

#### 7.1 Development Tools

**VS Code / VSCodium** (recommended code editor):

```bash
## VSCodium (open-source VS Code)
wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | \
  gpg --dearmor | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg

echo 'deb [signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg] \
  https://download.vscodium.com/debs vscodium main' | \
  sudo tee /etc/apt/sources.list.d/vscodium.list

sudo apt update
sudo apt install -y codium

## Or official VS Code
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] \
  https://packages.microsoft.com/repos/code stable main" | \
  sudo tee /etc/apt/sources.list.d/vscode.list
sudo apt update
sudo apt install -y code
```

**DBeaver** (database GUI):

```bash
wget -O /tmp/dbeaver.deb https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb
sudo dpkg -i /tmp/dbeaver.deb
sudo apt install -f -y  # Fix dependencies if needed
```

**HTTPie** (API testing):

```bash
conda activate idrm-mvp
pip install httpie
```

**Postman** (alternative API testing):

```bash
wget -O /tmp/postman.tar.gz https://dl.pstmn.io/download/latest/linux64
sudo tar -xzf /tmp/postman.tar.gz -C /opt
sudo ln -s /opt/Postman/Postman /usr/local/bin/postman
```

#### 7.2 Monitoring Tools (Production)

**Prometheus + Grafana** (to be configured later):

```bash
## Will be set up during production deployment
## See: 32-PRODUCTION-DEPLOYMENT.md
```

---

### 8. **Production-Specific Requirements**

#### 8.1 Domain Name & DNS

**Required for Production**:
1. Registered domain (e.g., `idrm.gov.in` or `idrm.example.com`)
2. Access to DNS management
3. Email address for SSL certificates

**DNS Configuration**:

```
Type    Name              Value                TTL
---------------------------------------------------
A       @                 YOUR_SERVER_IP       3600
A       www               YOUR_SERVER_IP       3600
A       api               YOUR_SERVER_IP       3600
```

**Verify DNS**:
```bash
dig yourdomain.com +short
## Should return: YOUR_SERVER_IP

dig api.yourdomain.com +short
## Should return: YOUR_SERVER_IP
```

**DNS Propagation**: Wait 5-60 minutes for global propagation.

#### 8.2 SSL Certificate

**Let's Encrypt (Free)** - Will be configured during production setup:

```bash
## Certbot will be installed during production setup
## See: 32-PRODUCTION-DEPLOYMENT.md for SSL configuration
```

#### 8.3 Firewall Configuration

**Production firewall rules**:

```bash
## Install UFW (Uncomplicated Firewall)
sudo apt install -y ufw

## Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

## Allow SSH (change port if using non-standard)
sudo ufw allow 22/tcp

## Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

## Enable firewall
sudo ufw enable

## Check status
sudo ufw status verbose
```

**⚠️ Important**: Configure firewall BEFORE enabling to avoid locking yourself out!

#### 8.4 Backup Storage

**Configure separate backup storage**:
- Separate drive/partition for backups
- Offsite backup location (cloud storage)
- Automated backup scripts (configured during production setup)

---

### 9. **Common Issues & Troubleshooting**

#### 9.1 Bun Installation Issues

**Problem**: `bun: command not found`

**Solution**:
```bash
## Reload shell configuration
source ~/.bashrc

## Or manually add to PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

## Check if Bun exists
ls -la $HOME/.bun/bin/bun
```

**Problem**: Permission denied during installation

**Solution**:
```bash
## Don't use sudo for Bun installation
## It should install to user home directory
```

#### 9.2 Miniconda Issues

**Problem**: Conda not found after installation

**Solution**:
```bash
## Manually initialize conda
~/miniconda3/bin/conda init bash
source ~/.bashrc
```

**Problem**: Conda environment activation fails

**Solution**:
```bash
## Check if environment exists
conda env list

## Create if missing
conda create -n idrm-mvp python=3.11 -y

## Activate
conda activate idrm-mvp
```

**Problem**: Geospatial library installation fails

**Solution**:
```bash
## Use conda-forge channel explicitly
conda install -c conda-forge geopandas shapely fiona -y

## If still fails, try updating conda
conda update -n base -c defaults conda -y
```

#### 9.3 PostgreSQL Issues

**Problem**: Cannot connect to PostgreSQL

**Solution 1** - Check service:
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**Solution 2** - Check authentication:
```bash
## Edit pg_hba.conf
sudo nano /etc/postgresql/16/main/pg_hba.conf

## Ensure this line exists:
## host    all             all             127.0.0.1/32            scram-sha-256

## Restart PostgreSQL
sudo systemctl restart postgresql
```

**Problem**: PostGIS extension not found

**Solution**:
```bash
## Reinstall PostGIS
sudo apt install --reinstall postgresql-16-postgis-3 -y

## Then in psql:
CREATE EXTENSION IF NOT EXISTS postgis;
```

#### 9.4 Redis Issues

**Problem**: Redis not starting

**Solution**:
```bash
## Check logs
sudo journalctl -u redis-server -n 50

## Common issue: Port already in use
sudo lsof -i :6379

## If another Redis running, stop it
sudo systemctl stop redis-server
sudo systemctl start redis-server
```

**Problem**: Connection refused

**Solution**:
```bash
## Check if Redis is listening
sudo netstat -tlnp | grep 6379

## Check Redis configuration
sudo nano /etc/redis/redis.conf
## Ensure: bind 127.0.0.1
## Restart after changes
sudo systemctl restart redis-server
```

#### 9.5 NGINX Issues

**Problem**: Port 80 already in use

**Solution**:
```bash
## Check what's using port 80
sudo lsof -i :80

## If Apache is running
sudo systemctl stop apache2
sudo systemctl disable apache2

## Start NGINX
sudo systemctl start nginx
```

**Problem**: Permission denied errors

**Solution**:
```bash
## Check NGINX user
ps aux | grep nginx

## Fix permissions
sudo chown -R www-data:www-data /var/www
sudo chmod -R 755 /var/www
```

#### 9.6 Docker Issues

**Problem**: Permission denied when running docker

**Solution**:
```bash
## Add user to docker group
sudo usermod -aG docker $USER

## Logout and login, or use:
newgrp docker

## Test
docker run hello-world
```

**Problem**: Docker service not starting

**Solution**:
```bash
## Check Docker service
sudo systemctl status docker

## Check logs
sudo journalctl -u docker -n 50

## Restart Docker
sudo systemctl restart docker
```

---

### 10. **Next Steps**

#### 10.1 Prerequisites Complete Checklist

Before proceeding, verify:

- [ ] Operating system: Ubuntu 22.04 or 24.04 LTS
- [ ] Hardware meets requirements for your environment
- [ ] System essentials installed (gcc, git, curl, etc.)
- [ ] Bun installed and working (`bun --version`)
- [ ] Miniconda installed with idrm-mvp environment
- [ ] Python 3.11 in idrm-mvp environment
- [ ] Geospatial libraries installed (geopandas, shapely, etc.)
- [ ] FastAPI and dependencies installed
- [ ] PostgreSQL 16 installed and running
- [ ] PostGIS 3.4 extension enabled
- [ ] Redis installed and running
- [ ] NGINX installed and running
- [ ] Docker installed (if staging/production)
- [ ] All verification tests pass ✅

#### 10.2 What to Do Next

**Choose your environment path**:

##### **For Development Setup** (Native Ubuntu):
→ Read: [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md)  
→ Time: 2-3 hours  
→ You'll build: Complete native development environment

##### **For Staging Setup** (Docker):
→ Read: [31-STAGING-SETUP.md](31-STAGING-SETUP.md)  
→ Time: 1-2 hours  
→ You'll build: Docker-based staging environment

##### **For Production Setup** (Docker + Security):
→ Read: [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)  
→ Time: 3-4 hours  
→ You'll build: Production-ready secure deployment

#### 10.3 Additional Reading

**Understand the architecture**:
→ [10-SYSTEM-ARCHITECTURE.md](10-SYSTEM-ARCHITECTURE.md) - System design overview

**Understand requirements**:
→ [20-FUNCTIONAL-SPECIFICATION.md](20-FUNCTIONAL-SPECIFICATION.md) - What the system does

**Understand why we chose these technologies**:
→ [11-ARCHITECTURE-DECISIONS.md](11-ARCHITECTURE-DECISIONS.md) - Technology rationale

---

### ✅ **Summary**

You now have:
- ✅ Complete understanding of prerequisites
- ✅ All required software installed
- ✅ System verified and ready
- ✅ Clear next steps for your environment

**Installation Time Summary**:
- **Development**: 60-90 minutes total
- **Staging**: 45-60 minutes total
- **Production**: 90-120 minutes total

**You're ready to proceed with environment setup!** 🚀

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite  
**Previous**: [00-GETTING-STARTED.md](00-GETTING-STARTED.md)  
**Next**: [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md) or [31-STAGING-SETUP.md](31-STAGING-SETUP.md) or [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)  
**Feedback**: Open an issue or submit a PR on GitHub

---

## IDRM Platform Setup Prerequisites v3.0

### Complete Requirements for Multi-Platform Development

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Stack**: Bun + Python (Miniconda) + PostgreSQL + PostGIS + Redis

---

### 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Required Software](#required-software)
3. [Platform-Specific Requirements](#platform-specific-requirements)
4. [Development Tools](#development-tools)
5. [Pre-Installation Checklist](#pre-installation-checklist)

---

### 🖥️ System Requirements

#### Hardware Requirements by Environment

**Development (Native Ubuntu) - Three Frontends**:
```
CPU:    8-12 cores (running 5 dev servers simultaneously)
RAM:    16-32 GB (Backend + 3 frontends + IDE + browser)
Storage: 150 GB SSD (node_modules + Python packages + Android SDK)
Network: 100 Mbps
GPU:    Optional (for React Native Android emulator)
```

**Staging (Docker) - All Platforms**:
```
CPU:    16 cores
RAM:    32-48 GB
Storage: 300 GB SSD
Network: 1 Gbps
```

**Production (Cloud + CI/CD)**:
```
CPU:    32+ cores (recommended)
RAM:    64-128 GB (recommended)
Storage: 1 TB NVMe SSD
Network: 10 Gbps
Backup:  1 TB (separate storage)
```

#### Operating System

**Supported** ✅:
- Ubuntu 22.04 LTS (Jammy) - **Recommended for v3**
- Ubuntu 24.04 LTS (Noble)
- Debian 12 (Bookworm)

**NOT Supported** ❌:
- Ubuntu < 22.04
- CentOS/RHEL
- Windows (use WSL2 with Ubuntu 22.04)
- macOS (not tested for production)

#### Verify Your System

```bash
## Check OS version
lsb_release -a
## Should show: Ubuntu 22.04 or 24.04

## Check CPU cores (need 8+ for v3)
nproc
## Should show: 8+ for dev, 16+ for staging, 32+ for production

## Check RAM (need 16GB+ for v3)
free -h
## Should show: 16GB+ for dev, 32GB+ for staging, 64GB+ for production

## Check disk space
df -h /
## Should show: 150GB+ for dev, 300GB+ for staging, 1TB+ for production

## Check available disk I/O
sudo hdparm -Tt /dev/sda
## Should show: >100 MB/sec for SSD
```

---

### 📦 Required Software

#### Core Stack (v3.0 - Three Frontends)

```
1. ✅ NGINX (Reverse Proxy)
2. ✅ Bun 1.x (API Gateway + Frontend Build) - NOT Node.js!
3. ✅ Python 3.11 via Miniconda - NOT venv!
4. ✅ Redis 7.2+ (Cache + Pub/Sub)
5. ✅ Python Geospatial Service - NOT Java GeoServer!
6. ✅ PostgreSQL 16 + PostGIS 3.4
7. ✅ Expo CLI (for React Native)
8. ✅ Android Studio (optional - for Android dev)
9. ✅ Xcode (macOS only - for iOS dev)
```

---

#### 1. System Essentials

```bash
## Update system first
sudo apt update && sudo apt upgrade -y

## Install build tools
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
  dnsutils \
  python3-pip \
  libpq-dev \
  libgdal-dev \
  libgeos-dev \
  libproj-dev

## Verify
gcc --version     # Should show: 11.x or 12.x
git --version     # Should show: 2.34+
python3 --version # Should show: 3.10+
```

---

#### 2. Bun Runtime (CRITICAL for v3)

**Why Bun for v3**: 
- 3-4x faster than Node.js
- Built-in TypeScript support
- Handles API Gateway + all frontend builds
- WebSocket server for real-time updates

```bash
## Install Bun
curl -fsSL https://bun.sh/install | bash

## Add to PATH
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

## Make permanent
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

## Verify installation
bun --version
## Should show: 1.0.0 or higher

## Test Bun
bun run -b "console.log('Bun works!')"
## Should print: Bun works!

## Install global packages
bun add -g typescript@latest
bun add -g vite@latest
```

**IMPORTANT**: Do NOT install Node.js or npm! Bun replaces both.

---

#### 3. Python 3.11 via Miniconda (CRITICAL for v3)

**Why Miniconda**:
- Better for geospatial packages (GDAL, GeoPandas)
- Isolated environments
- Reproducible via environment.yml
- Industry standard for data/ML work

```bash
## Download Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

## Install
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

## Initialize
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc

## Verify
conda --version
## Should show: conda 23.x or higher

## Create IDRM environment
conda create -n idrm-mvp python=3.11 -y

## Activate
conda activate idrm-mvp

## Install core packages
pip install --break-system-packages \
  fastapi \
  uvicorn[standard] \
  sqlalchemy \
  psycopg2-binary \
  alembic \
  python-jose[cryptography] \
  passlib[bcrypt] \
  python-multipart \
  redis \
  geopandas \
  shapely \
  gdal \
  fiona \
  pyproj

## Verify
python --version  # Should show: Python 3.11.x
pip list | grep fastapi
```

**IMPORTANT**: Use `--break-system-packages` flag for all pip installs in Miniconda!

---

#### 4. PostgreSQL 16 + PostGIS 3.4

```bash
## Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

## Update and install
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16

## Install PostGIS
sudo apt install -y postgresql-16-postgis-3

## Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

## Verify
sudo systemctl status postgresql
psql --version  # Should show: psql (PostgreSQL) 16.x

## Create database and user
sudo -u postgres psql << EOF
CREATE USER idrm_user WITH PASSWORD 'idrm_secure_password_2024';
CREATE DATABASE idrm_db OWNER idrm_user;
\c idrm_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;
EOF

## Test connection
psql -U idrm_user -d idrm_db -c "SELECT PostGIS_version();"
```

---

#### 5. Redis 7.2+ (NEW in v3)

**Why Redis**:
- Session caching
- API response caching
- Real-time pub/sub for all three frontends
- Rate limiting

```bash
## Install Redis
sudo apt install -y redis-server

## Configure Redis
sudo nano /etc/redis/redis.conf
## Set: supervised systemd
## Set: bind 127.0.0.1

## Start Redis
sudo systemctl start redis
sudo systemctl enable redis

## Verify
redis-cli ping
## Should return: PONG

## Test
redis-cli set test "Hello Redis"
redis-cli get test
## Should return: "Hello Redis"
```

---

#### 6. Expo CLI (for React Native)

```bash
## Install Expo CLI globally with Bun
bun add -g expo-cli
bun add -g eas-cli

## Verify
expo --version
eas --version

## Login to Expo (create account if needed)
expo login

## Test
expo whoami
## Should show your Expo username
```

---

#### 7. Android Studio (Optional - for Android Development)

**Only needed if developing React Native Android app**

```bash
## Download Android Studio
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz

## Extract
sudo tar -xzf android-studio-*-linux.tar.gz -C /opt/

## Add to PATH
echo 'export ANDROID_HOME=$HOME/Android/Sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/emulator' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/platform-tools' >> ~/.bashrc
source ~/.bashrc

## Install required packages
sudo apt install -y libc6:i386 libncurses5:i386 libstdc++6:i386 lib32z1 libbz2-1.0:i386

## Run Android Studio
/opt/android-studio/bin/studio.sh

## Install via Android Studio:
## - Android SDK
## - Android SDK Platform
## - Android Virtual Device (AVD)
```

---

### 🎨 Platform-Specific Requirements

#### HTML/Tailwind Frontend

**Required**:
- ✅ Bun (already installed)
- ✅ Modern browser (Chrome, Firefox, Safari)

**Packages** (installed per-project):
```bash
cd frontend/html-tailwind
bun install
## Installs: vite, tailwindcss, autoprefixer, postcss
```

---

#### React SPA Frontend

**Required**:
- ✅ Bun (already installed)
- ✅ Modern browser with React DevTools

**Packages** (installed per-project):
```bash
cd frontend/react-spa
bun install
## Installs: react, react-dom, react-router-dom, vite, tailwindcss
```

---

#### React Native Mobile

**Required**:
- ✅ Expo CLI (already installed)
- ✅ Expo Go app on phone (for testing)
- ✅ Android Studio OR Xcode (for emulators)

**For iOS Development (macOS only)**:
```bash
## Install Xcode from App Store
## Install Xcode Command Line Tools
xcode-select --install

## Install CocoaPods
sudo gem install cocoapods
```

**For Android Development**:
- Android Studio (already installed above)
- Android SDK Platform 33+
- Android Virtual Device (AVD)

**Packages** (installed per-project):
```bash
cd mobile
bun install
## Installs: expo, react-native, react-navigation, etc.
```

---

### 🛠️ Development Tools

#### Essential IDEs & Editors

**VSCode/VSCodium** (Recommended):
```bash
## Install VSCodium (open-source VSCode)
wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | gpg --dearmor | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://paulcarroty.gitlab.io/vscodium-deb-rpm-repo/debs vscodium main' | sudo tee /etc/apt/sources.list.d/vscodium.list
sudo apt update && sudo apt install -y codium

## Or install official VSCode
sudo snap install code --classic

## Install extensions
code --install-extension dbaeumer.vscode-eslint
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-azuretools.vscode-docker
```

#### Database Tools

**DBeaver** (Recommended):
```bash
sudo snap install dbeaver-ce
```

**pgAdmin 4** (Alternative):
```bash
curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'
sudo apt update
sudo apt install -y pgadmin4-desktop
```

#### API Testing

**HTTPie** (Command-line):
```bash
sudo apt install -y httpie

## Test
http GET http://localhost:8000/health
```

**Bruno** (GUI - Postman alternative):
```bash
sudo snap install bruno
```

#### Additional Tools

```bash
## JSON processor
sudo apt install -y jq

## Redis CLI
## Already installed with redis-server

## Git UI
sudo snap install gitkraken --classic

## Docker (for staging)
sudo apt install -y docker.io docker-compose
sudo usermod -aG docker $USER

## NGINX
sudo apt install -y nginx
```

---

### 🔐 Access Requirements

#### Required Accounts

**For Development**:
1. ✅ GitHub account (code repository)
2. ✅ Expo account (React Native deployment)
3. ✅ npm account (optional - for publishing packages)

**For Staging/Production**:
1. ✅ Cloud provider account (AWS, Google Cloud, or DigitalOcean)
2. ✅ Domain registrar account
3. ✅ SSL certificate (Let's Encrypt free tier)
4. ✅ SendGrid/Mailgun (email notifications)
5. ✅ Twilio (SMS notifications - optional)
6. ✅ Apple Developer ($99/year - for iOS app)
7. ✅ Google Play Console ($25 one-time - for Android app)

#### SSH Keys

```bash
## Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

## Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

## Copy public key
cat ~/.ssh/id_ed25519.pub
## Add to GitHub, server, etc.
```

---

### ✅ Pre-Installation Checklist

#### System Checklist

- [ ] Ubuntu 22.04+ installed and updated
- [ ] 16GB+ RAM available
- [ ] 150GB+ disk space free
- [ ] Internet connection stable (100 Mbps+)
- [ ] User has sudo privileges
- [ ] Firewall configured (ports 3000, 5173, 5174, 8000, 5432, 6379)

#### Software Checklist

- [ ] Bun installed (`bun --version` works)
- [ ] Miniconda installed (`conda --version` works)
- [ ] PostgreSQL 16 installed and running
- [ ] PostGIS extension enabled
- [ ] Redis installed and running
- [ ] Git configured (`git config --list`)
- [ ] Expo CLI installed (if doing React Native)
- [ ] Android Studio installed (if doing Android)

#### Development Environment Checklist

- [ ] VSCode/VSCodium installed
- [ ] Database tools installed (DBeaver or pgAdmin)
- [ ] API testing tools installed (HTTPie or Bruno)
- [ ] Terminal customized (oh-my-zsh recommended)
- [ ] SSH keys generated and added to GitHub
- [ ] Docker installed (for staging)

#### Multi-Platform Checklist (v3)

- [ ] Can run 5 terminal windows simultaneously
- [ ] Browser supports React DevTools
- [ ] Phone available for React Native testing (optional)
- [ ] Emulators configured (Android/iOS)
- [ ] Network allows WebSocket connections
- [ ] Localhost ports available: 3000, 5173, 5174, 8000-8004, 5432, 6379

---

### 🚀 Quick Verification Script

Save as `verify-prerequisites-v3.sh`:

```bash
#!/bin/bash

echo "IDRM v3 Prerequisites Verification"
echo "=================================="
echo ""

## System
echo "1. System Info:"
lsb_release -a | grep Description
echo "CPU Cores: $(nproc)"
echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
echo "Disk: $(df -h / | tail -1 | awk '{print $4}')"
echo ""

## Bun
echo "2. Bun:"
bun --version || echo "❌ Bun not installed"
echo ""

## Python/Conda
echo "3. Python/Miniconda:"
conda --version || echo "❌ Conda not installed"
python --version || echo "❌ Python not found"
echo ""

## PostgreSQL
echo "4. PostgreSQL:"
psql --version || echo "❌ PostgreSQL not installed"
sudo systemctl status postgresql --no-pager | grep Active
echo ""

## Redis
echo "5. Redis:"
redis-cli --version || echo "❌ Redis not installed"
redis-cli ping || echo "❌ Redis not running"
echo ""

## Expo
echo "6. Expo CLI:"
expo --version || echo "⚠️  Expo not installed (optional for React Native)"
echo ""

## Git
echo "7. Git:"
git --version || echo "❌ Git not installed"
echo ""

echo "=================================="
echo "Verification Complete!"
echo ""
echo "✅ = Installed and working"
echo "❌ = Not installed or not working"
echo "⚠️  = Optional, not critical"
```

```bash
## Run verification
chmod +x verify-prerequisites-v3.sh
./verify-prerequisites-v3.sh
```

---

### 📊 Resource Usage Estimates

#### Development (All 5 Terminals Running)

```
Backend (Python/FastAPI):    100-150 MB
API Gateway (Bun):           50-80 MB
HTML/Tailwind (Vite):        80-120 MB
React SPA (Vite):            100-150 MB
React Native (Expo):         200-300 MB
PostgreSQL:                  150-200 MB
Redis:                       30-50 MB
VSCode:                      300-500 MB
Chrome DevTools:             500-800 MB
Android Emulator (optional): 1-2 GB
───────────────────────────────────────
TOTAL:                       1.5-4.5 GB
```

Your 16-32GB RAM system will handle this comfortably!

---

### 🔧 Troubleshooting Common Issues

#### Bun won't install
```bash
## Try manual installation
mkdir -p ~/.bun
curl -fsSL https://bun.sh/install | bash -s "bun-v1.0.0"
```

#### Miniconda conflicts with system Python
```bash
## This is normal! Use conda environments
conda activate idrm-mvp
which python  # Should show: /home/user/miniconda3/envs/idrm-mvp/bin/python
```

#### PostgreSQL won't start
```bash
sudo systemctl status postgresql
sudo journalctl -u postgresql -n 50
## Check port 5432 not in use
sudo lsof -i :5432
```

#### Redis permission denied
```bash
sudo chown redis:redis /var/lib/redis
sudo systemctl restart redis
```

#### Expo can't connect to phone
```bash
## Make sure phone and laptop on same WiFi
## Check firewall allows port 19000
sudo ufw allow 19000
```

---

### 🎯 Next Steps

After completing prerequisites:

1. **Development Setup**: Follow `setup-monolith-development-v3.md`
2. **Staging Setup**: Follow `setup-staging-v3.md` (Docker)
3. **Production Setup**: Follow `setup-production-v3.md` (CI/CD)

---

**IDRM v3 Prerequisites: Complete Stack for Multi-Platform Development!** 🚀

**Required Time**: 2-3 hours for full setup  
**Platforms**: All three frontends ready  
**Next**: Start development with `setup-monolith-development-v3.md`
