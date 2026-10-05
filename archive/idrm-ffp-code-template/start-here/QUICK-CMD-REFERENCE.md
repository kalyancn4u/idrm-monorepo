# IDRM v3 Monolith: Quick Reference Guide
## Everything You Need at Your Fingertips - Multi-Platform Edition

**Version**: 3.0  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Stack**: Bun + Python (Miniconda) + PostgreSQL + Redis

---

## 🎯 v3 Quick Facts

**Three Frontend Platforms**:
- HTML/Tailwind (Port 5173) - Primary web
- React SPA (Port 5174) - Admin dashboards
- React Native (Expo) - iOS + Android mobile

**Key Changes from v2**:
- ❌ Removed: Java/GeoServer, Node.js, npm, venv
- ✅ Added: Python geospatial, Bun, Miniconda, React Native

---

## 🚀 Installation (v3 Stack)

```bash
# Download v3 setup script
wget https://raw.githubusercontent.com/your-repo/idrm-mvp/v3/setup-idrm-v3.sh
chmod +x setup-idrm-v3.sh
./setup-idrm-v3.sh

# What it installs:
# - PostgreSQL 16 + PostGIS 3.4
# - Redis 7.2+
# - Miniconda (Python 3.11)
# - Bun (JavaScript runtime) - NOT Node.js!
# - Expo CLI (for React Native)
# - VSCodium/VSCode
# - DBeaver, Android Studio (optional)

# Time: 20-25 minutes
```

---

## 📁 Daily Workflow (v3 - Three Platforms)

### Full Stack Development (5 Terminals)

```bash
# Terminal 1: Backend
cd ~/projects/idrm-mvp/src/backend/app-python
conda activate idrm-mvp
uvicorn main:app --reload --port 8000

# Terminal 2: API Gateway
cd ~/projects/idrm-mvp/src/backend/api-gateway
bun run dev

# Terminal 3: HTML/Tailwind Frontend
cd ~/projects/idrm-mvp/src/frontend/web-html
bun run dev    # NOT npm run dev!

# Terminal 4: React SPA (Admin)
cd ~/projects/idrm-mvp/src/frontend/web-react
bun run dev

# Terminal 5: React Native (Mobile)
cd ~/projects/idrm-mvp/src/frontend/mobile-expo
npx expo start
```

### Single Platform Focus

```bash
# Working on mobile app only? Just run:

# Terminal 1: Backend
cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload

# Terminal 2: Mobile
cd src/frontend/mobile-expo && npx expo start
```

### URLs (v3)

- **Backend API**: http://localhost:8000
- **API Gateway**: http://localhost:3000
- **HTML/Tailwind**: http://localhost:5173
- **React SPA**: http://localhost:5174
- **API Docs**: http://localhost:8000/docs
- **React Native**: Expo Dev Tools (auto-opens)

---

## 🗄️ Database Commands (Same as v2)

```bash
# Connect
psql -U idrm_user -d idrm_db

# Quick status
sudo systemctl status postgresql
sudo systemctl status redis

# Backup
pg_dump -U idrm_user -d idrm_db > backup.sql
```

---

## 🐍 Python (Miniconda) Commands

**v3 uses Miniconda, NOT venv!**

```bash
# Activate environment
conda activate idrm-mvp

# Install packages (IMPORTANT: use --break-system-packages)
pip install package-name --break-system-packages

# Update environment
conda env update -f environment.yml

# Deactivate
conda deactivate

# List environments
conda env list

# Create new environment
conda create -n idrm-mvp python=3.11
```

**Common mistake**: Don't use `python -m venv` - we use Miniconda!

---

## 🟨 JavaScript (Bun) Commands

**v3 uses Bun, NOT npm or node!**

```bash
# Install dependencies
bun install              # NOT npm install

# Run dev server
bun run dev              # NOT npm run dev

# Build for production
bun run build            # NOT npm run build

# Run script
bun run script.ts        # NOT node script.js

# Execute file directly
bun script.ts

# Install package
bun add package-name     # NOT npm install package-name

# Remove package
bun remove package-name  # NOT npm uninstall
```

**Common mistake**: Using `npm` or `node` commands - use `bun` instead!

---

## 📱 React Native (Expo) Commands

```bash
# Start development server
npx expo start

# Run on iOS simulator
npx expo start --ios

# Run on Android emulator
npx expo start --android

# Clear cache
npx expo start -c

# Build for production
eas build --platform ios
eas build --platform android

# Over-the-air update
eas update --branch production

# Check project
npx expo doctor
```

---

## 🔧 Frontend Commands (Three Platforms)

### HTML/Tailwind

```bash
cd src/frontend/web-html
bun install              # Install dependencies
bun run dev              # Start dev server (port 5173)
bun run build            # Build for production
bun run preview          # Preview production build
```

### React SPA

```bash
cd src/frontend/web-react
bun install              # Install dependencies
bun run dev              # Start dev server (port 5174)
bun run build            # Build for production
bun run preview          # Preview production build
bun run test             # Run tests
```

### React Native

```bash
cd src/frontend/mobile-expo
bun install              # Install dependencies
npx expo start           # Start Expo dev server
npx expo start --ios     # Open iOS simulator
npx expo start --android # Open Android emulator
bun run test             # Run tests
```

---

## 🔌 API Gateway Commands

```bash
cd src/backend/api-gateway
bun install              # Install dependencies
bun run dev              # Start dev server (port 3000)
bun run start            # Start production server
bun test                 # Run tests
```

---

## 🧪 Testing Commands (v3)

```bash
# Backend tests
conda activate idrm-mvp
pytest tests/ -v
pytest tests/test_api.py::test_create_user -v

# HTML/Tailwind tests
cd src/frontend/web-html
bun test

# React SPA tests
cd src/frontend/web-react
bun test
bun test:watch

# React Native tests
cd src/frontend/mobile-expo
bun test
bun test --watch

# Integration tests (all platforms)
cd tests/integration
pytest test_multi_platform.py -v
```

---

## 🚨 Troubleshooting (v3)

### Port Already in Use

```bash
# Check what's using a port
sudo lsof -i :8000    # Backend
sudo lsof -i :3000    # API Gateway
sudo lsof -i :5173    # HTML/Tailwind
sudo lsof -i :5174    # React SPA

# Kill process
kill -9 <PID>
```

### Frontend Won't Connect

```bash
# Check CORS in backend (src/backend/app-python/core/)
allow_origins=[
    "http://localhost:5173",  # HTML/Tailwind (web-html)
    "http://localhost:5174",  # React SPA (web-react)
    "exp://*",                # React Native (mobile-expo)
]

# Check API Gateway is running
curl http://localhost:3000/health
```

### React Native Can't Connect

```bash
# Use your computer's IP, not localhost
# In src/frontend/mobile-expo/src/config.ts:
export const API_URL = "http://192.168.1.100:3000/api/v1";
# Replace 192.168.1.100 with YOUR local IP

# Find your IP:
ip addr show | grep inet
# Or on macOS: ifconfig | grep inet
```

### Python Geospatial Service Issues

```bash
# Install geospatial packages
conda activate idrm-mvp
pip install geopandas shapely gdal fiona pyproj --break-system-packages

# Test geospatial module (inside the monolith)
curl http://localhost:8000/health
```

---

## 📦 Package Management (v3)

### Python (Miniconda)

```bash
# Add package
pip install package-name --break-system-packages

# Add to requirements
echo "package-name==1.0.0" >> requirements.txt

# Update all
pip install -r requirements.txt --break-system-packages
```

### JavaScript (Bun)

```bash
# Add package
bun add package-name

# Add dev dependency
bun add -d package-name

# Update all
bun update

# Remove package
bun remove package-name
```

---

## 🎨 Quick Code Snippets (v3)

### Start All Services Script

```bash
#!/bin/bash
# scripts/dev-all-v3.sh

# Start backend
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload; exec bash"

# Start API Gateway
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/src/backend/api-gateway && bun run dev; exec bash"

# Start HTML/Tailwind
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/src/frontend/web-html && bun run dev; exec bash"

# Start React SPA
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/src/frontend/web-react && bun run dev; exec bash"

# Start React Native
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/src/frontend/mobile-expo && npx expo start; exec bash"

echo "✅ All v3 services started!"
```

### Health Check All Services

```bash
#!/bin/bash
# scripts/health-check-v3.sh

echo "Checking Backend (8000)..."
curl -s http://localhost:8000/health | jq

echo "Checking API Gateway (3000)..."
curl -s http://localhost:3000/health | jq

echo "Checking HTML/Tailwind (5173)..."
curl -s http://localhost:5173 > /dev/null && echo "✅ Running"

echo "Checking React SPA (5174)..."
curl -s http://localhost:5174 > /dev/null && echo "✅ Running"

echo "Checking PostgreSQL..."
sudo systemctl status postgresql --no-pager

echo "Checking Redis..."
sudo systemctl status redis --no-pager
```

---

## 🔐 Environment Variables (v3)

```bash
# src/backend/app-python/.env
DATABASE_URL=postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,exp://*

# src/backend/api-gateway/.env
BACKEND_URL=http://localhost:8000
FRONTEND_HTML_URL=http://localhost:5173
FRONTEND_SPA_URL=http://localhost:5174

# src/frontend/mobile-expo/.env (or src/config.ts)
API_URL=http://192.168.1.100:3000/api/v1  # Use your local IP
```

---

## 📊 Monitoring Commands

```bash
# View logs
journalctl -u idrm-backend -f        # Backend logs
journalctl -u idrm-api-gateway -f    # API Gateway logs
tail -f /var/log/postgresql/*.log    # PostgreSQL logs

# System resources
htop                                  # CPU/RAM usage
df -h                                 # Disk usage
free -h                               # Memory usage

# Database performance
psql -U idrm_user -d idrm_db -c "SELECT * FROM pg_stat_activity;"
```

---

## 🚀 Production Deployment (v3)

```bash
# Build all frontends
cd src/frontend/web-html && bun run build
cd src/frontend/web-react && bun run build

# Build mobile apps
cd src/frontend/mobile-expo
eas build --platform all

# Deploy to server
rsync -avz src/frontend/web-html/dist/ user@server:/var/www/idrm/
rsync -avz src/frontend/web-react/dist/ user@server:/var/www/idrm-admin/

# Restart services
ssh user@server "sudo systemctl restart idrm-backend idrm-api-gateway nginx"
```

---

## 📚 Documentation Links

- **PRD**: IDRM-MVP-PRD-v2.md (v3 review pending)
- **Architecture**: monolith-architecture-v3.md
- **Design System**: design-system-v3.md
- **Contributor Guide**: contributor-guide-v3.md
- **API Docs**: http://localhost:8000/docs

---

## 🎯 Common Commands Summary

**Python (Miniconda)**:
```bash
conda activate idrm-mvp
pip install package --break-system-packages
```

**JavaScript (Bun)**:
```bash
bun install
bun run dev
bun add package
```

**React Native (Expo)**:
```bash
npx expo start
eas build --platform ios
```

**Database**:
```bash
psql -U idrm_user -d idrm_db
sudo systemctl status postgresql
```

---

**IDRM v3 Quick Reference - Multi-Platform Development Made Easy!** 🚀
