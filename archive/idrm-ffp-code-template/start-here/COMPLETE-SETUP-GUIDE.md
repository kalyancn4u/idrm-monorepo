# IDRM Complete Setup Guide

## From Zero to Running — Development, Staging, and Production

**Version**: 3.0**Stack**: Bun · Python 3.11 (Miniconda) · PostgreSQL 16 + PostGIS 3.4 · Redis 7.2**Platforms**: HTML/Tailwind (5173) · React SPA (5174) · React Native (Expo)

> For deep dives see:
>
> - Development details: [docs/IDRM-DEVELOPMENT-GUIDE.md](../docs/IDRM-DEVELOPMENT-GUIDE.md)
> - Staging/Production: [docs/IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md)

---

## Table of Contents

1. [Quick Hardware Requirements](#1-quick-hardware-requirements)
2. [Installing the v3 Stack](#2-installing-the-v3-stack)
3. [Clone and Configure the Project](#3-clone-and-configure-the-project)
4. [Start Development (5-Terminal Approach)](#4-start-development-5-terminal-approach)
5. [Staging Setup (Docker)](#5-staging-setup-docker)
6. [Production Setup Overview](#6-production-setup-overview)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Quick Hardware Requirements

| Environment | CPU        | RAM       | Storage    |
| ----------- | ---------- | --------- | ---------- |
| Development | 8-12 cores | 16-32 GB  | 150 GB SSD |
| Staging     | 16 cores   | 32-48 GB  | 300 GB SSD |
| Production  | 32+ cores  | 64-128 GB | 1 TB NVMe  |

**OS**: Ubuntu 22.04 LTS recommended. Windows: use WSL2.

**Required ports**: 3000 (Bun gateway), 5173 (HTML/Tailwind), 5174 (React SPA), 8000 (FastAPI), 5432 (PostgreSQL), 6379 (Redis)

---

## 2. Installing the v3 Stack

> **Critical**: Bun replaces Node.js/npm. Miniconda replaces venv. No Java/GeoServer.

### 2.1 System Essentials

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y \
  build-essential curl wget git gnupg lsb-release \
  libpq-dev libgdal-dev libgeos-dev libproj-dev jq \
  python3-pip net-tools
```

### 2.2 Bun Runtime

```bash
curl -fsSL https://bun.sh/install | bash
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

bun --version    # 1.0.0+
bun add -g typescript@latest vite@latest
```

### 2.3 Python 3.11 via Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc

conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

pip install --break-system-packages \
  fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic \
  python-jose[cryptography] passlib[bcrypt] python-multipart \
  redis geopandas shapely gdal fiona pyproj pytest pytest-cov httpx
```

### 2.4 PostgreSQL 16 + PostGIS 3.4

```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16 postgresql-16-postgis-3

sudo systemctl start postgresql && sudo systemctl enable postgresql

sudo -u postgres psql << 'EOF'
CREATE USER idrm_user WITH PASSWORD 'idrm_secure_password_2024';
CREATE DATABASE idrm_db OWNER idrm_user;
\c idrm_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO idrm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO idrm_user;
EOF
```

### 2.5 Redis 7.2

```bash
sudo apt install -y redis-server
# In /etc/redis/redis.conf: set supervised=systemd and bind=127.0.0.1
sudo systemctl start redis && sudo systemctl enable redis
redis-cli ping    # PONG
```

### 2.6 Expo CLI (React Native — optional)

```bash
bun add -g expo-cli eas-cli
expo login
```

---

## 3. Clone and Configure the Project

```bash
mkdir -p ~/projects && cd ~/projects
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp
```

### 3.1 Backend Environment

```bash
cd src/backend/app-python
cat > .env << 'EOF'
DATABASE_URL=postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key-change-in-production-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,exp://192.168.1.100:19000
ENVIRONMENT=development
DEBUG=true
EOF
chmod 600 .env

conda activate idrm-mvp
alembic upgrade head    # Apply DB migrations
```

### 3.2 API Gateway Environment

```bash
cd ../src/backend/api-gateway
bun install

cat > .env << 'EOF'
BACKEND_URL=http://localhost:8000
FRONTEND_HTML_URL=http://localhost:5173
FRONTEND_SPA_URL=http://localhost:5174
PORT=3000
NODE_ENV=development
WS_ENABLED=true
WS_PORT=3001
EOF
```

### 3.3 Frontend Environments

```bash
# HTML/Tailwind
cd src/frontend/web-html
bun install
echo "export const API_URL = 'http://localhost:3000/api/v1';" > src/config.js

# React SPA
cd ../web-react
bun install

# React Native (use your LAN IP)
cd ../mobile-expo
bun install
# Edit src/config.ts with your LAN IP from: ip addr show | grep "inet "
```

---

## 4. Start Development (5-Terminal Approach)

| # | Terminal      | Command                                                                                           |
| - | ------------- | ------------------------------------------------------------------------------------------------- |
| 1 | Backend       | `cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000` |
| 2 | API Gateway   | `cd src/backend/api-gateway && bun run dev`                                                     |
| 3 | HTML/Tailwind | `cd src/frontend/web-html && bun run dev`                                                       |
| 4 | React SPA     | `cd src/frontend/web-react && bun run dev`                                                      |
| 5 | React Native  | `cd src/frontend/mobile-expo && npx expo start`                                                 |

**PostgreSQL and Redis start automatically** as systemd services — no terminal needed.

### Quick Verification

```bash
curl http://localhost:8000/health    # {"status": "healthy"}
curl http://localhost:3000/health    # {"status": "ok"}
# Open http://localhost:5173 → HTML/Tailwind
# Open http://localhost:5174 → React SPA admin
```

### 🚩 Ports the stack uses (and the firewall)

Ports: **8000** backend · **3000/3001** gateway (HTTP/WebSocket) · **5173** HTML · **5174** React SPA · **5432** PostgreSQL · **6379** Redis.

🚩 **For same-machine development you do NOT need to open the firewall.** The browser reaches `localhost:<port>` over the loopback interface, which `ufw` never blocks — just start the apps.

```bash
# Are the ports free before you start?  (no output = all free)
sudo ss -tulpn | grep -E ':(3000|3001|8000|5173|5174|5432|6379)\b'
# Free a stuck port:
sudo fuser -k 8000/tcp        # or simply Ctrl+C the terminal running it
```

🚩 To reach a dev server from **another device** (e.g. your phone): start it on all interfaces (`uvicorn --host 0.0.0.0`, `vite --host`; the Bun gateway already listens widely), then `sudo ufw allow 5173/tcp`. **Never** open `5432`/`6379` (your database/Redis).

> 🚩 Beginner-friendly deep dive — checking/opening/freeing ports, `ufw`, reaching the box from the LAN, and running **dev → staging → production on one Ubuntu host** — is in **`docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`**.

### Automated Start Script

```bash
# Save as dev-start-v3.sh in project root — see IDRM-DEVELOPMENT-GUIDE.md for full script
chmod +x dev-start-v3.sh
./dev-start-v3.sh
```

---

## 5. Staging Setup (Docker)

Staging uses Docker Compose with all services containerized.

```bash
# Prerequisites: Docker + Docker Compose installed
# docker-compose.staging.yml covers postgres, redis, backend, api-gateway, frontend-web, frontend-admin, nginx

cp .env.staging.example .env.staging
# Edit .env.staging with staging values

docker-compose -f docker-compose.staging.yml up -d
docker-compose -f docker-compose.staging.yml exec backend alembic upgrade head

# Verify
curl https://staging.idrm.example.com/health
```

For the complete Docker Compose file with all Dockerfiles and NGINX config, see [docs/IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md) — Staging section.

---

## 6. Production Setup Overview

Production runs on a cloud server (DigitalOcean, AWS, or GCP) with:

- SSL/TLS via Certbot (Let's Encrypt)
- Prometheus + Grafana + Loki monitoring
- Automated backups (hourly → daily → weekly → monthly, uploaded to S3)
- Blue-green deployment via GitHub Actions CI/CD

**Minimum production tiers**:

| Tier   | Server            | Monthly Cost     | Users     |
| ------ | ----------------- | ---------------- | --------- |
| Tier 1 | 4 vCPU / 8 GB     | ~$96/month       | < 10,000  |
| Tier 2 | 8 vCPU / 16 GB    | ~$192/month      | < 50,000  |
| Tier 3 | Multi-server + LB | $500-1,000/month | < 200,000 |

For full server provisioning, SSL, CI/CD, and monitoring setup, see [docs/IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md) — Production section.

---

## 7. Verification Checklist

### Automated Prerequisites Check

Save as `verify-prerequisites.sh` in the project root and run before starting:

```bash
#!/bin/bash
# verify-prerequisites.sh — IDRM v3 stack verification

echo "=== IDRM v3 Prerequisites Verification ==="
echo ""

check() {
  if eval "$1" &>/dev/null; then
    echo "✅  $2: $(eval "$3")"
  else
    echo "❌  $2 NOT found — install from: $4"
  fi
}

check "command -v bun"       "Bun"          "bun --version"            "https://bun.sh"
check "command -v conda"     "Conda"        "conda --version"          "https://docs.conda.io/en/latest/miniconda.html"
check "conda activate idrm-mvp && python --version" \
                             "Python 3.11"  "python --version"         "conda create -n idrm-mvp python=3.11"
check "command -v psql"      "PostgreSQL"   "psql --version"           "apt install postgresql-16"
check "psql -U postgres -tAc \"SELECT PostGIS_Version();\"" \
                             "PostGIS 3.4"  "psql -U postgres -tAc 'SELECT PostGIS_Version();'" \
                                                                       "apt install postgresql-16-postgis-3"
check "command -v redis-cli" "Redis"        "redis-cli --version"      "apt install redis-server"

echo ""
echo "Services (run after starting stack):"
curl -sf http://localhost:8000/health && echo "✅  FastAPI  (8000)" || echo "⚠️  FastAPI  (8000) — not running"
curl -sf http://localhost:3000/health && echo "✅  Bun GW   (3000)" || echo "⚠️  Bun GW   (3000) — not running"
redis-cli ping &>/dev/null           && echo "✅  Redis    (6379)" || echo "⚠️  Redis    (6379) — not running"

echo ""
echo "=== Done ==="
```

```bash
chmod +x verify-prerequisites.sh
./verify-prerequisites.sh
```

### Development Ready

- [ ] `bun --version` shows 1.0.0+
- [ ] `conda activate idrm-mvp && python --version` shows Python 3.11.x
- [ ] `psql --version` shows 16.x
- [ ] `redis-cli ping` returns PONG
- [ ] `curl http://localhost:8000/health` returns `{"status": "healthy"}`
- [ ] `curl http://localhost:3000/health` returns OK
- [ ] `http://localhost:5173` loads HTML/Tailwind app
- [ ] `http://localhost:5174` loads React SPA admin

### Staging Ready

- [ ] All containers healthy: `docker-compose ps`
- [ ] DB migrations applied: `alembic current`
- [ ] NGINX serving all three frontends
- [ ] SSL certificates active
- [ ] WebSocket connections working

### Production Ready

- [ ] Monitoring dashboards active (Grafana)
- [ ] Automated backups verified
- [ ] Blue-green deploy tested once
- [ ] All GitHub Actions secrets configured
- [ ] Pre-launch security checklist complete (see IDRM-DEPLOYMENT-GUIDE.md)

---

## 8. Common Troubleshooting

### Port already in use

```bash
# Who is on the port? (works for any IDRM port)
sudo ss -tulpn | grep ':8000'                               # or: sudo lsof -i :8000
# Free it — pick the one that matches:
sudo fuser -k 8000/tcp                                      # a native dev process (or Ctrl+C its terminal)
docker compose -f infra/docker/full-stack.yml down          # a Docker (staging/prod) container
sudo systemctl stop postgresql redis-server                 # the system DB/Redis (to free 5432/6379 for Docker)
```

🚩 On one machine, **dev / staging / production share the same ports — run one at a time.**
Full guide: **`docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`**.

### Database connection fails

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection directly
psql -U idrm_user -d idrm_db -c "SELECT 1;"

# Verify DATABASE_URL in src/backend/app-python/.env
```

### PostGIS functions not found

```bash
psql -U idrm_user -d idrm_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -U idrm_user -d idrm_db -c "SELECT PostGIS_Version();"
```

### Python package import error

```bash
# Ensure the right conda env is active
conda activate idrm-mvp
conda list | grep <package-name>

# Reinstall if missing
pip install --break-system-packages <package-name>
```

### Redis not responding

```bash
redis-cli ping          # Should return PONG
sudo systemctl restart redis
redis-cli ping
```

### Bun gateway can't reach FastAPI

```bash
# Verify FastAPI is up
curl http://localhost:8000/health

# Verify BACKEND_URL in src/backend/api-gateway/.env
# Should be: BACKEND_URL=http://localhost:8000
```

### Geospatial GDAL library error on import

```bash
# Reinstall geospatial stack through conda (not pip)
conda install -c conda-forge geopandas gdal fiona pyproj shapely -y
```

---

**See also**: [CLAUDE.md](../CLAUDE.md) for daily commands quick reference

### Key Documents

| Document                                                           | When to Read                              |
| ------------------------------------------------------------------ | ----------------------------------------- |
| [CLAUDE.md](../CLAUDE.md)                                             | Daily reference — API examples, commands |
| [COMPLETE-BEGINNERS-GUIDE.md](COMPLETE-BEGINNERS-GUIDE.md)            | First time setup                          |
| [COMPLETE-API-SPECS-GUIDE.md](COMPLETE-API-SPECS-GUIDE.md)            | Building or calling any API               |
| [COMPLETE-DATABASE-GUIDE.md](COMPLETE-DATABASE-GUIDE.md)              | Database queries, schema                  |
| [COMPLETE-DevSecOps-GUIDE.md](COMPLETE-DevSecOps-GUIDE.md)            | Writing tests, code review                |
| [docs/IDRM-ARCHITECTURE-GUIDE.md](../docs/IDRM-ARCHITECTURE-GUIDE.md) | Understanding system design               |
| [docs/IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md)     | Deploying to staging/production           |
