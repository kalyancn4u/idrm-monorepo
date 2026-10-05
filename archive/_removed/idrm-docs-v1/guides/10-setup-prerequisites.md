> *Type: Guide (novice / how-to) · Audience: Novices, DevOps · Status: Archived — v1 historical generation*

# IDRM Platform Setup Prerequisites

<!-- IDRM-CLEANUP doc=v1-g10-prereq status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — setup guide → superseded
> Gen-1 setup guide. Current MVP setup = [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + the installer `../../../scripts/setup-idrm-ubuntu.sh` + guides [`linux-101`](../../../../guides/mvp/learn/linux-101.md),
> [`postgresql-postgis-101`](../../../../guides/mvp/learn/postgresql-postgis-101.md), [`git-github-101`](../../../../guides/mvp/learn/git-github-101.md).
> MVP prerequisites = Ubuntu + PostgreSQL/PostGIS + MinIO + Miniconda (no Node/Docker). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

> Complete checklist of requirements before setting up IDRM platform in any environment

## Table of Contents

1. [System Requirements](#system-requirements)
2. [Required Software](#required-software)
3. [Domain & DNS Setup](#domain--dns-setup)
4. [Access Requirements](#access-requirements)
5. [Pre-Installation Checklist](#pre-installation-checklist)

---

## System Requirements

### Minimum Hardware Requirements

**Development (Monolith)**:
```
CPU: 4 cores
RAM: 8 GB
Storage: 50 GB SSD
Network: 100 Mbps
```

**Staging (Docker)**:
```
CPU: 4 cores
RAM: 16 GB
Storage: 100 GB SSD
Network: 100 Mbps
```

**Production (Docker)**:
```
CPU: 8 cores (recommended 16)
RAM: 32 GB (recommended 64 GB)
Storage: 200 GB SSD (NVMe recommended)
Network: 1 Gbps
```

### Operating System

**Supported**:
- Ubuntu 22.04 LTS (Recommended)
- Ubuntu 24.04 LTS
- Debian 12

**NOT Supported**:
- CentOS/RHEL (different package management)
- Windows Server
- macOS Server

### Verify Your System

```bash
# Check OS version
cat /etc/os-release

# Check CPU cores
nproc

# Check RAM
free -h

# Check disk space
df -h

# Check network
ip addr show
```

---

## Required Software

### Core Dependencies (All Environments)

#### 1. System Updates
```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Essential Build Tools
```bash
sudo apt install -y \
  curl \
  wget \
  git \
  build-essential \
  software-properties-common \
  apt-transport-https \
  ca-certificates \
  gnupg \
  lsb-release \
  unzip \
  vim \
  nano \
  htop
```

#### 3. Bun Runtime (MANDATORY)
```bash
# Install Bun (latest version)
curl -fsSL https://bun.sh/install | bash

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.bun/bin:$PATH"

# Verify installation
bun --version
# Should show: bun 1.x.x
```

#### 4. Python 3.11+
```bash
# Add deadsnakes PPA for latest Python
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.11
sudo apt install -y python3.11 python3.11-venv python3.11-dev

# Install pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.11

# Verify
python3.11 --version
pip3.11 --version
```

#### 5. PostgreSQL 16 + PostGIS
```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update

# Install PostgreSQL 16
sudo apt install -y postgresql-16 postgresql-contrib-16 postgresql-16-postgis-3

# Verify
sudo -u postgres psql --version
# Should show: psql (PostgreSQL) 16.x
```

#### 6. Redis
```bash
# Install Redis
sudo apt install -y redis-server

# Verify
redis-cli --version
# Should show: redis-cli 7.x or 6.x
```

#### 7. NGINX
```bash
# Install NGINX
sudo apt install -y nginx

# Verify
nginx -v
# Should show: nginx version: nginx/1.x
```

---

### Docker (Staging & Production Only)

#### 1. Install Docker
```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Verify
docker --version
docker compose version
```

#### 2. Configure Docker
```bash
# Add current user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Apply group changes (or logout/login)
newgrp docker

# Test Docker
docker run hello-world

# Enable Docker to start on boot
sudo systemctl enable docker
```

---

### Java (for GeoServer)

```bash
# Install OpenJDK 11 (required for GeoServer)
sudo apt install -y openjdk-11-jdk

# Verify
java -version
# Should show: openjdk version "11.x"

# Set JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64' >> ~/.bashrc
source ~/.bashrc
```

---

## Domain & DNS Setup

### Production Requirements

**You Need**:
1. A registered domain name (e.g., `idrm.gov.in` or `yourdomain.com`)
2. Access to DNS management panel
3. SSL certificate (Let's Encrypt - free)

### DNS Configuration

**Required DNS Records**:

```
Type    Name              Value                    TTL
A       @                 <YOUR_SERVER_IP>         3600
A       www               <YOUR_SERVER_IP>         3600
A       api               <YOUR_SERVER_IP>         3600
A       geoserver         <YOUR_SERVER_IP>         3600
CNAME   www               yourdomain.com           3600
```

**Example for `idrm.example.com`**:
```
A       @                 203.0.113.1              3600
A       api               203.0.113.1              3600
A       geoserver         203.0.113.1              3600
```

**Verify DNS Propagation**:
```bash
# Check A record
dig yourdomain.com +short

# Check specific subdomain
dig api.yourdomain.com +short

# Wait 5-60 minutes for DNS propagation
```

---

## Access Requirements

### 1. Server Access

**SSH Key Setup** (Recommended):
```bash
# Generate SSH key (on your local machine)
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy to server
ssh-copy-id username@server_ip

# Test connection
ssh username@server_ip
```

### 2. Firewall Ports

**Required Open Ports**:

```
Port    Service           Environment
22      SSH              All (secure it!)
80      HTTP             All
443     HTTPS            All
3000    API Gateway      Development only
5432    PostgreSQL       Development only (NEVER production)
6379    Redis            Development only (NEVER production)
8080    GeoServer        Development only (proxy via NGINX in production)
```

**Configure UFW** (Production):
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (IMPORTANT - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status
```

### 3. Sudo Access

Verify you have sudo access:
```bash
sudo whoami
# Should output: root
```

---

## Pre-Installation Checklist

### Before Starting Setup

**System Checks**:
- [ ] Ubuntu 22.04+ installed
- [ ] Minimum hardware requirements met
- [ ] System fully updated (`sudo apt update && sudo apt upgrade`)
- [ ] Stable internet connection
- [ ] SSH access configured
- [ ] Sudo privileges confirmed

**Software Checks**:
- [ ] Bun installed and in PATH
- [ ] Python 3.11+ installed
- [ ] PostgreSQL 16 installed
- [ ] Redis installed
- [ ] NGINX installed
- [ ] Java 11 installed (for GeoServer)
- [ ] Docker installed (Staging/Production only)

**Network Checks** (Production):
- [ ] Domain name registered
- [ ] DNS A records configured
- [ ] DNS propagated (verify with `dig`)
- [ ] Firewall configured
- [ ] Port 80/443 accessible from internet

**Security Checks**:
- [ ] SSH key authentication set up
- [ ] Root login disabled
- [ ] Password authentication disabled (optional but recommended)
- [ ] Fail2Ban installed (Production)
- [ ] UFW enabled (Production)

**Project Setup**:
- [ ] Git repository access
- [ ] Environment variables prepared
- [ ] Database credentials chosen
- [ ] JWT secret generated
- [ ] API keys obtained (if any)

---

## Environment Variables Template

Create this file for reference:

**`.env.example`**:
```bash
# Database
DB_USER=idrm_user
DB_PASSWORD=CHANGE_ME_SECURE_PASSWORD_HERE
DB_NAME=idrm_db
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# API Gateway
PORT=3000
NODE_ENV=development
JWT_SECRET=CHANGE_ME_RANDOM_STRING_64_CHARS
JWT_EXPIRATION=3600
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# GeoServer
GEOSERVER_URL=http://localhost:8080/geoserver
GEOSERVER_ADMIN_USER=admin
GEOSERVER_ADMIN_PASSWORD=CHANGE_ME_GEOSERVER_PASSWORD

# Frontend
VITE_API_URL=http://localhost:3000/api/v1
VITE_WS_URL=ws://localhost:3000
VITE_GEOSERVER_URL=http://localhost:8080/geoserver

# Production-specific
DOMAIN=idrm.example.com
SSL_EMAIL=admin@idrm.example.com
```

---

## Password & Secret Generation

### Generate Secure Passwords

```bash
# Generate random password (32 chars)
openssl rand -base64 32

# Generate JWT secret (64 chars)
openssl rand -hex 64

# Generate UUID
uuidgen
```

**Store Securely**:
- Use password manager (1Password, Bitwarden, LastPass)
- Never commit to Git
- Use `.env` files (add to `.gitignore`)

---

## Verification Commands

### Quick Health Check

```bash
# System
uname -a
lsb_release -a

# Software versions
bun --version
python3.11 --version
psql --version
redis-cli --version
nginx -v
java -version
docker --version  # Staging/Production only

# Services
sudo systemctl status postgresql
sudo systemctl status redis-server
sudo systemctl status nginx

# Network
ip addr show
curl -I http://localhost
```

---

## Common Issues & Solutions

### Issue 1: Bun not in PATH
**Solution**:
```bash
# Add to ~/.bashrc
echo 'export PATH="$HOME/.bun/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: PostgreSQL not starting
**Solution**:
```bash
# Check logs
sudo journalctl -u postgresql -n 50

# Restart service
sudo systemctl restart postgresql

# Check status
sudo systemctl status postgresql
```

### Issue 3: Permission denied (Docker)
**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

### Issue 4: Port already in use
**Solution**:
```bash
# Find what's using the port
sudo lsof -i :3000

# Kill the process
sudo kill -9 <PID>
```

---

## Next Steps

After completing prerequisites:

1. **Development**: Follow `idrm-instructions_setup_monolith.md`
2. **Staging**: Follow `idrm-instructions_setup_staging.md`
3. **Production**: Follow `idrm-instructions_setup_production.md`

---

## Support & Resources

**Official Documentation**:
- Bun: https://bun.sh/docs
- PostgreSQL: https://www.postgresql.org/docs/16/
- PostGIS: https://postgis.net/documentation/
- Redis: https://redis.io/docs/
- NGINX: https://nginx.org/en/docs/
- Docker: https://docs.docker.com/

**Community**:
- Stack Overflow
- PostgreSQL IRC/Discord
- IDRM Project GitHub Issues

---

**Prerequisites completed? Proceed to environment-specific setup guides!** 🚀
