> *Type: Guide (novice / how-to) · Audience: Everyone · Status: Archived — v2 historical generation*

# IDRM Monolith: Quick Reference Guide

<!-- IDRM-CLEANUP doc=v2-g01-quickref status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — quick reference → current guides
> Superseded by [`../../../../guides/mvp/00-start-learning-paths.md`](../../../../guides/mvp/00-start-learning-paths.md)
> + [`tech-stack-101`](../../../../guides/mvp/learn/tech-stack-101.md) (component map). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Everything You Need at Your Fingertips

---

## 🚀 Installation (One Command)

```bash
# Download and run setup script
wget https://raw.githubusercontent.com/your-repo/idrm-mvp/main/setup-idrm-ubuntu.sh
chmod +x setup-idrm-ubuntu.sh
./setup-idrm-ubuntu.sh

# Or if you have the script locally:
chmod +x setup-idrm-ubuntu.sh
./setup-idrm-ubuntu.sh
```

**What it installs**:
- PostgreSQL 16 + PostGIS 3.4
- Miniconda (Python 3.11)
- Bun (JavaScript runtime)
- VSCodium/VSCode
- DBeaver
- Google Chrome
- HTTPie, jq, and more

**Time**: 15-20 minutes

---

## 📁 Daily Workflow

### Morning Startup

```bash
# Option 1: Manual start (3 terminals)

# Terminal 1: Check PostgreSQL
sudo systemctl status postgresql
# If not running: sudo systemctl start postgresql

# Terminal 2: Backend
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp
uvicorn app.main:app --reload --port 8000

# Terminal 3: Frontend
cd ~/projects/idrm-mvp/frontend
bun run dev
```

```bash
# Option 2: One-command start (uses script)
cd ~/projects/idrm-mvp
./scripts/dev-start.sh
# Opens terminals automatically
```

### URLs

- **Backend API**: http://localhost:8000
- **API Docs** (Swagger): http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **ReDoc** (Alt API docs): http://localhost:8000/redoc

---

## 🗄️ Database Commands

### Connection

```bash
# Connect to database
psql -U idrm_user -d idrm_db

# Quick query
psql -U idrm_user -d idrm_db -c "SELECT COUNT(*) FROM users;"

# With DBeaver (GUI)
dbeaver &
# Use connection details:
# Host: localhost, Port: 5432
# Database: idrm_db, User: idrm_user
# Password: idrm_secure_password_2024
```

### Common Queries

```sql
-- Check PostGIS version
SELECT PostGIS_version();

-- List all tables
\dt

-- Count records
SELECT 
    'users' as table_name, COUNT(*) FROM users
UNION ALL
SELECT 'service_requests', COUNT(*) FROM service_requests;

-- Recent service requests
SELECT service_id, service_type, status, created_at
FROM service_requests
ORDER BY created_at DESC
LIMIT 10;

-- Services within 10km of a point (Mumbai)
SELECT 
    service_id,
    service_type,
    ST_Distance(
        location::geography,
        ST_MakePoint(72.8777, 19.0760)::geography
    ) / 1000 as distance_km
FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(72.8777, 19.0760)::geography,
    10000
)
ORDER BY distance_km;

-- Database size
SELECT pg_size_pretty(pg_database_size('idrm_db'));
```

### Backup & Restore

```bash
# Backup (automatic script)
cd ~/projects/idrm-mvp
./scripts/backup-db.sh
# Creates: database/backups/idrm_backup_YYYYMMDD_HHMMSS.sql.gz

# Manual backup
PGPASSWORD='idrm_secure_password_2024' pg_dump -U idrm_user idrm_db > backup.sql

# Restore
./scripts/restore-db.sh database/backups/idrm_backup_20241222_120000.sql.gz

# Manual restore
PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user idrm_db < backup.sql
```

---

## 🐍 Python/Conda Commands

### Environment Management

```bash
# List environments
conda env list

# Activate environment
conda activate idrm-mvp

# Deactivate
conda deactivate

# Update environment from file
cd ~/projects/idrm-mvp/backend
conda env update -f environment.yml

# Install new package
conda activate idrm-mvp
pip install package-name

# Freeze dependencies
pip freeze > requirements.txt
```

### Python Shell

```bash
# Activate environment
conda activate idrm-mvp

# Python REPL
python

# IPython (better REPL)
pip install ipython
ipython

# Test database connection
python -c "
from app.db.session import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT 1'))
    print('Database connected!')
"
```

---

## 🎨 Frontend (Bun) Commands

### Development

```bash
cd ~/projects/idrm-mvp/frontend

# Install dependencies
bun install

# Start dev server (with hot reload)
bun run dev

# Build for production
bun run build

# Run tests
bun test

# Add package
bun add package-name

# Add dev dependency
bun add -d package-name

# Remove package
bun remove package-name
```

### Tailwind CSS

```bash
# Build CSS (automatic in dev mode)
bunx tailwindcss -i ./src/styles/tailwind.css -o ./dist/output.css

# Watch mode (separate terminal)
bunx tailwindcss -i ./src/styles/tailwind.css -o ./dist/output.css --watch

# Production build (minified)
bunx tailwindcss -i ./src/styles/tailwind.css -o ./dist/output.css --minify
```

---

## 🧪 Testing

### API Testing with HTTPie

```bash
# Install (if not already)
sudo apt install httpie

# Register user
http POST localhost:8000/api/v1/users/register \
    email=test@example.com \
    password=secure123 \
    full_name="Test User" \
    phone="9876543210"

# Login (save token)
http POST localhost:8000/api/v1/users/login \
    email=test@example.com \
    password=secure123 \
    | jq -r '.access_token' > /tmp/token.txt

# Use token
TOKEN=$(cat /tmp/token.txt)
http GET localhost:8000/api/v1/users/me \
    "Authorization: Bearer $TOKEN"
```

### API Testing with Curl

```bash
# Register user
curl -X POST http://localhost:8000/api/v1/users/register \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "secure123",
        "full_name": "Test User"
    }'

# Login
curl -X POST http://localhost:8000/api/v1/users/login \
    -H "Content-Type: application/json" \
    -d '{
        "email": "test@example.com",
        "password": "secure123"
    }' | jq

# With token
TOKEN="<your-token>"
curl -X GET http://localhost:8000/api/v1/services \
    -H "Authorization: Bearer $TOKEN"
```

### Python Tests

```bash
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::test_create_user

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Load Testing

```bash
# Apache Bench (simple)
ab -n 1000 -c 10 http://localhost:8000/api/v1/services

# Locust (advanced)
conda activate idrm-mvp
pip install locust

# Create locustfile.py (see monolith-architecture.md)
locust -f locustfile.py
# Open http://localhost:8089
```

---

## 🔧 Development Tools

### VSCodium/VSCode

```bash
# Open project
codium ~/projects/idrm-mvp
# or
code ~/projects/idrm-mvp

# Recommended extensions (install from UI):
# - Python (ms-python.python)
# - Pylance (ms-python.vscode-pylance)
# - Tailwind CSS IntelliSense (bradlc.vscode-tailwindcss)
# - Bun (oven.bun-vscode)
# - GitLens (eamodio.gitlens)
```

### Git Workflow

```bash
cd ~/projects/idrm-mvp

# Check status
git status

# Create feature branch
git checkout -b feature/user-authentication

# Stage changes
git add .

# Commit
git commit -m "feat: Add user registration endpoint"

# Push to remote
git push origin feature/user-authentication

# Pull latest
git pull origin main

# Merge main into feature branch
git checkout feature/user-authentication
git merge main
```

---

## 📊 Monitoring

### PostgreSQL Status

```bash
# Service status
sudo systemctl status postgresql

# Active connections
psql -U idrm_user -d idrm_db -c "
SELECT 
    count(*) as total_connections,
    count(*) FILTER (WHERE state = 'active') as active,
    count(*) FILTER (WHERE state = 'idle') as idle
FROM pg_stat_activity;
"

# Database stats
psql -U idrm_user -d idrm_db -c "
SELECT * FROM pg_stat_database WHERE datname = 'idrm_db';
"

# Table sizes
psql -U idrm_user -d idrm_db -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

### Application Logs

```bash
# Backend logs (if using systemd in production)
sudo journalctl -u idrm-backend -f

# Development logs (if using file logging)
tail -f ~/projects/idrm-mvp/logs/idrm.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log

# Nginx logs (production)
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### System Resources

```bash
# CPU and memory
htop

# Disk usage
df -h

# PostgreSQL process
ps aux | grep postgres

# Python process
ps aux | grep python

# Network connections
netstat -tulpn | grep -E '(8000|3000|5432)'
```

---

## 🚨 Troubleshooting

### PostgreSQL Not Starting

```bash
# Check status
sudo systemctl status postgresql

# View logs
sudo tail -100 /var/log/postgresql/postgresql-16-main.log

# Check if port is in use
sudo lsof -i :5432

# Restart service
sudo systemctl restart postgresql

# Check config syntax
sudo -u postgres /usr/lib/postgresql/16/bin/postgres -C config_file
```

### Cannot Connect to Database

```bash
# Test connection
psql -U idrm_user -d idrm_db -h localhost

# Check authentication config
sudo cat /etc/postgresql/16/main/pg_hba.conf

# Verify user exists
sudo -u postgres psql -c "\du"

# Check if database exists
sudo -u postgres psql -c "\l"
```

### Conda Environment Issues

```bash
# Environment doesn't activate
source ~/miniconda3/bin/activate
conda init bash
source ~/.bashrc

# Reinstall environment
conda env remove -n idrm-mvp
conda env create -f backend/environment.yml

# Update conda
conda update -n base conda
```

### Bun Issues

```bash
# Reinstall Bun
curl -fsSL https://bun.sh/install | bash

# Clear cache
rm -rf node_modules
bun install

# Check version
bun --version

# Update Bun
bun upgrade
```

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000
# Kill it: kill -9 <PID>

# Find process using port 3000
sudo lsof -i :3000

# Find process using port 5432
sudo lsof -i :5432
```

### Frontend Not Loading

```bash
cd ~/projects/idrm-mvp/frontend

# Clear and reinstall
rm -rf node_modules
bun install

# Check for errors
bun run dev --verbose

# Build manually
bunx tailwindcss -i ./src/styles/tailwind.css -o ./dist/output.css
```

---

## 📦 Deployment

### Prepare for Production

```bash
# 1. Update production config
cd ~/projects/idrm-mvp/backend

# Create production environment file
cat > .env.production << EOF
DATABASE_URL=postgresql+asyncpg://idrm_user:STRONG_PASSWORD@localhost/idrm_db
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=False
EOF

# 2. Build frontend
cd ~/projects/idrm-mvp/frontend
bun run build

# 3. Test production build
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp
gunicorn app.main:app -k uvicorn.workers.UvicornWorker \
    --workers 4 --bind 0.0.0.0:8000
```

### Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/idrm-backend.service

# Add content (see monolith-architecture.md)

# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable idrm-backend

# Start service
sudo systemctl start idrm-backend

# Check status
sudo systemctl status idrm-backend
```

### Setup Nginx

```bash
# Install nginx
sudo apt install nginx

# Create site config
sudo nano /etc/nginx/sites-available/idrm

# Add configuration (see monolith-architecture.md)

# Enable site
sudo ln -s /etc/nginx/sites-available/idrm /etc/nginx/sites-enabled/

# Test config
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal:
sudo certbot renew --dry-run
```

---

## 🔐 Security Checklist

### Development

- [ ] Don't commit .env files
- [ ] Use strong passwords
- [ ] Keep dependencies updated
- [ ] Review code before committing

### Production

- [ ] Change all default passwords
- [ ] Use environment variables for secrets
- [ ] Enable firewall (ufw)
- [ ] Set up SSL/TLS
- [ ] Configure CORS properly
- [ ] Rate limit API endpoints
- [ ] Regular security updates
- [ ] Set up monitoring
- [ ] Configure automated backups
- [ ] Test backup restoration

---

## 📚 Quick Links

### Documentation

- **API Docs**: http://localhost:8000/docs
- **PostgreSQL Docs**: https://www.postgresql.org/docs/16/
- **PostGIS Docs**: https://postgis.net/documentation/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Bun Docs**: https://bun.sh/docs
- **Tailwind Docs**: https://tailwindcss.com/docs

### Project Files

- **Setup Script**: `setup-idrm-ubuntu.sh`
- **Architecture**: `docs/monolith-architecture.md`
- **Design System**: `docs/design-system.md`
- **Environment Config**: `backend/environment.yml`
- **Frontend Config**: `frontend/package.json`

---

## 💡 Tips & Tricks

### Faster Development

```bash
# Use aliases in ~/.bashrc
alias idrm-backend='cd ~/projects/idrm-mvp/backend && conda activate idrm-mvp && uvicorn app.main:app --reload'
alias idrm-frontend='cd ~/projects/idrm-mvp/frontend && bun run dev'
alias idrm-db='psql -U idrm_user -d idrm_db'

# Reload shell
source ~/.bashrc

# Now just type:
idrm-backend
idrm-frontend
idrm-db
```

### Database Snapshots

```bash
# Create snapshot before major changes
pg_dump -U idrm_user idrm_db > before_migration.sql

# Make changes...

# If something breaks, restore:
psql -U idrm_user idrm_db < before_migration.sql
```

### VS Code Tasks

Create `.vscode/tasks.json`:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Start Backend",
            "type": "shell",
            "command": "conda activate idrm-mvp && uvicorn app.main:app --reload",
            "problemMatcher": []
        },
        {
            "label": "Start Frontend",
            "type": "shell",
            "command": "cd frontend && bun run dev",
            "problemMatcher": []
        }
    ]
}
```

Press `Ctrl+Shift+B` to run tasks!

---

## 🎯 Next Steps

1. **Week 1**: Set up environment, explore codebase
2. **Week 2**: Build first feature end-to-end
3. **Week 3**: Add tests, improve error handling
4. **Week 4**: Polish UI, add documentation

**Remember**: Commit early, commit often! 🚀

---

## 📞 Getting Help

### Log Files

Check these when things go wrong:
- Setup: `~/idrm-setup.log`
- Application: `~/projects/idrm-mvp/logs/idrm.log`
- PostgreSQL: `/var/log/postgresql/postgresql-16-main.log`
- Nginx: `/var/log/nginx/error.log`

### Useful Commands

```bash
# System info
lsb_release -a
uname -r

# Check installed versions
python --version
bun --version
psql --version
git --version

# Disk space
df -h

# Memory usage
free -h

# Running processes
ps aux | grep -E '(python|postgres|bun)'
```

---

**Happy Coding! 🎉**

Remember: The best code is shipped code. Start simple, iterate, improve!
