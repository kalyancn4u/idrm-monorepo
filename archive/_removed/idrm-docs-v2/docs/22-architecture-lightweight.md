> *Type: Document (specification) · Audience: Architects · Status: Archived — v2 historical generation*

# IDRM MVP: Lightweight Architecture (Revised)

<!-- IDRM-CLEANUP doc=v2-22-lightweight status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — architecture variant → `docs/mvp/20`
> Another v2 architecture draft (the "lightweight" cut). Current source of truth =
> [`../../../../docs/mvp/20-architecture-system.md`](../../../../docs/mvp/20-architecture-system.md) + ADRs `docs/mvp/21`.
> MVP-aligned. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Minimal Docker + Miniconda + Bun Setup

> **Philosophy**: Run only what must be containerized (PostgreSQL). Everything else native for performance.

---

## Revised Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Your Ubuntu Laptop                        │
│                                                              │
│  ┌────────────────┐  ┌──────────────┐  ┌─────────────────┐│
│  │   PostgreSQL   │  │   FastAPI    │  │   Bun Server    ││
│  │   + PostGIS    │  │  (Miniconda) │  │  (Frontend)     ││
│  │   (Docker)     │  │   Port 8000  │  │   Port 3000     ││
│  │   Port 5432    │  │              │  │                 ││
│  └────────────────┘  └──────────────┘  └─────────────────┘│
│         ↑                    ↑                   ↑          │
│         │                    │                   │          │
│         └────────────────────┴───────────────────┘          │
│                      localhost                              │
└─────────────────────────────────────────────────────────────┘

Browser → http://localhost:3000 (Bun serves frontend + proxies API)
          ↓
       Bun Runtime
          ↓
       FastAPI (localhost:8000)
          ↓
       PostgreSQL+PostGIS (Docker)
```

---

## Technology Stack (Optimized)

### Database Layer
- **PostgreSQL 16 + PostGIS 3.4** (Docker only - must be containerized)
- **Why Docker?** PostGIS setup is complex; Docker ensures consistency
- **Resource Impact**: ~200MB RAM, minimal CPU

### Backend Layer
- **Python 3.11 via Miniconda** (native, no containers)
- **FastAPI** for API server
- **Why Miniconda?** 
  - Lighter than Anaconda (~400MB vs 3GB)
  - Better dependency management than pip+venv
  - Cross-platform consistency
  - Easy environment management

### Frontend Layer
- **Bun 1.x** (native JavaScript runtime - replaces Node.js)
- **Tailwind CSS** for styling
- **Leaflet** for maps
- **Why Bun?**
  - 3-4x faster than Node.js
  - Built-in TypeScript support
  - Built-in bundler (no webpack!)
  - Single binary (~90MB)
  - Fast package install (~20x faster than npm)

---

## Resource Comparison

### Old Approach (Full Docker Compose)
```
PostgreSQL container:    ~200 MB RAM
FastAPI container:       ~150 MB RAM
Node.js container:       ~100 MB RAM
Redis container:         ~50 MB RAM
GeoServer container:     ~500 MB RAM
Docker overhead:         ~200 MB RAM
────────────────────────────────────
TOTAL:                  ~1.2 GB RAM
```

### New Approach (Minimal Docker)
```
PostgreSQL container:    ~200 MB RAM
Python (Miniconda):      ~100 MB RAM (native)
Bun runtime:            ~50 MB RAM (native)
────────────────────────────────────
TOTAL:                  ~350 MB RAM
```

**Savings**: ~850 MB RAM, significantly faster startup!

---

## Development Workflow

### Daily Development
```bash
# 1. Start PostgreSQL (only Docker service)
docker compose up -d postgres

# 2. Activate Miniconda environment
conda activate idrm-mvp

# 3. Start FastAPI backend
cd backend
uvicorn app.main:app --reload --port 8000

# 4. Start Bun dev server (different terminal)
cd frontend
bun run dev
```

### Production Deployment
```bash
# For production, we CAN containerize everything if needed
# But for MVP on your laptop, native is better
```

---

## Why This Stack is Better for You

### Bun vs Node.js
| Feature | Node.js | Bun | Winner |
|---------|---------|-----|--------|
| Runtime speed | 1x | 3-4x faster | 🏆 Bun |
| Package install | npm (slow) | 20x faster | 🏆 Bun |
| TypeScript | Needs ts-node | Native | 🏆 Bun |
| Bundler | Need webpack/vite | Built-in | 🏆 Bun |
| Binary size | N/A | 90MB single file | 🏆 Bun |
| Maturity | Very mature | New (2023) | Node |
| Ecosystem | Huge | Growing | Node |

**Verdict**: Bun wins for solo development, modern projects

### Miniconda vs Docker Python
| Feature | Docker Python | Miniconda | Winner |
|---------|--------------|-----------|--------|
| Startup time | ~3-5 sec | Instant | 🏆 Conda |
| RAM usage | 150+ MB | 100 MB | 🏆 Conda |
| Development | Edit = rebuild | Hot reload | 🏆 Conda |
| Debugging | Complex | Native | 🏆 Conda |
| Deployment | Easy | Manual setup | Docker |

**Verdict**: Miniconda for development, Docker for deployment

---

## Installation Order

### 1. Miniconda (Python Environment)
```bash
# Download Miniconda installer
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# Install
bash Miniconda3-latest-Linux-x86_64.sh -b -p $HOME/miniconda3

# Initialize
~/miniconda3/bin/conda init bash

# Restart terminal or source
source ~/.bashrc

# Verify
conda --version
```

### 2. Bun (JavaScript Runtime)
```bash
# Install Bun (single command)
curl -fsSL https://bun.sh/install | bash

# Add to PATH (usually automatic)
export PATH="$HOME/.bun/bin:$PATH"

# Verify
bun --version

# Should show: bun 1.x.x
```

### 3. Docker (PostgreSQL only)
```bash
# Install Docker (already covered in previous guide)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Verify
docker --version
```

---

## Project Structure (Updated)

```
idrm-mvp/
├── docker-compose.yml          # PostgreSQL only
├── README.md
├── .gitignore
│
├── backend/                    # Python + FastAPI
│   ├── environment.yml         # Conda environment
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   └── tests/
│
├── frontend/                   # Bun + Tailwind
│   ├── package.json            # Bun dependencies
│   ├── bun.lockb              # Bun lock file
│   ├── tailwind.config.js     # Tailwind configuration
│   ├── postcss.config.js      # PostCSS for Tailwind
│   ├── src/
│   │   ├── index.html         # Entry point
│   │   ├── main.js            # JavaScript entry
│   │   ├── styles/
│   │   │   ├── tailwind.css   # Tailwind imports
│   │   │   └── custom.css     # Custom styles
│   │   ├── components/        # Reusable components
│   │   ├── pages/             # Page components
│   │   ├── utils/             # Utilities
│   │   └── design-system/     # Design tokens
│   └── public/                # Static assets
│
├── database/
│   └── init/                  # SQL initialization
│
└── docs/                      # Documentation
    ├── design-system.md       # Design system guide
    ├── components.md          # Component library
    └── api-docs.md           # API documentation
```

---

## Minimal Docker Compose (PostgreSQL Only)

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres
    environment:
      POSTGRES_DB: idrm_db
      POSTGRES_USER: idrm_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-idrm_secure_pass}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U idrm_user"]
      interval: 10s
      timeout: 5s
      retries: 5
    # Resource limits (optional, for low-end hardware)
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

volumes:
  postgres-data:
```

---

## Performance Benefits

### Startup Times
```
Old Stack (Full Docker):
- docker compose up:        ~15-20 seconds
- Services ready:           ~30-40 seconds
- Code changes rebuild:     ~5-10 seconds

New Stack (Minimal Docker):
- docker compose up:        ~5 seconds (PostgreSQL only)
- FastAPI ready:           ~1 second (instant)
- Bun dev server:          ~0.5 seconds (instant)
- Hot reload:              ~100ms (blazingly fast)
```

### Development Experience
```
Old: Change code → Wait for Docker rebuild → Test
     (5-10 second delay per change)

New: Change code → Instant hot reload → Test
     (100ms delay per change)
```

**Result**: ~50x faster iteration cycle!

---

## When to Add Docker Back

### Development (Current Phase)
✅ PostgreSQL only (complex to set up natively)
❌ Python (Miniconda is faster)
❌ Frontend (Bun is faster)

### Testing/CI Phase
✅ PostgreSQL (consistency)
✅ Python (reproducible tests)
❌ Frontend (Bun is fast enough)

### Production Deployment
✅ Everything containerized for easy deployment
✅ Docker Compose or Kubernetes
✅ But develop locally without containers!

---

## Hybrid Approach (Best of Both Worlds)

```bash
# Development: Native performance
conda activate idrm-mvp
uvicorn app.main:app --reload
bun run dev

# Production: Containerized reliability  
docker compose -f docker-compose.prod.yml up -d
```

**Keep both configurations**, use what makes sense for each phase!

---

## Migration Path

### Phase 1 (Current): Minimal Docker
- PostgreSQL: Docker
- Backend: Miniconda
- Frontend: Bun
- **Goal**: Fast development

### Phase 2 (Testing): Add Backend Container
- PostgreSQL: Docker
- Backend: Docker (for CI/CD)
- Frontend: Bun
- **Goal**: Reproducible tests

### Phase 3 (Production): Full Containerization
- Everything: Docker/Kubernetes
- **Goal**: Easy deployment, scaling

---

## Resource Recommendations

### Minimum Hardware (Your Laptop)
- CPU: i5-1235U ✅ (Perfectly adequate)
- RAM: 32GB ✅ (Excellent! Can run multiple instances)
- SSD: 512GB ✅ (Good for development)

### Resource Allocation
```
PostgreSQL:      200 MB RAM, 10% CPU
FastAPI:         100 MB RAM, 5% CPU
Bun dev server:  50 MB RAM, 5% CPU
VS Code:         500 MB RAM, 10% CPU
Browser:         500 MB RAM, 10% CPU
────────────────────────────────────
TOTAL:          ~1.4 GB RAM, 40% CPU
```

**You have plenty of headroom!** Could run 10+ instances if needed.

---

## Why Bun is Perfect for This Project

### 1. **Speed** 
```bash
# NPM (Node.js)
npm install          # ~30-60 seconds
npm run dev         # ~3-5 seconds startup

# Bun
bun install         # ~2-3 seconds (20x faster!)
bun run dev        # ~0.5 seconds startup (10x faster!)
```

### 2. **Built-in Features**
```javascript
// TypeScript - no configuration needed
import type { User } from './types';

// JSX - works out of the box
const App = () => <div>Hello</div>;

// Environment variables
const apiUrl = Bun.env.API_URL;

// Fast bundler - no webpack/vite needed
// bun build src/main.js --outdir dist
```

### 3. **Node.js Compatibility**
```javascript
// All Node.js APIs work
import express from 'express';  // Works!
import fs from 'fs';            // Works!

// But faster execution
```

### 4. **Modern Standards**
- ES modules by default
- Top-level await
- Fast test runner
- Built-in SQLite (if needed)

---

## Next Steps

1. **Install Miniconda** (5 min)
2. **Install Bun** (2 min)
3. **Setup PostgreSQL** (Docker only)
4. **Create design system** (FIRST! Before coding)
5. **Build backend** (Miniconda environment)
6. **Build frontend** (Bun + Tailwind)

---

## Quick Command Reference

```bash
# Conda commands
conda create -n idrm-mvp python=3.11
conda activate idrm-mvp
conda deactivate
conda env list

# Bun commands
bun install                    # Install dependencies
bun run dev                    # Start dev server
bun run build                  # Build for production
bun test                       # Run tests
bun add <package>             # Add dependency
bun remove <package>          # Remove dependency

# Docker commands (PostgreSQL only)
docker compose up -d postgres  # Start database
docker compose down           # Stop database
docker compose logs postgres  # View logs
```

---

## Comparison Table (Final)

| Aspect | Full Docker | Minimal Docker | Winner |
|--------|-------------|----------------|--------|
| RAM Usage | ~1.2 GB | ~350 MB | 🏆 Minimal |
| Startup Time | 30-40s | 5s | 🏆 Minimal |
| Hot Reload | 5-10s | <1s | 🏆 Minimal |
| Dev Experience | Slower | Fast | 🏆 Minimal |
| Production Deploy | Easy | Manual | Full Docker |
| Reproducibility | High | Medium | Full Docker |
| Debugging | Harder | Easy | 🏆 Minimal |

**Verdict**: Minimal Docker for development, Full Docker for production!

---

This is the **optimal setup for your hardware and workflow**. You get:
- ✅ Fast development iteration
- ✅ Low resource usage
- ✅ Modern tooling (Bun!)
- ✅ Easy to understand
- ✅ Production path clear

Ready to proceed with this architecture? 🚀
