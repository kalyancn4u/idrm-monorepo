# IDRM Development Guide
## Setting Up & Working with the Multi-Platform Development Environment

**Version**: 3.0  
**Stack**: Bun + Python 3.11 (Miniconda) + PostgreSQL 16 + PostGIS 3.4 + Redis 7.2  
**Platforms**: HTML/Tailwind (Port 5173) · React SPA (Port 5174) · React Native (Expo)  
**Approach**: Native services (no Docker in dev), hot reload, instant feedback

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Installing Prerequisites](#2-installing-prerequisites)
3. [Project Structure](#3-project-structure)
4. [Backend Setup](#4-backend-setup-pythonfastapi)
5. [API Gateway Setup](#5-api-gateway-setup-bun)
6. [Frontend Setup](#6-frontend-setup-three-platforms)
7. [Running All Services (5-Terminal Approach)](#7-running-all-services-5-terminal-approach)
8. [Development Workflow](#8-development-workflow)
9. [Running Tests](#9-running-tests)
10. [Troubleshooting](#10-troubleshooting)
11. [Jupyter Notebooks](#11-jupyter-notebooks)
12. [Email & PDF Templates (Jinja2)](#12-email--pdf-templates-jinja2)

---

## 1. System Requirements

### Hardware

| Environment | CPU | RAM | Storage | Network |
|-------------|-----|-----|---------|---------|
| Development (native, 5 dev servers) | 8-12 cores | 16-32 GB | 150 GB SSD | 100 Mbps |
| Staging (Docker, all platforms) | 16 cores | 32-48 GB | 300 GB SSD | 1 Gbps |
| Production (cloud + CI/CD) | 32+ cores | 64-128 GB | 1 TB NVMe SSD | 10 Gbps |

### Operating System

**Supported**:
- Ubuntu 22.04 LTS (Jammy) — recommended
- Ubuntu 24.04 LTS (Noble)
- Debian 12 (Bookworm)
- Windows: use WSL2 with Ubuntu 22.04

**Not supported**: Ubuntu < 22.04, CentOS/RHEL, macOS (not tested for production)

### Verify Your System

```bash
lsb_release -a          # Ubuntu 22.04 or 24.04
nproc                   # 8+ cores for dev
free -h                 # 16 GB+ RAM
df -h /                 # 150 GB+ free disk
```

### Resource Usage (All 5 Terminals Running)

```
Backend (Python/FastAPI):     100-150 MB
API Gateway (Bun):             50-80 MB
HTML/Tailwind (Vite):          80-120 MB
React SPA (Vite):             100-150 MB
React Native (Expo):          200-300 MB
PostgreSQL:                   150-200 MB
Redis:                         30-50 MB
VSCode:                       300-500 MB
Chrome:                       500-800 MB
──────────────────────────────────────────
TOTAL:                       1.5-2.5 GB
```

Your 16-32 GB machine has plenty of headroom.

---

## 2. Installing Prerequisites

> **v3 stack — do not substitute**:
> - `bun` — NOT Node.js / npm
> - `conda` (Miniconda) — NOT `python -m venv`
> - Python geospatial module inside the monolith (port 8000) — NOT Java / GeoServer

### 2.1 System Essentials

```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y \
  build-essential software-properties-common apt-transport-https \
  ca-certificates curl wget git gnupg lsb-release \
  unzip zip vim nano htop net-tools dnsutils \
  python3-pip libpq-dev libgdal-dev libgeos-dev libproj-dev jq
```

### 2.2 Bun Runtime

```bash
curl -fsSL https://bun.sh/install | bash

# Make permanent
echo 'export BUN_INSTALL="$HOME/.bun"' >> ~/.bashrc
echo 'export PATH="$BUN_INSTALL/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

bun --version    # 1.0.0+

# Global packages
bun add -g typescript@latest vite@latest
```

Do **not** install Node.js separately — Bun replaces it.

### 2.3 Python 3.11 via Miniconda

```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3
$HOME/miniconda3/bin/conda init bash
source ~/.bashrc

conda --version    # 23.x+

# Create project environment
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

# Install Python dependencies
pip install --break-system-packages \
  fastapi uvicorn[standard] sqlalchemy psycopg2-binary alembic \
  python-jose[cryptography] passlib[bcrypt] python-multipart \
  redis geopandas shapely gdal fiona pyproj \
  pytest pytest-cov httpx

python --version   # Python 3.11.x
```

### 2.4 PostgreSQL 16 + PostGIS 3.4

```bash
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt update
sudo apt install -y postgresql-16 postgresql-contrib-16 postgresql-16-postgis-3

sudo systemctl start postgresql
sudo systemctl enable postgresql

psql --version    # psql (PostgreSQL) 16.x

# Create database and user
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

# Verify PostGIS
psql -U idrm_user -d idrm_db -c "SELECT PostGIS_version();"
```

### 2.5 Redis 7.2

```bash
sudo apt install -y redis-server

sudo nano /etc/redis/redis.conf
# Set: supervised systemd
# Set: bind 127.0.0.1

sudo systemctl start redis
sudo systemctl enable redis

redis-cli ping    # PONG
```

### 2.6 Expo CLI (React Native — optional)

```bash
bun add -g expo-cli eas-cli
expo login        # Create an Expo account if needed
expo whoami       # Verify login
```

### 2.7 Development Tools

**IDE (VSCode)**:
```bash
sudo snap install code --classic

code --install-extension dbaeumer.vscode-eslint
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

**Database GUI**:
```bash
sudo snap install dbeaver-ce    # Recommended
```

**API testing**:
```bash
sudo apt install -y httpie      # CLI: http GET http://localhost:8000/health
sudo snap install bruno         # GUI alternative to Postman
```

### 2.8 Prerequisites Verification

```bash
#!/bin/bash
echo "IDRM v3 Prerequisites Verification"
echo "=================================="

echo "Bun:"; bun --version || echo "Not installed"
echo "Conda:"; conda --version || echo "Not installed"
echo "Python (in conda env):"; python --version 2>/dev/null || echo "Activate idrm-mvp env first"
echo "PostgreSQL:"; psql --version || echo "Not installed"
echo "PostGIS:"; psql -U idrm_user -d idrm_db -c "SELECT PostGIS_version();" 2>/dev/null || echo "Not enabled"
echo "Redis:"; redis-cli ping || echo "Not running"
echo "Expo CLI:"; expo --version 2>/dev/null || echo "Not installed (optional)"
echo "Git:"; git --version || echo "Not installed"
echo "=================================="
```

Required ports that must all be free before starting: `3000`, `3001`, `5173`, `5174`, `8000`, `5432`, `6379`.

> 🚩 **Ports & firewall (local dev).** Same-machine dev needs **no firewall** — the browser reaches `localhost:<port>` over loopback, which `ufw` never blocks. Quick checks:
>
> ```bash
> sudo ss -tulpn | grep -E ':(3000|3001|8000|5173|5174|5432|6379)\b'   # what's in use?
> sudo fuser -k 8000/tcp        # free a stuck port (or Ctrl+C its terminal)
> ```
>
> To reach a dev server from your **phone/another device**, make it listen on `0.0.0.0` (`uvicorn --host 0.0.0.0`, `vite --host`) and `sudo ufw allow <port>/tcp`. Full beginner guide — incl. **dev → staging → production on one Ubuntu host** — is in **`docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`**.

---

## 3. Project Structure

```
idrm-mvp/
│
├── src/
│   ├── backend/
│   │   ├── api-gateway/              # Bun TypeScript gateway (port 3000)
│   │   │   ├── src/
│   │   │   │   ├── index.ts          # Main server — rate limiting, CORS, proxy
│   │   │   │   ├── middleware/       # cors, rateLimit, auth, security, logger
│   │   │   │   ├── routes/           # api.ts (proxy), static.ts
│   │   │   │   └── utils/            # redis.ts, jwt.ts, config.ts
│   │   │   ├── package.json
│   │   │   ├── tsconfig.json
│   │   │   └── bun.lockb
│   │   │
│   │   ├── app-python/               # Python FastAPI — Modular Monolith (port 8000)
│   │   │   ├── api/                  # Route handlers (auth, services, geo, analytics)
│   │   │   ├── core/                 # Config, DB connection, Redis, security
│   │   │   ├── dbmodels/             # SQLAlchemy ORM models
│   │   │   ├── schemas/              # Pydantic request/response schemas
│   │   │   ├── services/             # Business logic (matching, notifications)
│   │   │   ├── templates/            # Jinja2 email/PDF/export templates
│   │   │   ├── main.py               # FastAPI entry point
│   │   │   ├── requirements.txt
│   │   │   ├── environment.yml       # Conda environment spec
│   │   │   └── .env.example
│   │   │
│   │   └── contracts/                # Shared API contracts
│   │       ├── model-schema/
│   │       ├── openapi/
│   │       └── protobuf/
│   │
│   └── frontend/
│       ├── web-html/                 # Primary citizen-facing web (port 5173)
│       │   ├── public/               # Static assets served directly
│       │   │   └── images/icons/
│       │   └── src/
│       │       ├── assets/           # fonts/, icons/, illustrations/, images/
│       │       ├── components/
│       │       ├── js/
│       │       │   ├── api/          # API client
│       │       │   ├── modules/      # maps/, payments/
│       │       │   ├── ui/
│       │       │   └── utils/
│       │       ├── layouts/
│       │       ├── pages/            # auth/, app/, provider/, admin/
│       │       └── styles/themes/
│       │
│       ├── web-react/                # Admin dashboard (port 5174)
│       │   ├── public/
│       │   └── src/
│       │
│       └── mobile-expo/              # React Native / Expo (iOS + Android)
│           ├── components/
│           ├── navigation/
│           └── screens/
│
├── database/
│   └── init/                         # SQL: extensions, schema, seed data
│   └── package.json
│
├── dsml/                             # Data Science & ML
│   ├── data/feature-store/
│   ├── data/processed/
│   ├── data/raw/
│   ├── experiments/ab-tests/
│   ├── experiments/notebooks/        # Jupyter notebooks (exploration, prototypes, training)
│   ├── mlops/                        # deployment/, monitoring/, pipelines/, tracking/
│   ├── models/
│   ├── pipelines/
│   ├── projects/                     # churn-prediction/, misuse-anomaly-detection/, recommendation-system/
│   └── training/
│
├── infra/                            # docker/, k8s/, terraform/
├── configs/                          # Environment-specific config files
├── scripts/                          # Utility and automation scripts
├── tests/                            # Integration, E2E, performance tests
├── docs/                             # User-facing documentation (this file)
├── start-here/                       # Onboarding guides
├── instructions/                     # Claude Code / AI reference specs
├── schedules/
└── .github/workflows/                # CI/CD pipelines
```

### Backend Layer Responsibilities

| Layer | Directory | Responsibility |
|-------|-----------|----------------|
| API | `src/backend/app-python/api/` | Request handling, validation, routing |
| Schema | `src/backend/app-python/schemas/` | Pydantic request/response types |
| Service | `src/backend/app-python/services/` | Business logic (matching, geo calculations) |
| Model | `src/backend/app-python/dbmodels/` | SQLAlchemy table definitions |
| Core | `src/backend/app-python/core/` | Config, DB connection, Redis, JWT, exceptions |

The backend is a **single FastAPI process** — not a set of microservices. The module boundaries (auth, services, geo, analytics, notifications) are logical separations within one codebase that enable future microservice extraction if the system needs to scale independently.

### File Naming Conventions

| Language | Convention | Example |
|----------|-----------|---------|
| Python | `snake_case` | `user_service.py`, `test_auth.py` |
| TypeScript | `camelCase` | `rateLimit.ts`, `rateLimit.test.ts` |
| HTML/CSS | `kebab-case` | `login-page.html`, `custom.css` |
| SQL | Numbered + underscores | `01_create_users.sql` |

---

## 4. Backend Setup (Python/FastAPI)

### 4.1 Clone and Navigate

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp/src/backend/app-python
```

### 4.2 Create the Conda Environment

```bash
# From environment.yml (preferred — pins exact versions)
conda env create -f environment.yml
conda activate idrm-mvp

# Or manually
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp
pip install --break-system-packages -r requirements.txt
```

### 4.3 Environment Variables

```bash
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15

# CORS — all three frontends
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,exp://192.168.1.100:19000

# Environment
ENVIRONMENT=development
DEBUG=true

# Email (optional for dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF

chmod 600 .env
```

### 4.4 Initialize the Database Schema

```bash
# Option A: Run SQL init scripts directly (quickest for first setup)
cd ~/projects/idrm-mvp/database/init
for f in *.sql; do psql -U idrm_user -d idrm_db -f "$f"; done

# Option B: Use Alembic migrations
cd ~/projects/idrm-mvp/src/backend/app-python
conda activate idrm-mvp
alembic upgrade head

# Verify
psql -U idrm_user -d idrm_db -c "\dt"
```

### 4.5 Verify Backend

```bash
conda activate idrm-mvp
cd ~/projects/idrm-mvp/src/backend/app-python
uvicorn main:app --reload --port 8000

# In another terminal
curl http://localhost:8000/health    # {"status": "healthy"}
# Swagger UI: http://localhost:8000/docs
# ReDoc:      http://localhost:8000/redoc
```

---

## 5. API Gateway Setup (Bun)

### 5.1 Install and Configure

```bash
cd ~/projects/idrm-mvp/src/backend/api-gateway
bun install

cat > .env << 'EOF'
# Backend
BACKEND_URL=http://localhost:8000

# Frontend origins (CORS)
FRONTEND_HTML_URL=http://localhost:5173
FRONTEND_SPA_URL=http://localhost:5174
FRONTEND_MOBILE_URL=exp://192.168.1.100:19000

# Server
PORT=3000
NODE_ENV=development

# WebSocket
WS_ENABLED=true
WS_PORT=3001
EOF
```

### 5.2 Verify Gateway

```bash
bun run dev
# Should log: Bun API Gateway running on http://localhost:3000

# In another terminal
curl http://localhost:3000/health          # {"status": "ok", "gateway": "running"}
curl http://localhost:3000/api/v1/health   # Proxied to backend
```

---

## 6. Frontend Setup (Three Platforms)

### 6.1 HTML/Tailwind — Primary Web (Port 5173)

```bash
cd ~/projects/idrm-mvp/src/frontend/web-html
bun install

cat > src/config.js << 'EOF'
export const API_URL = 'http://localhost:3000/api/v1';
export const WS_URL  = 'ws://localhost:3001';
EOF

bun run dev
# Open: http://localhost:5173
```

### 6.2 React SPA — Admin Dashboard (Port 5174)

```bash
cd ~/projects/idrm-mvp/src/frontend/web-react
bun install

cat > src/config.ts << 'EOF'
export const API_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:3000/api/v1'
  : 'https://api.idrm.example.com/api/v1';

export const WS_URL = process.env.NODE_ENV === 'development'
  ? 'ws://localhost:3001'
  : 'wss://api.idrm.example.com/ws';
EOF

bun run dev
# Open: http://localhost:5174
```

### 6.3 React Native — Mobile App (Expo)

```bash
cd ~/projects/idrm-mvp/src/frontend/mobile-expo
bun install

# Find your local IP address
ip addr show | grep "inet "
# Example: inet 192.168.1.100

# Use your actual LAN IP — mobile devices cannot reach "localhost"
cat > src/config.ts << 'EOF'
export const API_URL = __DEV__
  ? 'http://192.168.1.100:3000/api/v1'    // Replace with your LAN IP
  : 'https://api.idrm.example.com/api/v1';

export const WS_URL = __DEV__
  ? 'ws://192.168.1.100:3001'
  : 'wss://api.idrm.example.com/ws';
EOF

npx expo start
# i → iOS simulator
# a → Android emulator
# Scan QR → Expo Go on physical device

# Open firewall for mobile devices
sudo ufw allow 3000
sudo ufw allow 19000    # Expo dev server
```

---

## 7. Running All Services (5-Terminal Approach)

Development uses **5 separate terminal tabs** — one per service. PostgreSQL and Redis run as systemd services and need no terminal.

| Terminal | Service | Port | Command |
|----------|---------|------|---------|
| 1 | Backend (FastAPI) | 8000 | `cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000` |
| 2 | API Gateway (Bun) | 3000/3001 | `cd src/backend/api-gateway && bun run dev` |
| 3 | HTML/Tailwind (Vite) | 5173 | `cd src/frontend/web-html && bun run dev` |
| 4 | React SPA (Vite) | 5174 | `cd src/frontend/web-react && bun run dev` |
| 5 | React Native (Expo) | — | `cd src/frontend/mobile-expo && npx expo start` |

### Automated Start Script

Save as `dev-start-v3.sh` in the project root:

```bash
#!/bin/bash
echo "Starting IDRM v3 Development Environment"
echo "========================================="

PROJECT=~/projects/idrm-mvp

check_port() { lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null; }

if check_port 8000; then
  echo "Backend already running on :8000"
else
  echo "1. Starting Backend..."
  gnome-terminal --tab -- bash -c "cd $PROJECT/src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000; exec bash"
fi

if check_port 3000; then
  echo "API Gateway already running on :3000"
else
  echo "2. Starting API Gateway..."
  gnome-terminal --tab -- bash -c "cd $PROJECT/src/backend/api-gateway && bun run dev; exec bash"
fi

if check_port 5173; then
  echo "HTML/Tailwind already running on :5173"
else
  echo "3. Starting HTML/Tailwind..."
  gnome-terminal --tab -- bash -c "cd $PROJECT/src/frontend/web-html && bun run dev; exec bash"
fi

if check_port 5174; then
  echo "React SPA already running on :5174"
else
  echo "4. Starting React SPA..."
  gnome-terminal --tab -- bash -c "cd $PROJECT/src/frontend/web-react && bun run dev; exec bash"
fi

echo "5. Starting React Native (Expo)..."
gnome-terminal --tab -- bash -c "cd $PROJECT/src/frontend/mobile-expo && npx expo start; exec bash"

echo ""
echo "Backend:       http://localhost:8000"
echo "API Docs:      http://localhost:8000/docs"
echo "API Gateway:   http://localhost:3000"
echo "HTML/Tailwind: http://localhost:5173"
echo "React SPA:     http://localhost:5174"
echo "React Native:  Expo DevTools (auto-opens)"
```

```bash
chmod +x dev-start-v3.sh
./dev-start-v3.sh
```

### Health Check Script

```bash
#!/bin/bash
# health-check-v3.sh
echo "IDRM v3 Health Check"
echo "===================="

echo "Backend (8000):"; curl -s http://localhost:8000/health | jq || echo "Not responding"
echo "API Gateway (3000):"; curl -s http://localhost:3000/health | jq || echo "Not responding"
echo "HTML/Tailwind (5173):"; curl -s http://localhost:5173 > /dev/null && echo "Running" || echo "Not running"
echo "React SPA (5174):"; curl -s http://localhost:5174 > /dev/null && echo "Running" || echo "Not running"
echo "PostgreSQL:"; pg_isready -U idrm_user -d idrm_db && echo "Running" || echo "Not running"
echo "Redis:"; redis-cli ping || echo "Not running"
```

### Hot Reload Performance

```
Python file changed → Backend reloads:
  Native (uvicorn --reload):  ~100 ms
  Docker volume mount:        ~5-10 s

TypeScript file changed → Bun gateway reloads:
  Native (bun --hot):          ~50 ms
  Docker volume mount:         ~3-5 s

React/HTML file changed → Vite HMR:
  Native:                      ~50 ms
  Docker volume mount:         ~2-3 s

Result: 50-100x faster iteration with native development
```

---

## 8. Development Workflow

### Daily Routine

```bash
# Morning: start all services
./dev-start-v3.sh

# Edit code in VSCode → save → hot reload kicks in automatically
# Watch logs in each terminal tab

# Before committing
cd src/backend/app-python && conda activate idrm-mvp && pytest ../../tests/ -v
cd src/frontend/web-react && bun test

# Commit
git add <specific files>     # prefer explicit paths over git add .
git commit -m "feat: describe what and why"
git push
```

### Adding a New Feature

```
Example: Service Rating feature

1. Branch
   git checkout -b feature/service-rating

2. Database (if new table needed)
   src/backend/app-python/dbmodels/rating.py    ← SQLAlchemy model
   alembic revision --autogenerate -m "add service rating"
   alembic upgrade head

3. Backend
   src/backend/app-python/schemas/rating.py     ← Pydantic schemas
   src/backend/app-python/services/rating.py    ← Business logic
   src/backend/app-python/api/services.py       ← Add rating endpoints
   tests/test_api/test_rating.py                ← Tests (80% coverage target)

4. Frontends (as needed)
   src/frontend/web-html/src/pages/app/service-detail.html
   src/frontend/web-html/src/js/services.js
   src/frontend/web-react/src/pages/ServiceDetail.tsx
   src/frontend/mobile-expo/screens/ServiceDetailScreen.tsx

5. Test & review
   pytest tests/ --cov=src/backend/app-python
   bun test (in each frontend directory)
   Manual test on localhost:5173 and localhost:5174

6. PR
   git push origin feature/service-rating
   # Open PR on GitHub
```

### Database Migrations

```bash
cd src/backend/app-python
conda activate idrm-mvp

# Generate from model changes
alembic revision --autogenerate -m "describe the change"

# Review the generated file in alembic/versions/ before applying

# Apply
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Check current revision
alembic current
```

---

## 9. Running Tests

### Backend Unit Tests

```bash
cd ~/projects/idrm-mvp
conda activate idrm-mvp

pytest tests/ -v
pytest tests/ -v --cov=src/backend/app-python --cov-report=html
# Coverage target: 80%+
# Open report: firefox htmlcov/index.html
```

### Frontend Tests

```bash
cd src/frontend/web-html    && bun test
cd src/frontend/web-react   && bun test
cd src/frontend/mobile-expo && bun test
```

### Integration and Load Tests

```bash
# Integration (requires all 5 services running)
pytest tests/integration/ -v

# E2E
pytest tests/e2e/ -v

# Load tests (Locust)
locust -f tests/performance/locustfile.py --headless \
  -u 100 -r 10 --run-time 60s
```

### Loading Test Data

```bash
# Lightweight (10 users, 25 requests) — unit tests
psql -U idrm_user -d idrm_db -f database/init/mock_data_unittest.sql

# Integration scale (100 users, 500 requests)
psql -U idrm_user -d idrm_db -f database/init/mock_data_integration.sql

# Full dataset (1,500 users, 8,000 requests)
psql -U idrm_user -d idrm_db -f database/init/mock_data_full.sql
```

---

## 10. Troubleshooting

### Port Already in Use

```bash
sudo lsof -i :8000    # Backend
sudo lsof -i :3000    # API Gateway
sudo lsof -i :5173    # HTML/Tailwind
sudo lsof -i :5174    # React SPA
kill -9 <PID>
```

### Backend Won't Start

```bash
# 1. Confirm conda env is active
conda activate idrm-mvp
which python    # Must show miniconda3/envs/idrm-mvp path

# 2. Test DB connection
psql -U idrm_user -d idrm_db -c "SELECT 1;"

# 3. Test Redis
redis-cli ping

# 4. Run with debug logging
uvicorn app.main:app --reload --port 8000 --log-level debug
```

### PostgreSQL Won't Start

```bash
sudo systemctl status postgresql
sudo journalctl -u postgresql -n 50
sudo lsof -i :5432    # Check for port conflict
```

### Redis Permission Denied

```bash
sudo chown redis:redis /var/lib/redis
sudo systemctl restart redis
```

### Frontend Gets CORS Error

```bash
# src/backend/app-python/core/ — allow_origins must include all three frontends:
#   "http://localhost:5173"   ← HTML/Tailwind (web-html)
#   "http://localhost:5174"   ← React SPA (web-react)
#   "exp://*"                 ← React Native (mobile-expo)

# Verify gateway routes correctly
curl http://localhost:3000/api/v1/health
```

### React Native Can't Reach Backend

```bash
# Must use your LAN IP, not "localhost"
ip addr show | grep "inet "    # Find your IP
# Update src/frontend/mobile-expo/src/config.ts with that IP

# Firewall
sudo ufw allow 3000
sudo ufw allow 19000    # Expo dev server

# Device and laptop must be on the same WiFi
# If network isolation persists, use tunnel mode:
npx expo start --tunnel
```

### Miniconda Conflicts with System Python

```bash
# This is expected — always activate the env first
conda activate idrm-mvp
which python    # /home/user/miniconda3/envs/idrm-mvp/bin/python
```

### Bun Installation Fails

```bash
mkdir -p ~/.bun
curl -fsSL https://bun.sh/install | bash -s "bun-v1.0.0"
```

---

## 11. Jupyter Notebooks

Notebooks live in `dsml/experiments/notebooks/` within the project. They are organized into categories by audience and purpose.

```
dsml/
└── experiments/
    └── notebooks/        # Jupyter notebooks
        ├── exploration/  # Data scientists — understand the system
        │   ├── 01-data-exploration.ipynb          # DB schema, sample data, table relationships
        │   ├── 02-geospatial-analysis.ipynb       # PostGIS queries, clustering, map rendering
        │   ├── 03-user-behavior-analysis.ipynb    # Request patterns, bottleneck identification
        │   └── 04-disaster-pattern-analysis.ipynb # Surge patterns, predictive insights
        ├── prototypes/   # Developers — test algorithms before production
        │   ├── matching-algorithm-prototype.ipynb  # Service-to-provider matching, A/B scoring
        │   ├── clustering-prototype.ipynb          # K-means vs DBSCAN for hotspot detection
        │   ├── notification-prototype.ipynb        # Email/SMS/push format and delivery testing
        │   └── ai-recommendation-prototype.ipynb  # ML resource prediction experiments
        ├── training/     # New team members — learn the stack interactively
        │   ├── beginner-python-fastapi.ipynb       # FastAPI intro, writing a first endpoint
        │   ├── postgis-tutorial.ipynb              # Spatial types, queries, index optimization
        │   ├── api-testing-tutorial.ipynb          # pytest, integration tests, coverage targets
        │   ├── frontend-integration.ipynb          # API calls, Leaflet.js map, Chart.js graphs
        │   └── deployment-walkthrough.ipynb        # Docker, Compose, environment config
        └── reports/      # Stakeholders — reproducible monthly and quarterly analytics
            ├── monthly-metrics.ipynb               # Request volumes, response times, satisfaction
            ├── disaster-response-analysis.ipynb    # Event timeline, efficiency, lessons learned
            ├── performance-analysis.ipynb          # API latency trends, query opt, cache hit rates
            └── quarterly-review.ipynb             # QoQ growth, tech debt inventory, roadmap
```

### Starting Jupyter

```bash
conda activate idrm-mvp
jupyter lab          # Opens at http://localhost:8888
# or
jupyter notebook     # Classic interface
```

Jupyter is included in the `idrm-mvp` conda environment. Run `jupyter lab` from the project root — notebooks in `exploration/` and `training/` connect to the local PostgreSQL instance, so ensure the dev database is running before executing cells that query data.

---

## 12. Email & PDF Templates (Jinja2)

IDRM uses a hybrid rendering approach: static HTML pages are served directly by Bun (CDN-cacheable), while dynamic content uses Jinja2 server-side templates. Templates live in `src/backend/app-python/templates/`.

```
src/backend/app-python/
└── templates/           # Dynamic Jinja2 templates — rendered per-request
    ├── email/
    │   ├── welcome.html            # Variables: {{ user.name }}, {{ verification_link }}
    │   ├── password-reset.html     # Variables: {{ reset_link }}, {{ expiry_time }}
    │   ├── service-created.html    # Variables: {{ service.id }}, {{ service.type }}, {{ location }}
    │   ├── service-accepted.html   # Variables: {{ provider.name }}, {{ provider.phone }}, {{ eta }}
    │   ├── service-completed.html  # Variables: {{ service.id }}, {{ completion_time }}
    │   └── daily-digest.html       # Variables: {{ stats }}, {{ pending_requests }}
    ├── pdf/
    │   ├── service-receipt.html    # Variables: {{ service.* }}, {{ qr_code }} → WeasyPrint → PDF
    │   ├── monthly-report.html     # Variables: {{ month }}, {{ stats }}, {{ charts }}
    │   └── certificate.html        # Variables: {{ volunteer.name }}, {{ hours }}, {{ org }}
    └── export/
        ├── csv-export.jinja2       # Variables: {{ headers }}, {{ rows }}
        ├── excel-export.jinja2     # Variables: {{ sheets }}, {{ data }}
        └── json-export.jinja2      # Variables: {{ data }}
```

Static HTML pages (served by Bun's API gateway, CDN-cacheable) live in `src/frontend/web-html/public/`.

### Jinja2 Setup

```python
# src/backend/app-python/core/templates.py
from jinja2 import Environment, FileSystemLoader
import os

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), '../templates')
jinja_env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def render_email_template(template_name: str, **context) -> str:
    template = jinja_env.get_template(f'email/{template_name}')
    return template.render(**context)

def render_pdf_template(template_name: str, **context) -> bytes:
    template = jinja_env.get_template(f'pdf/{template_name}')
    html = template.render(**context)
    from weasyprint import HTML
    return HTML(string=html).write_pdf()
```

### Usage Example

```python
# Send a service-accepted email
html = render_email_template(
    'service-accepted.html',
    provider_name="Dr. Ramesh Kumar",
    provider_phone="+919876543210",
    eta="20 minutes"
)

# Generate a service receipt PDF
pdf_bytes = render_pdf_template(
    'service-receipt.html',
    service=service_obj,
    qr_code=generate_qr(service_obj.id)
)
```

**Rule of thumb**: if the same HTML is served to every user without personalization, put it in `static/`. If it contains user-specific data (names, service IDs, dates), put it in `templates/` and render via Jinja2.

---

## Further Reading

- **Architecture**: [IDRM-ARCHITECTURE-GUIDE.md](IDRM-ARCHITECTURE-GUIDE.md) — modular monolith design, ADRs, data model
- **Deployment**: [IDRM-DEPLOYMENT-GUIDE.md](IDRM-DEPLOYMENT-GUIDE.md) — Docker staging, CI/CD, blue-green production
- **API Reference**: [../start-here/COMPLETE-API-SPECS-GUIDE.md](../start-here/COMPLETE-API-SPECS-GUIDE.md) — all endpoints with examples
- **Database**: [../start-here/COMPLETE-DATABASE-GUIDE.md](../start-here/COMPLETE-DATABASE-GUIDE.md) — schema, PostGIS queries, mock data
- **Quick Reference**: [../CLAUDE.md](../CLAUDE.md) — daily commands, port map, API examples

---

**IDRM v3 Development: Native, Fast, Multi-Platform**  
Hot reload: <100 ms · Three frontends · One backend · One conda environment
