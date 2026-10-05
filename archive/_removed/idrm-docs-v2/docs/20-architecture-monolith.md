> *Type: Document (specification) · Audience: Architects · Status: Archived — v2 historical generation*

# IDRM: Monolith Architecture (Native Ubuntu)
<!-- IDRM-CLEANUP doc=v2-20-monolith status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-2 **native monolith** architecture — the generation that reached the current MVP shape; **strongly aligns
> with `docs/mvp/20`** (and the evolution path prefigures the FFP). *Legend:* ✅ covered · ⚠ nuanced · ⊘ FFP.
>
> | Snippet | Section | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v2-20§arch` | Architecture Overview · Why Native Monolith | `docs/mvp/20` + ADR-001 | MVP | ✅ |
> | `v2-20§stack` | Technology Stack Details | `docs/mvp/20` · `tech-stack-101` | MVP | ✅ |
> | `v2-20§dir` | Directory Structure · Service Management | `docs/mvp/20`/`30` + `docs/mvp/80` (systemd) | MVP | ✅ |
> | `v2-20§evo` | Evolution Path: Monolith → Full Product | `docs/ffp/11` (triggers) + `docs/ffp/20` | FFP | ✅ (as FFP) |
> | `v2-20§test` | Testing Strategy | `docs/mvp/70` | MVP | ✅ |
> | `v2-20§ops` | Backup/Recovery · Monitoring · Prod Checklist · Security | `docs/mvp/80` + `22` | MVP | ✅ |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Production-Ready Setup from Day One

> **Philosophy**: Start with a monolith that can evolve into microservices without architectural debt.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ubuntu 22.04/24.04 LTS                        │
│                                                                  │
│  ┌────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  PostgreSQL 16 │  │   FastAPI    │  │   Bun Server      │  │
│  │  + PostGIS 3.4 │  │  (Miniconda) │  │   (Frontend)      │  │
│  │                │  │              │  │                   │  │
│  │  Native        │  │  Port 8000   │  │   Port 3000       │  │
│  │  systemd       │  │              │  │                   │  │
│  └────────────────┘  └──────────────┘  └───────────────────┘  │
│         ↑                    ↑                   ↑              │
│         │                    │                   │              │
│         └────────────────────┴───────────────────┘              │
│                      localhost                                  │
└─────────────────────────────────────────────────────────────────┘

Production Flow:
User → Nginx (reverse proxy) → Bun/FastAPI → PostgreSQL
```

---

## Why Native Monolith?

### 1. **Performance**

| Metric | Docker | Native | Improvement |
|--------|--------|--------|-------------|
| PostgreSQL startup | 5-10s | 1-2s | 5x faster |
| Query latency | +2-5ms | Baseline | No overhead |
| RAM usage | +200MB | Baseline | 200MB saved |
| File I/O | Overhead | Direct | Faster |

### 2. **Development Experience**

```bash
# Docker approach:
docker-compose up -d              # 15-20s
# Change code
docker-compose restart api        # 5-10s rebuild
# Test

# Native approach:
# PostgreSQL already running (systemd)
uvicorn app.main:app --reload    # 0.5s
# Change code → instant reload (100ms)
# Test
```

**Result**: 50x faster iteration cycle!

### 3. **Production Parity**

Native setup is CLOSER to production than Docker:
- Real production uses systemd services
- Real production has native PostgreSQL
- Real production doesn't run everything in containers
- This setup teaches production skills

### 4. **Debugging**

```bash
# Docker debugging:
docker exec -it container bash
# Find logs in container
# Network issues between containers
# Volume mount confusion

# Native debugging:
tail -f /var/log/postgresql/postgresql-16-main.log
systemctl status postgresql
psql -U idrm_user -d idrm_db
# Standard Linux tools work!
```

### 5. **Resource Efficiency**

Your laptop (i5-1235U, 32GB RAM):

```
Native Stack:
PostgreSQL:      150-200 MB
Python/FastAPI:  80-100 MB
Bun frontend:    40-60 MB
Total:          270-360 MB
─────────────────────────────
Remaining:      31.6 GB for development!

Could run 10+ instances if needed for testing
```

---

## Technology Stack Details

### Database Layer: PostgreSQL 16 + PostGIS 3.4

**Why Native?**
- Systemd management (production standard)
- Better performance (no Docker overhead)
- Easy backups (pg_dump, pg_basebackup)
- Standard monitoring tools work
- Upgrade path is standard PostgreSQL

**Installation**:
- From PostgreSQL apt repository (always latest)
- PostGIS from same repo (version compatibility)
- Configured for local development
- Production-ready configuration template included

**Configuration**:
```ini
# /etc/postgresql/16/main/postgresql.conf
max_connections = 100
shared_buffers = 256MB          # 25% of RAM for dev
effective_cache_size = 1GB      # 50% of available RAM
maintenance_work_mem = 128MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1          # SSD optimized
effective_io_concurrency = 200  # SSD
work_mem = 2621kB
```

### Backend: Python 3.11 + FastAPI (Miniconda)

**Why Miniconda?**
- Isolated environment (like production virtualenv)
- Reproducible (environment.yml)
- Cross-platform (works on any OS)
- Industry standard for Python data/ML work
- Better than pip+venv for complex dependencies

**Advantages over Docker Python**:
```bash
# Development speed:
Docker: Edit → Rebuild image → Restart container (5-10s)
Native: Edit → Hot reload (100ms)

# Debugging:
Docker: Remote debugger, port forwarding
Native: Standard Python debugger, native tools

# Dependencies:
Docker: Rebuild on every change
Native: pip install in active env (instant)
```

**Production Evolution**:
```bash
# Development: Miniconda environment
conda activate idrm-mvp
uvicorn app.main:app

# Production: Same code, different runner
gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
    --workers 4 --bind 0.0.0.0:8000
```

### Frontend: Bun + Tailwind CSS

**Why Bun?**
- 10-20x faster than Node.js
- Built-in bundler (no webpack/vite)
- TypeScript native
- Drop-in Node.js replacement
- Production-ready (v1.0+ is stable)

**Production Build**:
```bash
# Development:
bun run dev           # Instant hot reload

# Production:
bun build src/main.js --outdir dist --minify
# Serve with nginx
```

---

## Directory Structure

```
/home/your-user/
├── miniconda3/                   # Conda installation
│   └── envs/
│       └── idrm-mvp/            # Python environment
│
└── projects/
    └── idrm-mvp/                # Main project
        ├── backend/
        │   ├── app/
        │   │   ├── main.py      # FastAPI app
        │   │   ├── api/         # API routes
        │   │   ├── core/        # Config, security
        │   │   ├── db/          # Database
        │   │   ├── models/      # SQLAlchemy models
        │   │   ├── schemas/     # Pydantic schemas
        │   │   └── services/    # Business logic
        │   ├── tests/           # Tests
        │   └── environment.yml  # Conda env definition
        │
        ├── frontend/
        │   ├── src/
        │   │   ├── main.js
        │   │   ├── components/
        │   │   ├── styles/
        │   │   └── utils/
        │   ├── package.json
        │   └── bun.lockb
        │
        ├── database/
        │   ├── migrations/      # Schema migrations
        │   ├── seeds/           # Test data
        │   └── backups/         # Database backups
        │
        ├── docs/
        ├── scripts/             # Utility scripts
        └── logs/

/var/lib/postgresql/16/main/     # PostgreSQL data directory
/etc/postgresql/16/main/         # PostgreSQL configuration
/var/log/postgresql/             # PostgreSQL logs
```

---

## Service Management

### PostgreSQL (systemd)

```bash
# Start/stop
sudo systemctl start postgresql
sudo systemctl stop postgresql
sudo systemctl restart postgresql

# Enable/disable auto-start
sudo systemctl enable postgresql
sudo systemctl disable postgresql

# Status
sudo systemctl status postgresql
systemctl is-active postgresql

# Logs
sudo journalctl -u postgresql -f
tail -f /var/log/postgresql/postgresql-16-main.log
```

### FastAPI (Development)

```bash
# Manual start
conda activate idrm-mvp
cd ~/projects/idrm-mvp/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# With auto-reload on file changes
watchfiles 'uvicorn app.main:app --reload' backend/app
```

### Bun Frontend (Development)

```bash
cd ~/projects/idrm-mvp/frontend
bun run dev
# Auto-reloads on file changes
```

### Production Systemd Services

Create production systemd services:

```bash
# /etc/systemd/system/idrm-backend.service
[Unit]
Description=IDRM FastAPI Backend
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=your-user
WorkingDirectory=/home/your-user/projects/idrm-mvp/backend
Environment="PATH=/home/your-user/miniconda3/envs/idrm-mvp/bin"
ExecStart=/home/your-user/miniconda3/envs/idrm-mvp/bin/gunicorn \
    app.main:app \
    -k uvicorn.workers.UvicornWorker \
    --workers 4 \
    --bind 0.0.0.0:8000 \
    --access-logfile /home/your-user/projects/idrm-mvp/logs/access.log \
    --error-logfile /home/your-user/projects/idrm-mvp/logs/error.log
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Evolution Path: Monolith → Full Product

### Phase 1: MVP Monolith (Current)

```
Single Server:
├── PostgreSQL (native)
├── FastAPI (single process)
└── Bun (dev server) → Nginx (production)

Capacity: 100-500 concurrent users
```

**Production Deployment**:
```bash
# Nginx reverse proxy
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name idrm.example.com;
    
    location /api/ {
        proxy_pass http://backend;
    }
    
    location / {
        root /var/www/idrm/frontend;
        try_files $uri /index.html;
    }
}
```

### Phase 2: Optimized Monolith (Month 4-6)

```
Single Server (Optimized):
├── PostgreSQL (native, tuned)
├── FastAPI (Gunicorn + 4 workers)
├── Nginx (reverse proxy + static files)
└── Redis (native, for caching)

Capacity: 500-2,000 concurrent users
```

**What changes**:
- Install Redis: `apt install redis-server`
- Use Gunicorn with multiple workers
- Add connection pooling (pgbouncer)
- Enable query caching
- Optimize PostgreSQL config

**Code changes**: Minimal
```python
# Add Redis caching
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="idrm:")
```

### Phase 3: Vertical Scaling (Month 7-9)

```
Single Larger Server:
├── PostgreSQL (tuned for more RAM/CPU)
├── FastAPI (8-16 workers)
├── Redis (larger cache)
└── Nginx

Capacity: 2,000-5,000 concurrent users
```

**What changes**:
- Upgrade server specs (more RAM, faster CPU)
- Tune PostgreSQL for larger dataset
- Add database read replicas (streaming replication)
- Optimize queries with indexes

**Migration**: Just move to bigger server
```bash
# Backup on old server
pg_dump idrm_db > backup.sql

# Restore on new server
psql idrm_db < backup.sql

# Copy application code
rsync -avz ~/projects/idrm-mvp/ new-server:~/projects/idrm-mvp/
```

### Phase 4: Horizontal Scaling (Month 10-12)

```
Multiple Servers:
├── Load Balancer (HAProxy/Nginx)
├── Application Servers (2-4 instances)
│   └── FastAPI (4 workers each)
├── Database Cluster
│   ├── Primary (writes)
│   └── Replicas (reads)
└── Redis Cluster

Capacity: 5,000-20,000 concurrent users
```

**What changes**:
- Set up load balancer
- Deploy multiple app servers
- Configure PostgreSQL streaming replication
- Use Redis Sentinel/Cluster

**Code changes**: Minimal
```python
# Database session with read replicas
@app.get("/services")  # Read operation
async def get_services(db: Session = Depends(get_read_db)):
    # Uses read replica
    pass

@app.post("/services")  # Write operation
async def create_service(db: Session = Depends(get_write_db)):
    # Uses primary database
    pass
```

### Phase 5: Microservices (Year 2+)

```
Distributed Architecture:
├── API Gateway
├── Service Mesh
├── Microservices
│   ├── Auth Service
│   ├── Service Manager
│   ├── Geospatial Service
│   ├── Analytics Service
│   └── Notification Service
├── Database per Service
├── Message Queue (RabbitMQ/Kafka)
└── Monitoring Stack

Capacity: 20,000+ concurrent users
```

**Migration Strategy**:
```python
# Extract services one at a time
# Start with auth (least dependencies)

# Before (Monolith):
from app.services.auth import AuthService

# After (Microservice):
from app.clients.auth_client import AuthClient
# Interface stays the same!
```

**When to migrate**:
- Team size > 10 developers
- Clear service boundaries causing conflicts
- Need independent scaling
- Different deployment cycles needed

---

## Testing Strategy with Installed Tools

### 1. **Database Testing (DBeaver + psql)**

**Manual Testing**:
```sql
-- Test PostGIS
SELECT PostGIS_version();

-- Test spatial query
SELECT ST_Distance(
    ST_GeomFromText('POINT(78.4867 17.3850)', 4326)::geography,
    ST_GeomFromText('POINT(77.5946 12.9716)', 4326)::geography
) / 1000 as distance_km;

-- Test indexes
EXPLAIN ANALYZE
SELECT * FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(78.4867, 17.3850)::geography,
    5000
);
```

**Performance Testing**:
```sql
-- Create test data
INSERT INTO service_requests (requestor_id, service_type, priority, location, description)
SELECT 
    (SELECT user_id FROM users LIMIT 1),
    'MEDICAL',
    'HIGH',
    ST_SetSRID(ST_MakePoint(
        78.4867 + (random() - 0.5) * 0.1,
        17.3850 + (random() - 0.5) * 0.1
    ), 4326),
    'Test request ' || i
FROM generate_series(1, 10000) i;

-- Test query performance
EXPLAIN ANALYZE
SELECT COUNT(*) FROM service_requests
WHERE status = 'SUBMITTED';
```

### 2. **API Testing (HTTPie + Chrome + Swagger)**

**HTTPie (CLI)**:
```bash
# Register user
http POST localhost:8000/api/v1/users/register \
    email=test@example.com \
    password=secure123 \
    full_name="Test User"

# Login
http POST localhost:8000/api/v1/users/login \
    email=test@example.com \
    password=secure123

# Authenticated request
http GET localhost:8000/api/v1/services \
    "Authorization: Bearer <token>"
```

**Swagger UI**:
- Open http://localhost:8000/docs
- Interactive API documentation
- Test all endpoints visually
- See request/response schemas

**Chrome DevTools**:
- Network tab: Monitor API calls
- Console: Debug JavaScript
- Performance: Profile page load
- Lighthouse: Audit accessibility, performance

### 3. **Frontend Testing (Chrome + Bun)**

**Unit Tests**:
```javascript
// frontend/tests/utils.test.js
import { test, expect } from "bun:test";
import { formatDistance } from "../src/utils/geo";

test("format distance in meters", () => {
    expect(formatDistance(500)).toBe("500 m");
});

test("format distance in kilometers", () => {
    expect(formatDistance(1500)).toBe("1.5 km");
});
```

**Run tests**:
```bash
cd frontend
bun test
```

**E2E Testing**:
```javascript
// Use Playwright (install with: bun add -d playwright)
import { test, expect } from '@playwright/test';

test('register new user', async ({ page }) => {
    await page.goto('http://localhost:3000/register');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'secure123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('http://localhost:3000/dashboard');
});
```

### 4. **Load Testing (Apache Bench / Locust)**

**Apache Bench** (simple):
```bash
# Install
sudo apt install apache2-utils

# Test endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/api/v1/services

# With authentication
ab -n 100 -c 10 -H "Authorization: Bearer <token>" \
    http://localhost:8000/api/v1/services
```

**Locust** (advanced):
```python
# locustfile.py
from locust import HttpUser, task, between

class IDRMUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/users/login", json={
            "email": "test@example.com",
            "password": "secure123"
        })
        self.token = response.json()["access_token"]
    
    @task
    def get_services(self):
        self.client.get("/api/v1/services", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    @task(3)  # 3x more frequent
    def get_dashboard(self):
        self.client.get("/api/v1/analytics/dashboard", headers={
            "Authorization": f"Bearer {self.token}"
        })
```

Run:
```bash
conda activate idrm-mvp
pip install locust
locust -f locustfile.py
# Open http://localhost:8089
```

---

## Backup and Recovery

### Automated Backups

```bash
# /etc/cron.daily/idrm-backup
#!/bin/bash
BACKUP_DIR="/home/your-user/projects/idrm-mvp/database/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
PGPASSWORD='idrm_secure_password_2024' pg_dump -U idrm_user idrm_db | \
    gzip > "$BACKUP_DIR/idrm_${TIMESTAMP}.sql.gz"

# Keep only last 30 days
find "$BACKUP_DIR" -name "idrm_*.sql.gz" -mtime +30 -delete

# Optional: Upload to cloud storage
# aws s3 cp "$BACKUP_DIR/idrm_${TIMESTAMP}.sql.gz" s3://backups/idrm/
```

Make executable:
```bash
sudo chmod +x /etc/cron.daily/idrm-backup
```

### Point-in-Time Recovery

Enable WAL archiving:
```bash
# /etc/postgresql/16/main/postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'test ! -f /var/lib/postgresql/16/wal_archive/%f && cp %p /var/lib/postgresql/16/wal_archive/%f'
```

---

## Monitoring and Logging

### System Monitoring

```bash
# PostgreSQL stats
SELECT * FROM pg_stat_database WHERE datname = 'idrm_db';
SELECT * FROM pg_stat_user_tables;

# Connection count
SELECT count(*) FROM pg_stat_activity;

# Slow queries
SELECT pid, now() - query_start as duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '5 seconds';
```

### Application Logging

```python
# backend/app/core/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("idrm")
    logger.setLevel(logging.INFO)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        "logs/idrm.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    logger.addHandler(file_handler)
    return logger
```

---

## Production Deployment Checklist

### Pre-Deployment

- [ ] Security audit completed
- [ ] All tests passing
- [ ] Database migrations tested
- [ ] Backup/restore tested
- [ ] Performance benchmarks met
- [ ] Documentation updated

### Deployment

- [ ] Set up production server (Ubuntu 22.04 LTS)
- [ ] Run setup script
- [ ] Configure firewall (ufw)
- [ ] Set up SSL (Let's Encrypt)
- [ ] Configure Nginx reverse proxy
- [ ] Set production environment variables
- [ ] Enable systemd services
- [ ] Set up monitoring
- [ ] Configure automated backups

### Post-Deployment

- [ ] Verify all services running
- [ ] Test API endpoints
- [ ] Check database connectivity
- [ ] Monitor logs for errors
- [ ] Set up alerts
- [ ] Document deployment

---

## Security Considerations

### Production Security

```bash
# Firewall (ufw)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# PostgreSQL: Restrict to localhost
# /etc/postgresql/16/main/pg_hba.conf
local   all   all   md5
host    all   all   127.0.0.1/32   md5

# Change default passwords
ALTER USER idrm_user WITH PASSWORD '<strong-random-password>';

# Environment variables (never commit)
# /etc/environment or systemd service file
DATABASE_PASSWORD=<strong-random-password>
JWT_SECRET_KEY=<generated-with-openssl-rand-hex-32>
```

---

## Conclusion

This native Ubuntu monolith setup provides:

1. ✅ **Production-ready** from day one
2. ✅ **Better performance** than Docker
3. ✅ **Easier debugging** with standard tools
4. ✅ **Clear evolution path** to microservices
5. ✅ **Industry-standard** practices
6. ✅ **Resource efficient** (~350 MB RAM)
7. ✅ **Fast iteration** (instant hot reload)

**Remember**: The best architecture is one that ships. Start with monolith, evolve when needed!
