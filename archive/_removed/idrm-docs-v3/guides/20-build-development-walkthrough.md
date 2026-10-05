# IDRM v3 · Complete Development Walkthrough

<!-- IDRM-CLEANUP doc=v3-g20-walkthrough status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — build walkthrough (4016 L)
> Gen-3 end-to-end build walkthrough (microservices/Bun-era). Current build path = [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`../../../../docs/mvp/30-design-data-flow-and-modules.md`](../../../../docs/mvp/30-design-data-flow-and-modules.md)
> + conformance gate `docs/mvp/26`. Useful as a reference for step granularity; stack specifics superseded.
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: Beginners to experienced · Status: Archived — v3 historical generation*
*Consolidated from: 49-IDRM-COMPLETE-DEVELOPMENT-GUIDE.md, idrm-development-guide.md, idrm-fullstack-development-guide.md*

## Contents
- [IDRM: Complete Development Guide](#idrm-complete-development-guide)
- [idrm-development-guide.md](#idrm-development-guidemd)
- [idrm-fullstack-development-guide.md](#idrm-fullstack-development-guidemd)

---

## IDRM: Complete Development Guide

### From Zero to Full-Stack Developer - The Beginner's Journey

**Version**: 3.0 Complete  
**Audience**: Complete beginners to experienced developers  
**Reading Time**: 6-8 hours (but worth every minute!)  
**Last Updated**: May 16, 2026

---

### 🎯 **What This Guide Covers**

This is your **COMPLETE ROADMAP** to building the IDRM (Integrated Disaster Response Management) platform from scratch.

**You'll learn**:
- ✅ What IDRM is and why it matters
- ✅ Complete technology stack explained
- ✅ Setting up your development environment
- ✅ Building the frontend (HTML + JavaScript)
- ✅ Building the backend (Python + FastAPI)
- ✅ Working with maps (PostGIS + Leaflet)
- ✅ Testing your code
- ✅ Deploying to production
- ✅ Best practices & tips

**Prerequisites**: None! This guide assumes you're a complete beginner.

---

### 📚 **Table of Contents**

#### **Part 1: Understanding IDRM**
1. [What is IDRM?](#part-1-understanding-idrm)
2. [Real-World Examples](#real-world-examples)
3. [Technology Stack Overview](#technology-stack-overview)
4. [Architecture Explained](#architecture-explained)

#### **Part 2: Setting Up Your Development Environment**
5. [Required Software](#part-2-setting-up-your-development-environment)
6. [IDE Setup](#ide-setup)
7. [Installing Dependencies](#installing-dependencies)
8. [Project Structure](#project-structure)

#### **Part 3: Frontend Development**
9. [HTML & Tailwind CSS](#part-3-frontend-development)
10. [JavaScript Basics](#javascript-basics)
11. [Interactive Maps with Leaflet](#interactive-maps)
12. [API Integration](#api-integration)

#### **Part 4: Backend Development**
13. [Python & FastAPI](#part-4-backend-development)
14. [Database Design](#database-design)
15. [API Development](#api-development)
16. [Authentication & Security](#authentication-security)

#### **Part 5: Testing & Quality**
17. [Testing Strategy](#part-5-testing-quality)
18. [Writing Tests](#writing-tests)
19. [Code Quality](#code-quality)

#### **Part 6: Deployment**
20. [Deployment Overview](#part-6-deployment)
21. [Quick Reference](#quick-reference)

---

## **PART 1: Understanding IDRM**

### 1. **What is IDRM?**

#### 1.1 Simple Explanation

**IDRM** = **Integrated Disaster Response Management**

Think of it as **"Uber for disaster relief"** - connecting people who need help with organizations that can provide it, all on an interactive map.

**Real-World Analogy**:

```
Uber:
┌─────────────────────────────────────┐
│ 1. You need a ride                  │
│ 2. Open app, request ride           │
│ 3. Driver accepts                   │
│ 4. Track driver on map               │
│ 5. Driver arrives, ride completes   │
└─────────────────────────────────────┘

IDRM:
┌─────────────────────────────────────┐
│ 1. Citizen needs help (flood)       │
│ 2. Create request on map            │
│ 3. Provider accepts (NGO/Hospital)  │
│ 4. Track provider on map            │
│ 5. Service delivered, verified      │
└─────────────────────────────────────┘
```

---

#### 1.2 Key Features

**For Citizens** (People who need help):
- 📍 Create service request on map
- 🔒 Choose privacy level (public/private)
- 📱 Track service provider in real-time
- ✅ Verify service completion
- ⭐ Rate the service

**For Service Providers** (NGOs, Hospitals, Volunteers):
- 🔍 See nearby requests
- ✅ Accept requests
- 🗺️ Navigate to location
- ✔️ Mark as complete
- 📊 View service history

**For Coordinators** (Government officials):
- 📊 Dashboard with analytics
- 🚨 Approve critical requests
- 📈 Monitor response times
- 🗂️ Generate reports
- 👥 Manage organizations

---

### 2. **Real-World Examples**

#### 2.1 Mumbai Floods 2024

**Scenario**: Heavy rains cause flooding in Mumbai

```
Day 1 - Morning (10:00 AM):
┌────────────────────────────────────────┐
│ Citizen A (Kurla):                     │
│ "I need medical help, chest pain"      │
│ → Creates MEDICAL request (CRITICAL)   │
│ → Location: 19.0722°N, 72.8809°E       │
└────────────────────────────────────────┘
         ↓
         ↓ System matches nearest hospital
         ↓
┌────────────────────────────────────────┐
│ Sion Hospital:                         │
│ "We can help"                          │
│ → Accepts request                      │
│ → Ambulance dispatched                 │
│ → ETA: 15 minutes                      │
└────────────────────────────────────────┘
         ↓
         ↓ Real-time tracking
         ↓
┌────────────────────────────────────────┐
│ Citizen A:                             │
│ → Sees ambulance approaching on map    │
│ → Receives SMS notification            │
│ → Ambulance arrives in 12 minutes      │
│ → Service completed                    │
│ → Rates 5 stars                        │
└────────────────────────────────────────┘

Total Time: 12 minutes
Lives Saved: 1
Data Recorded: ✅
```

---

#### 2.2 Chennai Cyclone 2025

**Scenario**: Cyclone hits Chennai, mass evacuations needed

```
Day 1 - Evening (6:00 PM):
┌────────────────────────────────────────┐
│ 150 SHELTER requests created           │
│ 75 FOOD requests                       │
│ 50 MEDICAL requests                    │
│ Total: 275 requests in 1 hour          │
└────────────────────────────────────────┘
         ↓
         ↓ IDRM Auto-Matching
         ↓
┌────────────────────────────────────────┐
│ 25 NGOs activated                      │
│ 10 Hospitals on standby                │
│ 5 Government shelters opened           │
│                                        │
│ Matching Algorithm:                    │
│ ├─ Distance (nearest first)            │
│ ├─ Capacity (available resources)      │
│ ├─ Priority (critical first)           │
│ └─ Load balancing (distribute evenly)  │
└────────────────────────────────────────┘
         ↓
         ↓ Results
         ↓
┌────────────────────────────────────────┐
│ 245 requests fulfilled (89%)           │
│ Average response time: 28 minutes      │
│ Lives protected: 275 people            │
│ Data for future planning: ✅           │
└────────────────────────────────────────┘
```

---

### 3. **Technology Stack Overview**

#### 3.1 The Complete Stack

**Frontend** (What users see):
```
HTML/CSS/JavaScript
├─ HTML: Page structure
├─ Tailwind CSS: Beautiful styling
└─ JavaScript: Interactivity

Libraries:
├─ Leaflet.js: Interactive maps
├─ Chart.js: Data visualization
├─ Axios: API calls
└─ DOMPurify: Security (XSS prevention)
```

**Backend** (What powers everything):
```
Python 3.11+
├─ FastAPI: Web framework
├─ Uvicorn: ASGI server
└─ Pydantic: Data validation

Microservices:
├─ Auth Service (Port 8000): Login, registration
├─ Service Management (Port 8001): Request handling
├─ Geospatial API (Port 8002): Map operations
├─ Analytics (Port 8003): Reports, metrics
└─ Notifications (Port 8004): Email, SMS
```

**Database** (Where data lives):
```
PostgreSQL 15+
├─ Main database
├─ PostGIS extension: Geospatial data
└─ Full-text search: pg_trgm

Redis 7+
├─ Session storage
├─ Caching
└─ Rate limiting
```

**Infrastructure** (How it runs):
```
Docker
├─ Containerization
└─ docker-compose.yml

NGINX
├─ Reverse proxy
├─ SSL termination
└─ Load balancing

Monitoring
├─ Prometheus: Metrics
├─ Grafana: Dashboards
└─ Loki: Log aggregation
```

---

#### 3.2 Why These Technologies?

**Why Python + FastAPI?**
```
✅ Fast to develop
✅ Great for data science
✅ Excellent PostGIS support
✅ Automatic API documentation
✅ Type safety with Pydantic
✅ Async support (handles many users)

Alternative: Node.js + Express
❌ Harder PostGIS integration
❌ No native data science libraries
```

**Why PostgreSQL + PostGIS?**
```
✅ Best geospatial database
✅ Free and open-source
✅ ACID compliant (reliable)
✅ Spatial queries (find nearby)
✅ Used by Uber, Instagram, Spotify

Alternative: MongoDB
❌ Weaker geospatial support
❌ No ACID transactions
```

**Why HTML + Tailwind instead of React?**
```
✅ Simpler for beginners
✅ No build process needed
✅ Faster load times
✅ Works without JavaScript
✅ Government websites need accessibility

React is available as advanced option!
```

---

### 4. **Architecture Explained**

#### 4.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        USERS                            │
│  Citizens  |  Providers  |  Coordinators  |  Admins    │
└────────────┬────────────────────────────────────────────┘
             │
             ├─── HTTPS (443) ───┐
             │                   │
┌────────────▼───────────────────▼──────────────────────┐
│                   NGINX (Reverse Proxy)                 │
│  - SSL Termination                                     │
│  - Load Balancing                                      │
│  - Rate Limiting                                       │
│  - Static File Serving                                 │
└────────────┬───────────────────┬──────────────────────┘
             │                   │
    ┌────────▼────────┐   ┌─────▼──────┐
    │   FRONTEND      │   │  BACKEND   │
    │  (Port 3000)    │   │ (Port 8000)│
    │                 │   │            │
    │ HTML/CSS/JS     │   │ FastAPI    │
    │ Tailwind        │   │ Python     │
    │ Leaflet.js      │   │            │
    └─────────────────┘   └─────┬──────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
          ┌─────────▼─────────┐   ┌────────▼────────┐
          │   POSTGRESQL      │   │     REDIS       │
          │  (Port 5432)      │   │  (Port 6379)    │
          │                   │   │                 │
          │  + PostGIS        │   │  Sessions       │
          │  + pg_trgm        │   │  Cache          │
          │                   │   │  Rate Limits    │
          └───────────────────┘   └─────────────────┘
```

---

#### 4.2 Request Flow Example

**User creates a service request**:

```
1. USER ACTION:
   ├─ User fills form on create-service.html
   ├─ Clicks map to set location
   └─ Clicks "Submit"

2. FRONTEND (JavaScript):
   ├─ Validates form data
   ├─ Gets GPS coordinates
   ├─ Creates JSON payload
   └─ Sends POST /api/v1/services

3. NGINX:
   ├─ Receives HTTPS request
   ├─ Checks rate limit (30/min)
   ├─ Verifies SSL
   └─ Forwards to Backend

4. BACKEND (FastAPI):
   ├─ Validates JWT token
   ├─ Checks authorization (RBAC)
   ├─ Validates request data
   ├─ Checks Redis cache
   └─ Processes request

5. DATABASE (PostgreSQL):
   ├─ INSERT INTO service_requests
   ├─ Spatial index on location
   ├─ Triggers for notifications
   └─ Returns service_id

6. RESPONSE PATH:
   Backend → NGINX → Frontend → User
   
   JSON Response:
   {
     "status": "success",
     "data": {
       "service_id": "uuid-here",
       "status": "SUBMITTED",
       "created_at": "2026-05-16T10:00:00Z"
     }
   }

7. FRONTEND:
   ├─ Shows success message
   ├─ Redirects to service-detail.html
   └─ Updates map in real-time

Total Time: ~200ms
```

---

## **PART 2: Setting Up Your Development Environment**

### 5. **Required Software**

#### 5.1 Operating System

**Recommended**: Ubuntu 22.04/24.04 LTS

**Why?**
```
✅ Free and open-source
✅ Best PostgreSQL support
✅ Easy package management (apt)
✅ Production servers use Linux
✅ Great documentation

Also works on:
- macOS (with Homebrew)
- Windows (with WSL2)
```

---

#### 5.2 Installation Checklist

**Core Software**:
```
- [ ] Python 3.11+
- [ ] PostgreSQL 15+ with PostGIS
- [ ] Redis 7+
- [ ] Git
- [ ] Node.js 18+ (optional, for React)
- [ ] Docker & Docker Compose
- [ ] VS Code
```

**Python Packages**:
```
- [ ] FastAPI
- [ ] Uvicorn
- [ ] SQLAlchemy
- [ ] Psycopg (PostgreSQL driver)
- [ ] Pydantic
- [ ] Python-Jose (JWT)
- [ ] Passlib (Password hashing)
- [ ] Redis client
```

---

### 6. **IDE Setup**

#### 6.1 Visual Studio Code

**Why VS Code?**
```
✅ Free and lightweight
✅ Excellent extensions
✅ Integrated terminal
✅ Git built-in
✅ Works on all platforms
✅ Most popular (90M+ users)
```

**Essential Extensions**:

```bash
## Python Development
1. Python (Microsoft)
   - IntelliSense
   - Linting
   - Debugging
   
2. Pylance
   - Type checking
   - Auto-completion

3. Python Indent
   - Auto-correct indentation

## Frontend Development
4. Live Server
   - Instant preview
   - Auto-reload

5. Tailwind CSS IntelliSense
   - Class suggestions
   - Color preview

6. ES7+ React/Redux snippets
   - Code snippets

## Database
7. PostgreSQL
   - Run queries
   - View tables

## Git
8. GitLens
   - Blame annotations
   - History

## Docker
9. Docker
   - Manage containers
   - View logs

## General
10. Better Comments
    - Highlight TODOs
    - Color-code comments

11. Bracket Pair Colorizer
    - Match brackets

12. Error Lens
    - Inline errors
```

**Install all at once**:
```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ritwickdey.liveserver
code --install-extension bradlc.vscode-tailwindcss
code --install-extension dsznajder.es7-react-js-snippets
code --install-extension ckolkman.vscode-postgres
code --install-extension eamodio.gitlens
code --install-extension ms-azuretools.vscode-docker
```

---

#### 6.2 VS Code Configuration

**Create workspace settings** (`.vscode/settings.json`):

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--max-line-length=120"],
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length=120"],
  
  "editor.formatOnSave": true,
  "editor.rulers": [120],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  
  "[javascript]": {
    "editor.tabSize": 2,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  
  "[html]": {
    "editor.tabSize": 2,
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  
  "[css]": {
    "editor.tabSize": 2
  },
  
  "files.exclude": {
    "**/__pycache__": true,
    "**/*.pyc": true,
    "**/venv": true,
    "**/node_modules": true
  },
  
  "files.associations": {
    "*.html": "html"
  },
  
  "emmet.includeLanguages": {
    "javascript": "javascriptreact"
  }
}
```

---

### 7. **Installing Dependencies**

#### 7.1 Python Installation

**Ubuntu/Debian**:
```bash
## Update package list
sudo apt update

## Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

## Verify installation
python3.11 --version
## Output: Python 3.11.x

## Install pip
sudo apt install python3-pip

## Upgrade pip
pip3 install --upgrade pip
```

**macOS**:
```bash
## Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

## Install Python
brew install python@3.11

## Verify
python3.11 --version
```

---

#### 7.2 PostgreSQL + PostGIS Installation

**Ubuntu/Debian**:
```bash
## Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

## Install PostgreSQL + PostGIS
sudo apt update
sudo apt install postgresql-15 postgresql-15-postgis-3

## Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

## Verify
psql --version
## Output: psql (PostgreSQL) 15.x
```

**Create Development Database**:
```bash
## Switch to postgres user
sudo -u postgres psql

## Inside PostgreSQL shell:
postgres=# CREATE DATABASE idrm_dev;
postgres=# CREATE USER idrm_user WITH PASSWORD 'dev_password_123';
postgres=# GRANT ALL PRIVILEGES ON DATABASE idrm_dev TO idrm_user;

## Connect to database
postgres=# \c idrm_dev

## Enable PostGIS extension
idrm_dev=# CREATE EXTENSION postgis;
idrm_dev=# CREATE EXTENSION pg_trgm;  -- For full-text search

## Verify PostGIS
idrm_dev=# SELECT PostGIS_version();

## Exit
idrm_dev=# \q
```

---

#### 7.3 Redis Installation

**Ubuntu/Debian**:
```bash
## Install Redis
sudo apt install redis-server

## Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

## Test Redis
redis-cli ping
## Output: PONG
```

**Configure Redis for Development**:
```bash
## Edit Redis config
sudo nano /etc/redis/redis.conf

## Change these settings:
## maxmemory 256mb
## maxmemory-policy allkeys-lru

## Restart Redis
sudo systemctl restart redis-server
```

---

#### 7.4 Git Installation

**Ubuntu/Debian**:
```bash
sudo apt install git

## Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

## Verify
git --version
```

---

### 8. **Project Structure**

#### 8.1 Clone Repository

```bash
## Create workspace directory
mkdir -p ~/projects
cd ~/projects

## Clone IDRM repository
git clone https://github.com/your-org/idrm.git
cd idrm

## Check structure
ls -la
```

---

#### 8.2 Complete Project Structure

```
idrm/
├── README.md                          # Project overview
├── .gitignore                         # Git ignore file
├── .env.example                       # Environment template
├── docker-compose.yml                 # Docker setup
│
├── frontend/                          # All frontend code
│   ├── index.html                     # Landing page
│   ├── pages/                         # HTML pages
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── forgot-password.html
│   │   ├── app/
│   │   │   ├── dashboard.html
│   │   │   ├── create-service.html
│   │   │   ├── service-detail.html
│   │   │   ├── my-services.html
│   │   │   ├── map.html
│   │   │   ├── profile.html
│   │   │   └── notifications.html
│   │   ├── provider/
│   │   │   ├── provider-dashboard.html
│   │   │   ├── available-services.html
│   │   │   └── active-services.html
│   │   └── admin/
│   │       ├── admin-dashboard.html
│   │       ├── admin-users.html
│   │       └── admin-analytics.html
│   │
│   ├── assets/                        # Static assets
│   │   ├── css/
│   │   │   ├── tailwind.min.css
│   │   │   └── custom.css
│   │   ├── js/
│   │   │   ├── app.js                 # Main app logic
│   │   │   ├── auth.js                # Authentication
│   │   │   ├── services.js            # Service operations
│   │   │   ├── map.js                 # Map interactions
│   │   │   ├── utils.js               # Helper functions
│   │   │   └── config.js              # Configuration
│   │   ├── images/
│   │   └── icons/
│   │
│   └── components/                    # Reusable components
│       ├── navbar.html
│       ├── footer.html
│       └── modals.html
│
├── backend/                           # Python backend
│   ├── main.py                        # FastAPI entry point
│   ├── requirements.txt               # Python dependencies
│   ├── .env                           # Environment variables
│   │
│   ├── app/                           # Application code
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuration
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                # Authentication endpoints
│   │   │   ├── services.py            # Service endpoints
│   │   │   ├── users.py               # User endpoints
│   │   │   ├── organizations.py       # Organization endpoints
│   │   │   ├── geo.py                 # Geospatial endpoints
│   │   │   ├── analytics.py           # Analytics endpoints
│   │   │   └── admin.py               # Admin endpoints
│   │   │
│   │   ├── models/                    # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── service.py
│   │   │   ├── organization.py
│   │   │   └── audit.py
│   │   │
│   │   ├── schemas/                   # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── service.py
│   │   │   └── auth.py
│   │   │
│   │   ├── crud/                      # Database operations
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── service.py
│   │   │   └── organization.py
│   │   │
│   │   ├── core/                      # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py            # JWT, hashing
│   │   │   ├── database.py            # DB connection
│   │   │   ├── redis.py               # Redis client
│   │   │   └── deps.py                # Dependencies
│   │   │
│   │   └── utils/                     # Utilities
│   │       ├── __init__.py
│   │       ├── email.py               # Email sending
│   │       ├── sms.py                 # SMS sending
│   │       └── geospatial.py          # Geo utilities
│   │
│   ├── alembic/                       # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                         # Test files
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_services.py
│   │   └── test_geo.py
│   │
│   └── scripts/                       # Utility scripts
│       ├── seed_database.py
│       └── create_admin.py
│
├── database/                          # Database files
│   ├── schema.sql                     # Database schema
│   ├── init.sql                       # Initialization
│   └── seed.sql                       # Sample data
│
├── docker/                            # Docker files
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
├── nginx/                             # NGINX config
│   └── nginx.conf
│
├── docs/                              # Documentation
│   ├── 00-GETTING-STARTED.md
│   ├── 40-DATA-FORMATS.md
│   ├── 41-CODE-STANDARDS.md
│   ├── 42-VERIFICATION-CHECKLISTS.md
│   ├── 44-API-REFERENCE-MATRIX-v3.1-SECURITY.md
│   ├── 45-DATABASE-QUERY-REFERENCE.md
│   ├── 46-REDIS-OPERATIONS-REFERENCE.md
│   ├── 47-FRONTEND-WORKFLOWS-REFERENCE.md
│   ├── 48-COMPLETE-DEPLOYMENT-GUIDE.md
│   └── 49-IDRM-COMPLETE-DEVELOPMENT-GUIDE.md (this file)
│
└── .github/                           # GitHub specific
    └── workflows/
        └── deploy.yml                 # CI/CD pipeline
```

---

#### 8.3 Setup Virtual Environment

```bash
## Navigate to backend
cd backend

## Create virtual environment
python3.11 -m venv venv

## Activate virtual environment
source venv/bin/activate  # Linux/macOS
## OR
venv\Scripts\activate     # Windows

## You should see (venv) in prompt:
(venv) user@laptop:~/projects/idrm/backend$

## Upgrade pip
pip install --upgrade pip

## Install dependencies
pip install -r requirements.txt

## Verify installation
pip list
```

---

**Continue reading**:
- [Part 3: Frontend Development](#part-3-frontend-development)
- [Part 4: Backend Development](#part-4-backend-development)
- [Part 5: Testing & Quality](#part-5-testing-quality)
- [Part 6: Deployment](#part-6-deployment)

---

## **PART 3: Frontend Development**

### 9. **HTML & Tailwind CSS**

#### 9.1 Why HTML + Tailwind?

**Why not React?**
```
HTML + Tailwind:
✅ Simple for beginners
✅ No build process
✅ Faster load times
✅ Better SEO
✅ Works without JavaScript
✅ Government accessibility requirements

React:
❌ Learning curve
❌ Build process required
❌ Slower initial load
❌ SEO challenges
```

**For complete workflows and examples**, see:
- **47-FRONTEND-WORKFLOWS-REFERENCE.md** - All 18 pages documented
- **24-FRONTEND-IMPLEMENTATION.md** - Detailed implementation

---

#### 9.2 Creating Your First Page

**File**: `frontend/pages/auth/login.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Login - IDRM</title>
  
  <!-- Tailwind CSS -->
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css" rel="stylesheet">
  
  <!-- Axios for API calls -->
  <script src="https://cdn.jsdelivr.net/npm/axios@1.6.0/dist/axios.min.js"></script>
</head>
<body class="bg-gray-50">
  <!-- Container -->
  <div class="min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      
      <!-- Logo -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-600">IDRM</h1>
        <p class="text-gray-600 mt-2">Integrated Disaster Response Management</p>
      </div>
      
      <!-- Login Form -->
      <form id="loginForm">
        <!-- Email -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Email Address
          </label>
          <input 
            type="email" 
            id="email" 
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="your.email@example.com"
          >
        </div>
        
        <!-- Password -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            Password
          </label>
          <input 
            type="password" 
            id="password" 
            required
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="••••••••"
          >
        </div>
        
        <!-- Submit Button -->
        <button 
          type="submit" 
          id="submitBtn"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md transition duration-200"
        >
          Login
        </button>
      </form>
      
      <!-- Links -->
      <div class="mt-6 text-center text-sm">
        <a href="forgot-password.html" class="text-blue-600 hover:underline">
          Forgot password?
        </a>
        <span class="mx-2 text-gray-400">|</span>
        <a href="register.html" class="text-blue-600 hover:underline">
          Create account
        </a>
      </div>
    </div>
  </div>
  
  <!-- JavaScript -->
  <script src="../../assets/js/auth.js"></script>
</body>
</html>
```

---

### 10. **JavaScript Basics**

#### 10.1 Authentication Logic

**File**: `frontend/assets/js/auth.js`

```javascript
// Login form handler
document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  // Get form values
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  
  // Show loading state
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Logging in...';
  
  try {
    // POST request to login endpoint
    const response = await axios.post('/api/v1/auth/login', {
      email: email,
      password: password
    });
    
    // Success!
    const data = response.data.data;
    
    // Store tokens
    sessionStorage.setItem('access_token', data.access_token);
    sessionStorage.setItem('refresh_token', data.refresh_token);
    sessionStorage.setItem('user', JSON.stringify(data.user));
    
    // Redirect to dashboard
    window.location.href = '/app/dashboard.html';
    
  } catch (error) {
    // Handle errors
    if (error.response && error.response.status === 401) {
      showError('Invalid email or password');
    } else {
      showError('Login failed. Please try again.');
    }
    
    // Re-enable button
    submitBtn.disabled = false;
    submitBtn.textContent = 'Login';
  }
});

// Show error message
function showError(message) {
  // Create error toast
  const toast = document.createElement('div');
  toast.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50';
  toast.textContent = message;
  document.body.appendChild(toast);
  
  // Remove after 5 seconds
  setTimeout(() => toast.remove(), 5000);
}
```

**For more examples**, see **47-FRONTEND-WORKFLOWS-REFERENCE.md**

---

### 11. **Interactive Maps**

#### 11.1 Setting Up Leaflet

**Include in HTML**:
```html
<!-- Leaflet CSS -->
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

<!-- Leaflet JS -->
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<!-- Map container -->
<div id="map" style="height: 500px;"></div>
```

**Initialize Map** (`assets/js/map.js`):
```javascript
// Initialize map
const map = L.map('map').setView([17.3850, 78.4867], 13);

// Add tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

// Add marker
const marker = L.marker([17.3850, 78.4867]).addTo(map);
marker.bindPopup('<b>Charminar</b><br>Hyderabad, India');
```

**For complete geospatial queries**, see **45-DATABASE-QUERY-REFERENCE.md**

---

## **PART 4: Backend Development**

### 12. **Python & FastAPI**

#### 12.1 Creating Your First API

**File**: `backend/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="IDRM API",
    description="Integrated Disaster Response Management API",
    version="1.0.0"
)

## CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to IDRM API"}

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-05-16T10:00:00Z"
    }
```

**Run the server**:
```bash
cd backend
source venv/bin/activate

## Start server
uvicorn main:app --reload --port 8000

## Visit: http://localhost:8000/docs
```

**For all API endpoints**, see **44-API-REFERENCE-MATRIX-v3.1-SECURITY.md**

---

### 13. **Database Design**

**For complete schema and queries**, see:
- **45-DATABASE-QUERY-REFERENCE.md** - All SQL queries
- **40-DATA-FORMATS.md** - All data formats

---

## **PART 5: Testing & Quality**

**For complete testing guide**, see **42-VERIFICATION-CHECKLISTS.md**

---

## **PART 6: Deployment**

**For complete deployment guide**, see **48-COMPLETE-DEPLOYMENT-GUIDE.md**

---

### 📋 **Quick Reference**

#### **All Documentation**

```
Getting Started:
├─ 00-GETTING-STARTED.md           # Quick start guide

Architecture & Design:
├─ 01-ARCHITECTURE.md              # System architecture
├─ 02-DATABASE-DESIGN.md           # Database schema

Implementation:
├─ 20-BACKEND-IMPLEMENTATION.md    # Backend guide
├─ 24-FRONTEND-IMPLEMENTATION.md   # Frontend guide

Data & Standards:
├─ 40-DATA-FORMATS.md              # All JSON schemas
├─ 41-CODE-STANDARDS.md            # Coding standards
├─ 42-VERIFICATION-CHECKLISTS.md   # Testing guide

Reference:
├─ 44-API-REFERENCE-MATRIX-v3.1-SECURITY.md  # All APIs
├─ 45-DATABASE-QUERY-REFERENCE.md            # All queries
├─ 46-REDIS-OPERATIONS-REFERENCE.md          # Redis guide
├─ 47-FRONTEND-WORKFLOWS-REFERENCE.md        # Frontend flows

Deployment:
├─ 48-COMPLETE-DEPLOYMENT-GUIDE.md           # Full deployment

Development:
└─ 49-IDRM-COMPLETE-DEVELOPMENT-GUIDE.md     # This file
```

---

### 🎉 **You're Ready!**

**What you've learned**:
✅ IDRM architecture and technology stack
✅ Development environment setup
✅ Frontend development with HTML/JavaScript
✅ Backend development with Python/FastAPI
✅ Database design with PostgreSQL/PostGIS
✅ Testing strategies
✅ Deployment procedures

**Next steps**:
1. Read **50-CONTRIBUTION-GUIDE.md** to contribute
2. Join the team on GitHub
3. Start building!

**Total Documentation**: 50,000+ lines across 10+ documents
**You have everything needed to build IDRM!** 🚀

---

**Document Complete!**  
**Status**: ✅ Production-Ready  
**Version**: 3.0 Complete  
**Last Updated**: May 16, 2026

---

## idrm-development-guide.md

---
title: "The Complete Beginner's Guide to Building Full-Stack Geospatial Apps: Tools, Tips & Best Practices for 2026"
date: 2026-05-16 10:00:00 +0530
categories: [Development, Full-Stack]
tags: [python, full-stack, data-science, geospatial, devops, sdlc, docker, ci-cd]
image:
  path: /assets/img/dev-tools-2026.jpg
  alt: Modern Full-Stack Development Toolkit
---

Building a full-stack application with data science, machine learning, and geospatial components might sound overwhelming—especially if you're just starting out. But here's the good news: with the right tools and a clear understanding of **when to use what**, you can build production-ready applications like the Integrated Disaster Response Management (IDRM) platform efficiently and effectively.

This guide breaks down everything you need to know about modern development tools, from choosing the right IDE to deploying with Docker. We'll focus on practical, beginner-friendly explanations that cut through the jargon.

---

### 🎯 Understanding Your Project Stack

Before diving into tools, let's understand what makes a Full-Stack Development (FSD) project with Data Science & Machine Learning (DSML) unique:

#### The IDRM Tech Stack (Real-World Example)

The IDRM platform demonstrates a modern full-stack geospatial application:

- **Frontend**: HTML/Tailwind CSS (primary), React (advanced web), React Native (mobile)
- **API Gateway**: Bun (high-performance JavaScript runtime)
- **Backend**: Python with FastAPI (microservices architecture)
- **Database**: PostgreSQL with PostGIS (geospatial extension)
- **Caching**: Redis
- **Geospatial**: GeoPandas, Shapely, Rasterio
- **Deployment**: Docker containers with NGINX reverse proxy

**Why this matters**: Understanding your stack helps you choose tools that work together seamlessly rather than fighting against each other.

---

### 💻 Development Environment: Choosing Your IDE

#### For Python Development (Backend & Data Science)

Visual Studio Code with the Python extension is the most widely used Python IDE in 2026, and for good reason:

**Best Choice for Beginners: VS Code**
- ✅ **Free and lightweight**
- ✅ Excellent Python extension with IntelliSense
- ✅ Integrated terminal and debugger
- ✅ Native Git functionality and version control features
- ✅ Works on Windows, macOS, and Linux

**When to Use**: General Python development, FastAPI backends, scripting, and learning

**Setup for Your Project**:
```bash
## Install Python extension
## Search for "Python" by Microsoft in VS Code Extensions

## Install essential extensions:
## - Python (by Microsoft)
## - Pylance (language server)
## - Jupyter (for notebooks)
## - Docker
## - GitLens
```

**Alternative: PyCharm Professional**
- ✅ Deep FastAPI and Django integration
- ✅ Advanced refactoring tools
- ✅ Database tools built-in
- ❌ Paid ($249/year for Professional)

PyCharm Professional's framework-specific depth for Django and FastAPI rewards enterprise backend developers who will recoup its cost in debugging time saved daily.

**When to Use**: Large enterprise projects, complex debugging needs, if budget allows

#### For Data Science & ML Work

**Jupyter Lab / Jupyter Notebook**
- ✅ Most popular notebook software for data science, combining code with markdown and visualizations
- ✅ Supports Python, R, Julia, and 40+ languages
- ✅ Perfect for exploratory data analysis
- ✅ Inline visualization and documentation

Jupyter Lab remains the irreplaceable standard for data science exploration with cell-by-cell execution and inline output rendering as the primary workflow.

**When to Use**: 
- Analyzing geospatial data patterns
- Training ML models
- Creating reports with visualizations
- Prototyping algorithms before production

**Spyder IDE**
- ✅ Interactive console for real-time Python execution and data exploration
- ✅ Variable explorer (like MATLAB)
- ✅ Built-in access to NumPy, pandas, Matplotlib, and scientific libraries

**When to Use**: Scientific computing, numerical analysis, if coming from MATLAB

#### For Frontend Development (HTML/CSS/JavaScript)

**VS Code** (again!) is the top choice:
- ✅ Excellent HTML/CSS/JavaScript support
- ✅ Workspace-based configurations for project-specific settings
- ✅ Live Server extension for instant preview
- ✅ Emmet for fast HTML/CSS writing

**Essential Extensions for Frontend**:
- Live Server
- Tailwind CSS IntelliSense
- ES7+ React/Redux/React-Native snippets (if using React)
- Prettier (code formatting)
- ESLint (code quality)

#### AI-Powered IDEs (The New Frontier)

Cursor and Windsurf are IDE replacements with deep AI integration, allowing chat with your codebase and generation of entire features.

**When to Use AI-Assisted IDEs**:
- Building features faster with natural language
- Learning new frameworks or libraries
- Code review and refactoring
- Multi-file editing with deeper context awareness ($20/month for Cursor)

**Caution**: AI is a tool, not a replacement for thinking—best developers use AI to move faster on routine tasks while spending mental energy on hard problems.

---

### 🛠️ Essential Development Tools by Category

#### 1. Version Control & Collaboration

**Git + GitHub/GitLab (Mandatory)**

Version control is fundamental to modern development—GitHub for code storage, collaboration, and project management.

**Why You Need This**:
- Track every change to your code
- Collaborate with team members
- Roll back mistakes
- Deploy automatically via CI/CD

**Basic Commands You'll Use Daily**:
```bash
## Initialize repository
git init

## Stage and commit changes
git add .
git commit -m "Add authentication service"

## Push to remote
git push origin main

## Create feature branch
git checkout -b feature/geospatial-api

## Pull latest changes
git pull origin main
```

**Pro Tip**: Configure workspace settings per project instead of global settings to maintain consistent linting rules and formatting across teams.

#### 2. API Development & Testing

**Postman / Insomnia**

Postman provides a collaborative, open-source platform for building and testing APIs with over 350 plugins.

**When to Use**:
- Testing your FastAPI endpoints
- Debugging authentication (JWT tokens)
- Creating API documentation
- Sharing API collections with team

**Example Workflow for IDRM**:
1. Create a collection for "Auth Service"
2. Add requests for login, register, refresh token
3. Set environment variables for base URL
4. Use tests to validate responses

#### 3. Database Management

**For PostgreSQL + PostGIS**:

**pgAdmin 4** (GUI tool)
- Visual query builder
- Database design and modeling
- Performance monitoring

**DBeaver** (Universal database tool)
- Supports PostGIS with spatial query capabilities
- Works with multiple databases
- Free and open-source

**When to Use Each**:
- **pgAdmin**: PostgreSQL-specific tasks, production monitoring
- **DBeaver**: Development, working with multiple databases

**QGIS for Geospatial Data**

QGIS is a free, open-source GIS software supporting PostGIS, SpatiaLite, and web services through a unified data model.

**When to Use**:
- Visualizing PostGIS data on maps
- Testing spatial queries and validations
- Creating map layers for your application
- Data preparation and cleaning

**Critical for IDRM**: QGIS helps you verify that your geospatial service generates correct map tiles and GeoJSON data.

#### 4. Python Environment Management

**Miniconda (Recommended for Geospatial Projects)**

Why not regular pip/venv? GeoPandas, GDAL, Rasterio, and other geospatial libraries have complex C/C++ dependencies that Conda handles better than pip.

**Setup for IDRM**:
```bash
## Install Miniconda
## Download from: https://docs.conda.io/en/latest/miniconda.html

## Create environment
conda create -n idrm-mvp python=3.11

## Activate environment
conda activate idrm-mvp

## Install geospatial packages
conda install -c conda-forge geopandas rasterio shapely fiona
conda install -c conda-forge fastapi uvicorn

## Save environment
conda env export > environment.yml
```

**When to Use Conda**:
- ✅ Geospatial projects (GDAL, PostGIS integration)
- ✅ Data science with complex dependencies
- ✅ Scientific computing

**When to Use pip/venv**:
- Simple web applications
- Pure Python projects
- Minimal dependencies

#### 5. Frontend Build Tools

**Vite (Modern Build Tool)**

Vite has replaced older bundlers in many teams due to faster development servers and simpler configuration, supporting modern frameworks out of the box.

**For IDRM React/React Native**:
```bash
## Create React app with Vite
npm create vite@latest idrm-web -- --template react

## Start dev server
npm run dev
```

**Why Vite**:
- Lightning-fast hot module replacement (HMR)
- Optimized production builds
- Simple configuration

**Tailwind CSS**

Tailwind CSS has transformed how developers design user interfaces with utility-first classes for rapid, consistent responsive design.

**Setup**:
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init
```

#### 6. Containerization & Deployment

**Docker (Essential for Modern Deployment)**

In 2026, containerization is not optional—it's a standard practice providing consistency, scalability, and quick deployment.

**Why Docker for IDRM**:
- Same environment on your laptop and production server
- Easy to scale services independently
- Simplified dependency management
- One-command deployment

**Basic Dockerfile for Python Service**:
```dockerfile
## Multi-stage build for production
FROM python:3.11-slim as builder

## Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

## Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

## Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Production stage
FROM python:3.11-slim
COPY --from=builder /opt/venv /opt/venv

## Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

## Copy application code
WORKDIR /app
COPY . .

ENV PATH="/opt/venv/bin:$PATH"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Docker Compose for Local Development**:
```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7.2-alpine
    ports:
      - "6379:6379"

  auth_service:
    build: ./services/auth
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:dev_password@postgres:5432/idrm

volumes:
  postgres_data:
```

**When to Use Docker**:
- ✅ Always in production
- ✅ Team development (ensures everyone has same environment)
- ✅ Microservices architecture
- ✅ CI/CD pipelines

---

### 🔄 SDLC Best Practices: The Complete Development Cycle

#### Phase 1: Planning & Requirements (Weeks 1-2)

**Tools You Need**:
- **Notion / Confluence**: Documentation and requirements
- **Figma**: UI/UX mockups
- **Draw.io**: Architecture diagrams

Smart teams now spend 15-25% of total project time in planning—moving beyond what the client asked for to what the user actually needs.

**For IDRM**:
1. Define user stories (service requester, provider, admin)
2. Create API contracts
3. Design database schema
4. Plan microservice boundaries

#### Phase 2: Development Environment Setup (Week 1)

**Checklist**:
```bash
✅ Install VS Code + extensions
✅ Install Python 3.11 + Miniconda
✅ Install Docker Desktop
✅ Install PostgreSQL + PostGIS locally OR via Docker
✅ Install Git and configure SSH keys
✅ Clone repository and create dev branch
✅ Setup virtual environment
✅ Install project dependencies
✅ Configure .env file for local development
```

#### Phase 3: Development with CI/CD (Weeks 3-12)

**Continuous Integration / Continuous Deployment**

CI/CD introduces automation and monitoring to the complete SDLC, with security integrated early (Shift-Left Security) to reduce costs and improve compliance.

**GitHub Actions (Recommended for IDRM)**

GitHub Actions provides native integration with GitHub repositories, automating workflows directly from pull requests to deployment.

**Example CI Pipeline (.github/workflows/test.yml)**:
```yaml
name: Test and Build

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_PASSWORD: test_password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: |
        docker build -t idrm-auth:${{ github.sha }} ./services/auth
    
    - name: Scan for vulnerabilities
      run: |
        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
          aquasec/trivy image idrm-auth:${{ github.sha }}
```

**CI/CD Best Practices**:

1. **Automate Testing** (80%+ coverage)
   - Aim for 80%+ automated test coverage on critical paths
   - Unit tests, integration tests, API tests

2. **Security Scanning**
   - Integrate automated security testing tools like SAST, DAST, and SCA into CI/CD pipelines to catch vulnerabilities early
   - Scan dependencies for known vulnerabilities
   - Check for hardcoded secrets

3. **Shift-Left Security**
   - Fixing security issues early is significantly cheaper than addressing them post-deployment
   - Security as code, not afterthought

4. **Environment Parity**
   - Use Environment as a Service (EaaS) to provide on-demand ephemeral environments, ensuring all developers work in consistent environments

**Alternative CI/CD Tools**:
- **GitLab CI/CD**: Unified experience covering the entire SDLC with Auto DevOps feature
- **Jenkins**: Maximum control and customization (requires setup)
- **Azure DevOps**: Best for Microsoft ecosystem

#### Phase 4: Testing Strategy

**Testing Pyramid for IDRM**:

```
     /\
    /  \  E2E Tests (Few)
   /____\  
  /      \ Integration Tests (Some)
 /________\
/          \ Unit Tests (Many)
```

**Tools You Need**:

1. **pytest** (Python unit & integration tests)
```bash
## Install
pip install pytest pytest-cov pytest-asyncio

## Run tests
pytest tests/ -v --cov=app
```

2. **Playwright** (E2E browser testing)
Playwright enables automated testing across browsers for frontend validation

3. **k6** (Load testing)
k6 and cloud-based performance testing platforms allow developers to simulate user traffic and identify bottlenecks

**Example Test Structure**:
```python
## tests/test_auth_service.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "SecurePass123!",
        "role": "SERVICE_REQUESTER"
    })
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_login_invalid_credentials():
    response = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrong"
    })
    assert response.status_code == 401
```

#### Phase 5: Deployment (Week 13+)

**Docker Best Practices for Production**:

Multi-stage builds are essential for production images—separate build dependencies from runtime dependencies to reduce image size by 70-90%.

**Security Hardening**:
- Run containers as non-root users, scan for vulnerabilities, and minimize attack surface with distroless or Alpine base images
- Define resource constraints using memory and CPU limits to prevent container resource starvation

**Docker Compose for Production**:
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - api_gateway

  api_gateway:
    image: oven/bun:latest
    command: bun run src/index.ts
    environment:
      - NODE_ENV=production
    depends_on:
      - auth_service
      - geo_service

  auth_service:
    image: idrm-auth:latest
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgis/postgis:16-3.4
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    deploy:
      resources:
        limits:
          memory: 2G
```

**Monitoring & Logging**:
- Prometheus for metrics collection (v2.48.0) integrates well with Python-based data pipelines
- Grafana (v10.0.0) supports seamless integration with Python data sources for real-time dashboards
- ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging
- Sentry for error tracking with AI-powered grouping and fix recommendations

---

### 📚 Geospatial Development Essentials

#### Python Geospatial Libraries

**Core Libraries You'll Use**:

1. **GeoPandas**
   - Like pandas but including geometry columns for geospatial information
   - Perfect for spatial data manipulation

```python
import geopandas as gpd

## Read GeoJSON
services = gpd.read_file('services.geojson')

## Spatial query: Find services within 5km
services_nearby = services[
    services.geometry.distance(point) < 5000
]

## Export to different formats
services_nearby.to_file('nearby.shp')
```

2. **Rasterio**
   - Nice wrapper around GDAL for loading, manipulating, and saving raster geospatial data
   - Satellite imagery, elevation data

3. **Shapely**
   - Library for representing vector geometries in Python
   - Point, Line, Polygon operations

4. **Folium / Leaflet**
   - Interactive web maps
   - Integrates with GeoPandas

**Example: Creating Map Tiles (Replaces GeoServer)**:
```python
from fastapi import FastAPI
import geopandas as gpd
from shapely.geometry import box

app = FastAPI()

@app.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    # Calculate tile bounds
    bounds = tile_to_bbox(z, x, y)
    
    # Query PostGIS for features in bounds
    gdf = gpd.read_postgis(
        f"SELECT * FROM services WHERE ST_Intersects(geom, ST_MakeEnvelope({bounds}))",
        con=engine
    )
    
    # Render tile
    tile = render_vector_tile(gdf, z, x, y)
    return tile
```

#### PostGIS Essential Queries

**Spatial Queries You'll Use Daily**:

```sql
-- Find services within 5km of a point
SELECT * FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(78.9629, 20.5937), 4326)::geography,
    5000  -- meters
);

-- Cluster nearby points
SELECT ST_ClusterKMeans(location, 10) OVER() as cluster_id, *
FROM service_requests;

-- Create spatial index (CRITICAL for performance)
CREATE INDEX idx_services_location 
ON service_requests USING GIST(location);
```

---

### 🎓 Learning Path for Beginners

#### Week 1-2: Foundation
1. **Learn Python basics**
   - Variables, functions, classes
   - [Python.org Tutorial](https://docs.python.org/3/tutorial/)

2. **Understand Git**
   - Commits, branches, merges
   - [Git Book](https://git-scm.com/book/en/v2)

3. **Setup Development Environment**
   - Install VS Code, Python, Docker
   - Create first FastAPI app

#### Week 3-4: Backend Development
1. **FastAPI fundamentals**
   - REST APIs, path operations
   - Request/response models with Pydantic
   - Authentication (JWT)

2. **Database basics**
   - SQL queries
   - PostgreSQL setup
   - SQLAlchemy ORM

#### Week 5-6: Frontend Basics
1. **HTML/CSS/JavaScript**
   - DOM manipulation
   - Fetch API
   - Tailwind CSS

2. **React (if needed)**
   - Components, props, state
   - Hooks (useState, useEffect)

#### Week 7-8: Geospatial
1. **PostGIS basics**
   - Spatial data types
   - Common spatial queries

2. **Python geospatial**
   - GeoPandas operations
   - Map visualization

#### Week 9-12: DevOps & Deployment
1. **Docker**
   - Containers vs VMs
   - Dockerfile creation
   - Docker Compose

2. **CI/CD**
   - GitHub Actions
   - Automated testing

---

### 🚀 Quick Start Checklist for IDRM Project

#### Day 1: Setup
```bash
## 1. Install core tools
brew install python@3.11  # macOS
## OR
sudo apt install python3.11  # Ubuntu

## 2. Install Docker Desktop
## Download from: https://www.docker.com/products/docker-desktop

## 3. Install VS Code
## Download from: https://code.visualstudio.com/

## 4. Clone repository
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp

## 5. Setup Python environment
conda create -n idrm-mvp python=3.11
conda activate idrm-mvp
pip install -r requirements.txt

## 6. Start local services
docker-compose up -d postgres redis

## 7. Run migrations
alembic upgrade head

## 8. Start development server
cd services/auth
uvicorn main:app --reload
```

#### Week 1: Core Development Workflow
```bash
## Every morning
git pull origin develop
conda activate idrm-mvp
docker-compose up -d

## Before committing
pytest tests/
black app/  # Code formatting
flake8 app/  # Linting

## Committing work
git add .
git commit -m "feat: add user registration endpoint"
git push origin feature/user-auth

## Create pull request on GitHub
```

---

### 💡 Tips & Tricks for Efficient Development

#### 1. Use Code Snippets
Create VS Code snippets for common patterns:

```json
// .vscode/python.json
{
  "FastAPI Endpoint": {
    "prefix": "fapi",
    "body": [
      "@router.${1:get}(\"/${2:path}\")",
      "async def ${3:function_name}(",
      "    db: Session = Depends(get_db)",
      "):",
      "    ${4:pass}",
      "    return {\"message\": \"${5:success}\"}"
    ]
  }
}
```

#### 2. Keyboard Shortcuts
Master these VS Code shortcuts:
- `Cmd/Ctrl + P`: Quick file open
- `Cmd/Ctrl + Shift + P`: Command palette
- `F12`: Go to definition
- `Shift + F12`: Find all references
- `Cmd/Ctrl + D`: Select next occurrence

#### 3. Git Aliases
```bash
## Add to ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph --decorate
```

#### 4. Docker Optimization
Layer optimization through strategic ordering of Dockerfile instructions maximizes Docker's build cache effectiveness and speeds up deployments.

**Order matters**:
```dockerfile
## ❌ Bad: Cache invalidated on every code change
COPY . .
RUN pip install -r requirements.txt

## ✅ Good: Dependencies cached separately
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

#### 5. Environment Variables
Never commit secrets! Use `.env` files:

```bash
## .env.example (commit this)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key-here
REDIS_URL=redis://localhost:6379

## .env (never commit)
DATABASE_URL=postgresql://prod_user:real_password@prod.example.com:5432/idrm
JWT_SECRET=actual-production-secret-key
```

---

### 🔧 Troubleshooting Common Issues

#### Docker Problems

**Issue**: "Cannot connect to Docker daemon"
```bash
## Solution: Start Docker Desktop
## On Linux:
sudo systemctl start docker
```

**Issue**: "Port already in use"
```bash
## Find what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

## Kill the process or change port in docker-compose.yml
```

#### Python/Conda Issues

**Issue**: "ModuleNotFoundError: No module named 'geopandas'"
```bash
## Solution: Install in conda, not pip
conda install -c conda-forge geopandas
```

**Issue**: Environment activation not working
```bash
## Initialize conda for your shell
conda init bash  # or zsh, fish, etc.
## Restart terminal
```

#### Git Issues

**Issue**: "Merge conflict"
```bash
## 1. See conflicted files
git status

## 2. Open file, resolve conflicts manually
## Look for <<<<<<< HEAD markers

## 3. Mark as resolved
git add conflicted-file.py
git commit
```

---

### 📖 Additional Resources

#### Official Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [PostGIS](https://postgis.net/documentation/)
- [GeoPandas](https://geopandas.org/en/stable/)
- [Docker](https://docs.docker.com/)
- [React](https://react.dev/)

#### Learning Platforms
- [Real Python](https://realpython.com/) - Python tutorials
- [freeCodeCamp](https://www.freecodecamp.org/) - Full-stack development
- [Coursera: GIS Specialization](https://www.coursera.org/specializations/gis)

#### Communities
- [Stack Overflow](https://stackoverflow.com/)
- [GitHub Discussions](https://github.com/features/discussions)
- [Reddit: r/Python](https://reddit.com/r/Python)
- [Reddit: r/gis](https://reddit.com/r/gis)

---

### 🎯 Key Takeaways

1. **Choose the right tool for the job**: VS Code for general development, Jupyter for data exploration, QGIS for geospatial visualization

2. **Automate everything**: CI/CD isn't optional in 2026—it's how professional teams work

3. **Security first**: Shift-left security by integrating security testing early in the pipeline reduces costs and speeds up releases

4. **Docker is your friend**: Containers solve "works on my machine" forever

5. **Master the fundamentals**: React might not be dominant in five years, but HTTP isn't changing—invest in fundamentals

6. **Start simple, scale gradually**: Don't over-engineer early—build, measure, learn

7. **Document as you go**: Your future self (and team) will thank you

---

### 🚦 What's Next?

Now that you understand the tools and workflow:

1. **Set up your development environment** (Day 1)
2. **Build a simple CRUD API** with FastAPI (Week 1)
3. **Add database** with PostgreSQL (Week 1-2)
4. **Integrate geospatial features** (Week 2-3)
5. **Create frontend** with HTML/Tailwind (Week 3-4)
6. **Dockerize everything** (Week 4)
7. **Setup CI/CD pipeline** (Week 5)
8. **Deploy to production** (Week 6)

Remember: The Software Development Lifecycle in 2026 is not about following rigid rules—it's about creating a repeatable system that reduces risk while maximizing learning and delivery speed.

Building software is a journey of continuous learning. Start small, stay curious, and keep shipping!

---

**Questions or need help?** Drop a comment below or reach out on GitHub Discussions!

*Last updated: May 16, 2026*

---

## idrm-fullstack-development-guide.md

---
title: "IDRM Platform: Complete Full-Stack Development Guide for Beginners"
date: 2026-05-16 14:00:00 +0530
categories: [Full-Stack Development, Disaster Response]
tags: [idrm, full-stack, python, javascript, typescript, bash, devsecops, bun, fastapi, react, react-native, postgresql, redis, docker, ci-cd, sdlc]
image:
  path: /assets/img/posts/idrm-fullstack-guide.png
  alt: "IDRM Platform - Complete Development Guide"
author: idrm-platform
toc: true
comments: true
math: false
mermaid: true
pin: true
---
## IDRM Platform: The Complete Beginner's Guide to Full-Stack Development

> **TL;DR**: Step-by-step guide to building the IDRM disaster response platform using JavaScript, TypeScript, Python, and Bash. Covers the entire SDLC with tools, IDEs, tips, and DevSecOps practices.

---

### 🎯 What is the IDRM Platform?

**IDRM** = **Integrated Disaster Response Management**

Think of it as "Uber for disaster relief" - connecting people who need help with organizations that can provide it, all on an interactive map.

#### Real-World Example

```
During Mumbai Floods 2024:
1. Citizen: "I need medical help at my location" → Creates request on map
2. Coordinator: Sees request → Assigns to nearest hospital
3. Hospital: Accepts → Ambulance dispatched
4. Real-time tracking: Citizen sees ambulance approaching on map
5. Service completed → Transparent record maintained
```

#### Key Features

- 📍 **Live Map**: See all service requests and providers in real-time
- 🚑 **Smart Matching**: Auto-match requests to nearest providers
- 🔒 **Privacy-First**: Anonymous requests supported (ReVV system)
- 💰 **Transparent Donations**: Track exactly where money goes
- 📊 **Analytics**: Data-driven disaster response
- 📱 **Multi-Platform**: Web (HTML + React) + Mobile (iOS + Android)

---

### 🏗️ IDRM Architecture: The Big Picture

#### Technology Stack (What You'll Learn)

```mermaid
graph TB
    A[Users: Citizens, Providers, Coordinators] --> B{Frontend Layer}
  
    B --> C[HTML/CSS/JS + Tailwind<br/>Primary Web Interface]
    B --> D[React SPA<br/>Advanced Web Interface]
    B --> E[React Native<br/>iOS + Android Apps]
  
    C --> F[NGINX Reverse Proxy<br/>Port 80/443<br/>SSL + Load Balance]
    D --> F
    E --> F
  
    F --> G[Bun API Gateway<br/>Port 3000<br/>WebSocket + JWT]
  
    G --> H[Redis Cache<br/>Port 6379<br/>Sessions + Pub/Sub]
    G --> I[Python Microservices<br/>FastAPI + Conda]
  
    I --> J[Auth Service:8000]
    I --> K[Service Mgmt:8001]
    I --> L[Geospatial API:8002]
    I --> M[Analytics:8003]
    I --> N[Notifications:8004]
  
    J --> O[PostgreSQL + PostGIS<br/>Port 5432<br/>Main Database]
    K --> O
    L --> O
    M --> O
    N --> O
  
    style G fill:#4CAF50,color:#fff
    style I fill:#FF9800,color:#fff
    style O fill:#2196F3,color:#fff
```

#### Languages & Their Roles

| Language                  | Where Used               | Why This Language                                                                   | What You'll Build                              |
| ------------------------- | ------------------------ | ----------------------------------------------------------------------------------- | ---------------------------------------------- |
| **JavaScript (JS)** | Frontend (HTML/Tailwind) | ✅ Runs in browser``✅ Dynamic UI``✅ No build needed                 | Interactive maps, forms, real-time updates     |
| **TypeScript (TS)** | React + React Native     | ✅ Type safety``✅ Better IDE support``✅ Catch bugs early            | React components, mobile app screens           |
| **Python**          | Backend microservices    | ✅ Best for data science``✅ PostGIS integration``✅ Fast development | API services, geospatial processing, analytics |
| **Bash**            | DevOps & automation      | ✅ System scripting``✅ Deploy automation``✅ CI/CD pipelines         | Deployment scripts, backups, monitoring        |

---

### 📁 Complete Project Structure

```
idrm-platform/
├── frontend/                          # All frontend code
│   ├── html-tailwind/                 # Primary web interface
│   │   ├── index.html                 # Landing page
│   │   ├── pages/
│   │   │   ├── login.html
│   │   │   ├── map.html               # Main map interface
│   │   │   ├── dashboard.html
│   │   │   └── service-request.html
│   │   ├── js/
│   │   │   ├── app.js                 # Main JavaScript
│   │   │   ├── api.js                 # API client
│   │   │   ├── map.js                 # Leaflet integration
│   │   │   ├── auth.js                # Authentication
│   │   │   └── utils.js               # Helper functions
│   │   ├── css/
│   │   │   ├── tailwind.config.js
│   │   │   └── custom.css
│   │   └── assets/
│   │       ├── icons/
│   │       └── images/
│   │
│   ├── react-spa/                     # React web app (optional)
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── hooks/
│   │   │   ├── utils/
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── react-native/                  # Mobile app
│       ├── src/
│       │   ├── screens/
│       │   ├── components/
│       │   ├── navigation/
│       │   └── App.tsx
│       ├── package.json
│       └── app.json
│
├── backend/                           # All backend code
│   ├── api-gateway/                   # Bun API Gateway
│   │   ├── src/
│   │   │   ├── index.ts               # Main entry
│   │   │   ├── routes/
│   │   │   ├── middleware/
│   │   │   │   ├── auth.ts
│   │   │   │   ├── rateLimit.ts
│   │   │   │   └── cors.ts
│   │   │   └── websocket/
│   │   │       └── server.ts
│   │   └── package.json
│   │
│   └── services/                      # Python microservices
│       ├── auth/                      # Port 8000
│       │   ├── main.py                # FastAPI app
│       │   ├── models.py              # Database models
│       │   ├── schemas.py             # Pydantic schemas
│       │   ├── crud.py                # Database operations
│       │   └── requirements.txt
│       │
│       ├── service_mgmt/              # Port 8001
│       │   ├── main.py
│       │   ├── models.py
│       │   ├── workflow.py            # State machine
│       │   └── matching.py            # Provider matching
│       │
│       ├── geospatial/                # Port 8002 ⭐ CRITICAL
│       │   ├── main.py
│       │   ├── tiles.py               # Map tile generation
│       │   ├── vector.py              # GeoJSON generation
│       │   ├── queries.py             # Spatial queries
│       │   └── clustering.py          # Marker clustering
│       │
│       ├── analytics/                 # Port 8003
│       │   ├── main.py
│       │   ├── metrics.py             # Data aggregation
│       │   ├── ml_models/             # DSML component
│       │   │   ├── disaster_predictor.py
│       │   │   ├── demand_forecast.py
│       │   │   └── models/            # Saved ML models
│       │   └── reports.py
│       │
│       └── notifications/             # Port 8004
│           ├── main.py
│           ├── email.py
│           ├── sms.py
│           └── templates/
│
├── infrastructure/                    # DevOps & deployment
│   ├── docker/
│   │   ├── docker-compose.yml         # All services
│   │   ├── Dockerfile.bun             # API Gateway
│   │   ├── Dockerfile.python          # Python services
│   │   └── Dockerfile.frontend        # Frontend builds
│   │
│   ├── nginx/
│   │   ├── nginx.conf
│   │   └── ssl/                       # SSL certificates
│   │
│   ├── scripts/                       # Bash automation
│   │   ├── deploy.sh                  # Deployment
│   │   ├── backup.sh                  # Database backup
│   │   ├── health-check.sh            # Monitoring
│   │   └── setup-dev.sh               # Dev environment
│   │
│   └── ci-cd/
│       ├── .github/
│       │   └── workflows/
│       │       ├── test.yml
│       │       └── deploy.yml
│       └── .gitlab-ci.yml
│
├── database/
│   ├── migrations/                    # Database schema changes
│   ├── seeds/                         # Test data
│   └── schema.sql                     # Initial schema
│
└── docs/
    ├── api/                           # API documentation
    ├── setup/                         # Setup guides
    └── deployment/                    # Deployment docs
```

---

### 🎓 When to Use Which Language

#### JavaScript (Vanilla JS) - Frontend Basics

**Use For**:

- Primary web interface (HTML/Tailwind)
- Interactive forms and validation
- Leaflet map integration
- Real-time WebSocket updates
- Browser DOM manipulation

**Example Task**: "Display service requests on map"

```javascript
// frontend/html-tailwind/js/map.js
async function loadServiceRequests() {
    // Fetch data from API
    const response = await fetch('/api/services/requests');
    const services = await response.json();
  
    // Display on Leaflet map
    services.forEach(service => {
        const marker = L.marker([service.lat, service.lng])
            .bindPopup(`
                <h3>${service.type}</h3>
                <p>Priority: ${service.priority}</p>
                <button onclick="viewDetails('${service.id}')">View Details</button>
            `);
        marker.addTo(map);
    });
}
```

**Why JS Here**:

- ✅ Runs directly in browser (no build needed)
- ✅ Fast, lightweight
- ✅ Perfect for simple interactivity

---

#### TypeScript - Type-Safe Frontend

**Use For**:

- React SPA (advanced web interface)
- React Native mobile apps
- Bun API Gateway
- Large codebases needing type safety

**Example Task**: "Create reusable React component"

```typescript
// frontend/react-spa/src/components/ServiceCard.tsx
interface ServiceCardProps {
    id: string;
    type: 'medical' | 'food' | 'shelter';
    priority: 'critical' | 'high' | 'medium' | 'low';
    location: {
        lat: number;
        lng: number;
        address: string;
    };
    onAccept: (id: string) => void;
}

export const ServiceCard: React.FC<ServiceCardProps> = ({
    id, type, priority, location, onAccept
}) => {
    return (
        <div className={`card priority-${priority}`}>
            <h3>{type.toUpperCase()} Emergency</h3>
            <p>{location.address}</p>
            <button onClick={() => onAccept(id)}>
                Accept Service
            </button>
        </div>
    );
};
```

**Why TypeScript**:

- ✅ Catches errors at compile-time
- ✅ Better IDE autocomplete
- ✅ Self-documenting interfaces
- ✅ Refactoring safety

---

#### Python - Backend Powerhouse

**Use For**:

- All FastAPI microservices
- Geospatial processing (PostGIS)
- Data science & machine learning
- Background tasks (Celery)
- Database operations

**Example Task**: "Find providers near service request"

```python
## backend/services/geospatial/queries.py
from sqlalchemy import text
from geoalchemy2.functions import ST_DWithin, ST_Distance

async def find_nearby_providers(
    request_lat: float, 
    request_lng: float, 
    radius_km: float = 10,
    service_type: str = 'medical'
) -> list[dict]:
    """
    Find providers within radius of a service request.
  
    Args:
        request_lat: Request latitude
        request_lng: Request longitude
        radius_km: Search radius in kilometers
        service_type: Type of service needed
      
    Returns:
        List of nearby providers with distance
    """
    # PostGIS spatial query
    query = text("""
        SELECT 
            id,
            organization_name,
            service_types,
            ST_Y(location::geometry) as latitude,
            ST_X(location::geometry) as longitude,
            ST_Distance(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
            ) / 1000 AS distance_km
        FROM providers
        WHERE 
            ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                :radius * 1000
            )
            AND :service_type = ANY(service_types)
            AND status = 'active'
        ORDER BY distance_km
        LIMIT 10
    """)
  
    result = await db.execute(
        query, 
        {"lat": request_lat, "lng": request_lng, "radius": radius_km, "service_type": service_type}
    )
  
    return [dict(row) for row in result]
```

**Why Python**:

- ✅ Best PostGIS integration (GeoAlchemy2)
- ✅ Rich data science libraries (pandas, scikit-learn)
- ✅ Fast development (Django/FastAPI)
- ✅ Excellent for ML models

---

#### Bash - DevOps Automation

**Use For**:

- Deployment scripts
- Database backups
- Health monitoring
- CI/CD pipelines
- Server setup automation

**Example Task**: "Automated deployment script"

```bash
#!/bin/bash
## infrastructure/scripts/deploy.sh

set -e  # Exit on error

## Configuration
PROJECT_DIR="/home/idrm-prod/idrm-platform"
BACKUP_DIR="/home/idrm-prod/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "🚀 Starting IDRM Platform Deployment"
echo "====================================="

## Step 1: Backup current database
echo "📦 Creating database backup..."
cd "$PROJECT_DIR"
./infrastructure/scripts/backup.sh
echo "✅ Backup created: ${BACKUP_DIR}/backup_${TIMESTAMP}.sql.gz"

## Step 2: Pull latest code
echo "📥 Pulling latest code from repository..."
git pull origin main
echo "✅ Code updated"

## Step 3: Build Docker images
echo "🐳 Building Docker images..."
docker compose build --no-cache
echo "✅ Images built"

## Step 4: Run database migrations
echo "📊 Running database migrations..."
docker compose run --rm auth alembic upgrade head
echo "✅ Migrations complete"

## Step 5: Deploy with zero downtime
echo "🔄 Deploying services..."
docker compose up -d --no-deps --remove-orphans \
    api-gateway \
    auth \
    service-mgmt \
    geospatial \
    analytics \
    notifications

## Wait for health checks
echo "⏳ Waiting for services to be healthy..."
sleep 30

## Step 6: Verify deployment
echo "✅ Checking service health..."
for service in api-gateway auth service-mgmt geospatial analytics notifications; do
    if ! docker compose ps | grep -q "$service.*healthy"; then
        echo "❌ ERROR: $service is not healthy!"
        echo "Rolling back..."
        docker compose down
        exit 1
    fi
    echo "✅ $service is healthy"
done

## Step 7: Reload NGINX
echo "🔃 Reloading NGINX..."
docker compose exec nginx nginx -s reload

## Step 8: Clean up old images
echo "🧹 Cleaning up old Docker images..."
docker image prune -f

echo ""
echo "🎉 Deployment completed successfully!"
echo "📊 Check status: docker compose ps"
echo "📝 View logs: docker compose logs -f"
```

**Why Bash**:

- ✅ Native to Linux/Unix
- ✅ Perfect for system tasks
- ✅ Simple automation
- ✅ Integrates with all tools

---

### 🛠️ Complete Toolchain for IDRM Development

#### Essential IDEs & Editors

##### 1. Visual Studio Code ⭐ **Primary IDE**

**Best For**: JavaScript, TypeScript, Python (lightweight)

**Why VS Code**:

- Free and lightweight
- 40,000+ extensions
- Git integration
- Built-in terminal
- Remote development (SSH)

**Must-Have Extensions for IDRM**:

```bash
## Install all at once
code --install-extension dbaeumer.vscode-eslint              # JavaScript linting
code --install-extension esbenp.prettier-vscode              # Code formatting
code --install-extension ms-python.python                    # Python support
code --install-extension ms-python.vscode-pylance            # Python IntelliSense
code --install-extension ms-toolsai.jupyter                  # Jupyter notebooks
code --install-extension bradlc.vscode-tailwindcss           # Tailwind autocomplete
code --install-extension rangav.vscode-thunder-client        # API testing
code --install-extension ms-azuretools.vscode-docker         # Docker support
code --install-extension eamodio.gitlens                     # Git superpowers
code --install-extension humao.rest-client                   # Test HTTP requests
```

**Keyboard Shortcuts to Master**:

```
Ctrl+P           → Quick file open
Ctrl+Shift+P     → Command palette
Ctrl+`           → Toggle terminal
Ctrl+/           → Comment line
Alt+↑/↓          → Move line
Ctrl+D           → Select next match
F12              → Go to definition
Shift+Alt+F      → Format document
```

---

##### 2. PyCharm Community ⭐ **For Python/ML**

**Best For**: Python microservices, data science, ML models

**Why PyCharm**:

- Best Python debugger
- Database tools (PostgreSQL)
- Scientific mode (plots, DataFrames)
- Integrated Jupyter notebooks
- FastAPI support

**Perfect For IDRM**:

- Geospatial service development
- Analytics & ML model training
- Database schema management
- PostGIS query testing

---

##### 3. Cursor (AI-Powered) - Optional

**Best For**: AI-assisted coding

**Cost**: $20/month (free tier: 2000 completions)

**Why Consider It**:

- Based on VS Code (same shortcuts)
- AI completes entire functions
- Natural language commands: "Create a FastAPI endpoint to get nearby providers"
- Can generate tests automatically

---

#### Frontend Development Tools

##### Browser Developer Tools

**Chrome DevTools** ⭐ **Essential**

**Key Tabs**:

```
Console       → See JavaScript errors/logs
Network       → Monitor API calls
Elements      → Inspect HTML/CSS
Application   → LocalStorage, cookies
Performance   → Find slowness
Lighthouse    → Performance audit
```

**Quick Tips**:

```javascript
// In Console, test API calls
await fetch('/api/services/requests')
    .then(r => r.json())
    .then(console.log);

// Monitor WebSocket messages
// Network tab → WS → Click connection → Messages
```

---

##### Figma - UI/UX Design

**Cost**: Free (3 projects)

**Use For**:

- Design map interface before coding
- Create mobile app mockups
- Share designs with team
- Export assets (icons, images)

**IDRM Use Case**:

```
1. Design emergency request form
2. Export as PNG/SVG
3. Implement in HTML/React
```

---

#### Backend Development Tools

##### Postman / Thunder Client

**Postman** (Desktop) or **Thunder Client** (VS Code extension)

**Use For**: Testing API endpoints

**Example Test Workflow**:

```
1. POST /api/auth/register
   Body: { email, password, name }
   
2. POST /api/auth/login
   Body: { email, password }
   Response: { access_token }
   
3. GET /api/services/requests
   Header: Authorization: Bearer {access_token}
   
4. POST /api/services/requests
   Header: Authorization: Bearer {access_token}
   Body: { type: "medical", location: {...}, ... }
```

---

##### DBeaver - Database Management

**Cost**: Free

**Best For**: PostgreSQL + PostGIS

**Features**:

- Visual query builder
- ER diagrams
- Export/import CSV
- SQL editor with autocomplete
- Data visualization

**IDRM Use Case**:

```sql
-- Test spatial query in DBeaver
SELECT 
    id, 
    type, 
    ST_AsText(location) as location_text,
    ST_Distance(
        location::geography,
        ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography
    ) / 1000 AS distance_km
FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint(77.2090, 28.6139), 4326)::geography,
    10000  -- 10km radius
)
ORDER BY distance_km;
```

---

#### Data Science & ML Tools

##### Jupyter Lab ⭐ **For Analytics Service**

**Cost**: Free

**Use For**:

- Exploratory data analysis
- ML model training
- Data visualization
- Disaster prediction models

**IDRM Notebooks**:

```
backend/services/analytics/ml_models/notebooks/
├── 1_data_exploration.ipynb          # Understand data
├── 2_feature_engineering.ipynb       # Create features
├── 3_disaster_predictor.ipynb        # Train model
└── 4_demand_forecast.ipynb           # Predict demand
```

**Example Notebook**: Disaster Prediction

```python
## Cell 1: Load data
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/idrm')
df = pd.read_sql("SELECT * FROM service_requests", engine)
gdf = gpd.GeoDataFrame(df, geometry='location')

## Cell 2: Visualize
import matplotlib.pyplot as plt
gdf.plot(column='priority', legend=True, figsize=(12, 8))
plt.title('Service Request Density by Priority')
plt.show()

## Cell 3: Train model
from sklearn.ensemble import RandomForestClassifier

X = df[['latitude', 'longitude', 'time_of_day', 'month']]
y = df['priority']

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

## Cell 4: Save model
import joblib
joblib.dump(model, 'models/disaster_predictor_v1.pkl')
```

---

#### DevOps & Deployment Tools

##### Docker Desktop

**Cost**: Free (personal use)

**Essential For**: Local development that matches production

**Daily Usage**:

```bash
## Start all IDRM services
docker compose up -d

## View running containers
docker compose ps

## View logs
docker compose logs -f api-gateway

## Stop everything
docker compose down

## Rebuild after code changes
docker compose build api-gateway
docker compose up -d --no-deps api-gateway
```

---

##### GitHub / GitLab

**Git Basics Every Developer Needs**:

```bash
## Daily workflow
git status                    # Check changes
git add .                     # Stage all changes
git commit -m "feat: add map clustering"  # Commit
git push origin feature/map   # Push to GitHub

## Feature branch workflow
git checkout -b feature/analytics    # New branch
## ... make changes ...
git add .
git commit -m "feat: add analytics dashboard"
git push origin feature/analytics
## Create Pull Request on GitHub

## Update from main
git checkout main
git pull origin main
git checkout feature/analytics
git merge main

## Fix merge conflicts if any
## git add <resolved-files>
## git commit
```

**Conventional Commits** (Use These):

```bash
feat:     New feature
fix:      Bug fix
docs:     Documentation only
test:     Adding tests
refactor: Code restructuring
chore:    Build/config changes

## Examples
git commit -m "feat: add disaster zone clustering"
git commit -m "fix: resolve map marker overlap"
git commit -m "docs: update API documentation"
```

---

#### Testing Tools

##### For Frontend

**Jest + Testing Library**

```javascript
// frontend/react-spa/src/components/__tests__/ServiceCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { ServiceCard } from '../ServiceCard';

describe('ServiceCard', () => {
    it('renders service details correctly', () => {
        const service = {
            id: '123',
            type: 'medical',
            priority: 'high',
            location: { lat: 28.6, lng: 77.2, address: 'Delhi' }
        };
      
        render(<ServiceCard {...service} onAccept={jest.fn()} />);
      
        expect(screen.getByText('MEDICAL Emergency')).toBeInTheDocument();
        expect(screen.getByText('Delhi')).toBeInTheDocument();
    });
  
    it('calls onAccept when button clicked', () => {
        const mockOnAccept = jest.fn();
        const service = { id: '123', /* ... */ };
      
        render(<ServiceCard {...service} onAccept={mockOnAccept} />);
      
        fireEvent.click(screen.getByText('Accept Service'));
        expect(mockOnAccept).toHaveBeenCalledWith('123');
    });
});
```

---

##### For Backend

**Pytest + FastAPI TestClient**

```python
## backend/services/service_mgmt/tests/test_crud.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_service_request():
    """Test creating a new service request."""
    payload = {
        "type": "medical",
        "priority": "high",
        "location": {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "address": "Connaught Place, Delhi"
        },
        "contact": {
            "name": "John Doe",
            "phone": "+919876543210"
        }
    }
  
    response = client.post(
        "/api/services/requests", 
        json=payload,
        headers={"Authorization": "Bearer test_token"}
    )
  
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "medical"
    assert data["priority"] == "high"
    assert "id" in data

def test_get_nearby_providers():
    """Test geospatial query for nearby providers."""
    response = client.post(
        "/api/geo/nearby",
        json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "radius_km": 5,
            "service_type": "medical"
        }
    )
  
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
  
    # Check first provider
    if len(data) > 0:
        provider = data[0]
        assert "distance_km" in provider
        assert provider["distance_km"] <= 5
```

---

#### Monitoring & Debugging Tools

##### Application Monitoring

**Sentry** (Error Tracking)

**Cost**: Free tier (5,000 errors/month)

**Setup**:

```javascript
// frontend/react-spa/src/index.tsx
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: "your-sentry-dsn",
  environment: "production",
  tracesSampleRate: 1.0,
});
```

```python
## backend/services/auth/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FastApiIntegration()],
    environment="production",
)
```

**Benefit**: Get notified when errors happen in production

---

### 💡 Essential Tips & Tricks

#### 1. Hot Reload Everything

**Bun (API Gateway)**:

```bash
cd backend/api-gateway
bun run --watch src/index.ts
## Auto-restarts on file changes
```

**Python (FastAPI)**:

```bash
cd backend/services/auth
uvicorn main:app --reload --port 8000
## Auto-restarts on file changes
```

**Frontend (Vite)**:

```bash
cd frontend/html-tailwind
bunx vite
## Hot module replacement (instant updates)
```

---

#### 2. Use Environment Variables

**Never commit secrets!**

```bash
## .env (git-ignored)
DB_PASSWORD=your_password_here
JWT_SECRET=your_jwt_secret_here
SENTRY_DSN=your_sentry_dsn

## .env.example (committed)
DB_PASSWORD=CHANGE_ME
JWT_SECRET=CHANGE_ME
SENTRY_DSN=CHANGE_ME
```

**Load in code**:

```python
## Python
import os
from dotenv import load_dotenv

load_dotenv()
db_password = os.getenv("DB_PASSWORD")
```

```typescript
// TypeScript (Bun)
const dbPassword = process.env.DB_PASSWORD;
```

---

#### 3. Use Code Snippets

**VS Code User Snippets**:

```json
// .vscode/snippets/fastapi.json
{
  "FastAPI Endpoint": {
    "prefix": "fapi",
    "body": [
      "@app.${1:post}('/api/${2:endpoint}')",
      "async def ${3:function_name}(${4:params}):",
      "    \"\"\"${5:Description}\"\"\"",
      "    ${6:# TODO: Implementation}",
      "    return {\"success\": True}"
    ]
  }
}
```

Type `fapi` + Tab → Instant FastAPI endpoint!

---

#### 4. Database Migrations (Alembic)

**Track database changes**:

```bash
## Initialize (one-time)
cd backend/services/auth
alembic init migrations

## Create migration
alembic revision --autogenerate -m "add service_requests table"

## Apply migration
alembic upgrade head

## Rollback
alembic downgrade -1
```

**Why**: Never lose database structure, easy rollbacks

---

#### 5. Makefiles for Common Commands

```makefile
## Makefile
.PHONY: dev test deploy

dev:
	docker compose up -d
	cd frontend/html-tailwind && bunx vite &
	cd backend/api-gateway && bun run --watch src/index.ts

test:
	cd backend/services && pytest
	cd frontend/react-spa && bun test

deploy:
	./infrastructure/scripts/deploy.sh

clean:
	docker compose down
	docker system prune -f
```

**Usage**:

```bash
make dev     # Start development environment
make test    # Run all tests
make deploy  # Deploy to production
make clean   # Clean up Docker
```

---

### 🚀 Complete SDLC Workflow for IDRM

#### Phase 1: Planning (Week 1)

**Tasks**:

- [ ] Review PRD v2.0
- [ ] Create GitHub repository
- [ ] Setup project structure
- [ ] Define database schema
- [ ] Design API endpoints

**Tools**:

- Notion/Confluence (documentation)
- Figma (UI design)
- Excalidraw (architecture diagrams)
- GitHub Projects (task tracking)

---

#### Phase 2: Environment Setup (Week 1-2)

**Development Environment Setup**:

```bash
## 1. Clone repository
git clone https://github.com/your-org/idrm-platform.git
cd idrm-platform

## 2. Create project structure
./infrastructure/scripts/setup-dev.sh

## 3. Start services with Docker
docker compose up -d postgres redis

## 4. Setup Miniconda for Python services
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
conda create -n idrm-mvp python=3.11
conda activate idrm-mvp

## 5. Install Python dependencies
cd backend/services/auth
pip install -r requirements.txt

## 6. Install Bun dependencies
cd backend/api-gateway
bun install

## 7. Install frontend dependencies
cd frontend/html-tailwind
bun install

## 8. Setup database
cd database
psql -U postgres -d idrm -f schema.sql
```

---

#### Phase 3: Development (Weeks 2-12)

**Daily Workflow**:

**Morning (9:00 AM)**:

```bash
## 1. Update code
git pull origin main

## 2. Create feature branch
git checkout -b feature/disaster-prediction

## 3. Start dev environment
make dev
## Or manually:
docker compose up -d
cd backend/api-gateway && bun run --watch src/index.ts &
cd frontend/html-tailwind && bunx vite
```

**During Development**:

```bash
## Test API endpoints
curl http://localhost:3000/health

## Test Python service
curl http://localhost:8000/health

## View logs
docker compose logs -f postgres
tail -f backend/services/auth/logs/app.log
```

**Evening (6:00 PM)**:

```bash
## 1. Run tests
cd backend/services && pytest
cd frontend/react-spa && bun test

## 2. Format code
black backend/services/
prettier --write frontend/

## 3. Commit changes
git add .
git commit -m "feat: add disaster prediction model"

## 4. Push to GitHub
git push origin feature/disaster-prediction

## 5. Create Pull Request
## Go to GitHub → Create PR
```

---

#### Phase 4: Testing (Weeks 10-12)

**Testing Checklist**:

```bash
## 1. Unit Tests
cd backend/services/auth && pytest tests/
cd backend/services/service_mgmt && pytest tests/
cd frontend/react-spa && bun test

## 2. Integration Tests
cd backend && pytest tests/integration/

## 3. E2E Tests (Playwright)
cd tests/e2e && bunx playwright test

## 4. Load Testing (K6)
k6 run tests/load/api-stress-test.js

## 5. Security Scan
npm audit
pip-audit
docker scan idrm/api-gateway:latest
```

---

#### Phase 5: Deployment (Week 13+)

**CI/CD Pipeline** (GitHub Actions):

```yaml
## .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
    
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
    
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
    
      - name: Run Tests
        run: |
          cd backend/services && pytest
          cd frontend/react-spa && bun test
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Server
        run: |
          ssh user@server 'cd /app && ./infrastructure/scripts/deploy.sh'
    
      - name: Verify Deployment
        run: |
          curl -f https://api.idrm.gov.in/health
```

---

### 🔒 DevSecOps Practices for IDRM

#### Security Checklist

**Code Security**:

- [ ] No hardcoded secrets
- [ ] Environment variables for config
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS protection (sanitize user input)
- [ ] CSRF tokens for state-changing ops

**Infrastructure Security**:

- [ ] HTTPS enforced (TLS 1.3)
- [ ] Firewall configured (UFW)
- [ ] SSH key authentication only
- [ ] Database ports NOT exposed
- [ ] Redis password protected
- [ ] Rate limiting enabled

**CI/CD Security**:

- [ ] Secrets in GitHub/GitLab secrets (never in code)
- [ ] Dependency scanning (npm audit, pip-audit)
- [ ] Container scanning (Snyk, Trivy)
- [ ] SAST (Static Application Security Testing)
- [ ] DAST (Dynamic Application Security Testing)

---

#### Automated Security Scanning

```yaml
## .github/workflows/security.yml
name: Security Scan

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  push:
    branches: [ main, develop ]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
    
      - name: Scan Python Dependencies
        run: |
          pip install pip-audit
          pip-audit
    
      - name: Scan Node Dependencies
        run: |
          cd frontend/react-spa
          npm audit --audit-level=high
  
  container-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Scan Docker Images
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'idrm/api-gateway:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'
```

---

### 📊 Performance Optimization Tips

#### Frontend Optimization

**1. Code Splitting** (React):

```typescript
// Lazy load heavy components
const MapView = lazy(() => import('./pages/MapView'));
const Dashboard = lazy(() => import('./pages/Dashboard'));

function App() {
    return (
        <Suspense fallback={<Loading />}>
            <Routes>
                <Route path="/map" element={<MapView />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
        </Suspense>
    );
}
```

**2. Image Optimization**:

```bash
## Use WebP format
npm install sharp
npx sharp -i input.png -o output.webp

## Lazy load images
<img loading="lazy" src="map.png" alt="Map" />
```

---

#### Backend Optimization

**1. Database Indexing**:

```sql
-- Add indexes for frequently queried columns
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);
CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location);
CREATE INDEX idx_providers_service_area ON providers USING GIST(service_area);
```

**2. Redis Caching**:

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379)

def cache_result(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
          
            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
          
            # Call function
            result = await func(*args, **kwargs)
          
            # Cache result
            redis_client.setex(cache_key, ttl, json.dumps(result))
          
            return result
        return wrapper
    return decorator

@cache_result(ttl=60)  # Cache for 1 minute
async def get_nearby_providers(lat, lng, radius):
    # Expensive PostGIS query
    return await db.execute(query)
```

---

### 📚 Learning Resources

#### Official Documentation

**Frontend**:

- [Bun Docs](https://bun.sh/docs) ⭐
- [React Docs](https://react.dev)
- [React Native Docs](https://reactnative.dev)
- [Leaflet Docs](https://leafletjs.com)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)

**Backend**:

- [FastAPI Docs](https://fastapi.tiangolo.com) ⭐
- [PostgreSQL Docs](https://www.postgresql.org/docs/16/)
- [PostGIS Docs](https://postgis.net/documentation/)
- [Redis Docs](https://redis.io/docs/)

**DevOps**:

- [Docker Docs](https://docs.docker.com)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [NGINX Docs](https://nginx.org/en/docs/)

---

#### Recommended Courses

**Free**:

- [FreeCodeCamp Full Stack](https://www.freecodecamp.org/)
- [The Odin Project](https://www.theodinproject.com/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)

**Paid** (Worth It):

- Udemy: "Complete FastAPI Course"
- Coursera: "Full Stack Web Development"
- Pluralsight: "Docker and Kubernetes"

---

### 🎯 Quick Start Guide (TL;DR)

#### For Complete Beginners

**Month 1**: Learn Basics

```bash
## 1. Learn Git
https://try.github.io/

## 2. Learn JavaScript
https://javascript.info/

## 3. Learn Python
https://docs.python.org/3/tutorial/
```

**Month 2**: Frontend Basics

```bash
## 1. HTML/CSS fundamentals
https://web.dev/learn/html/

## 2. Tailwind CSS
https://tailwindcss.com/docs

## 3. Build a to-do app
```

**Month 3**: Backend Basics

```bash
## 1. Learn FastAPI
https://fastapi.tiangolo.com/tutorial/

## 2. Learn PostgreSQL
https://www.postgresqltutorial.com/

## 3. Build a simple CRUD API
```

**Month 4+**: Start Contributing to IDRM!

---

#### For Experienced Developers

**Day 1**: Environment Setup

```bash
git clone <repo>
docker compose up -d
make dev
```

**Day 2-7**: Pick a Feature

```bash
## Choose from:
- Implement disaster prediction ML model
- Add real-time provider tracking
- Build mobile app screens
- Improve map performance
```

**Week 2+**: Ship Features!

---

### 🤝 Contributing to IDRM

#### Feature Development Workflow

1. **Pick a Task** from GitHub Issues
2. **Create Branch**: `git checkout -b feature/your-feature`
3. **Code & Test**: Follow guidelines
4. **Commit**: Use conventional commits
5. **Push**: `git push origin feature/your-feature`
6. **PR**: Create Pull Request
7. **Review**: Address feedback
8. **Merge**: Celebrate! 🎉

---

### 📈 Success Metrics

#### Technical KPIs

```
API Response Time:    < 300ms (p95)
Map Load Time:        < 2 seconds
Database Queries:     < 50ms (p95)
Test Coverage:        > 80%
Uptime:              99.9%
```

#### How to Measure

**Backend**:

```python
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

**Frontend**:

```javascript
// Measure with Performance API
const startTime = performance.now();
await fetch('/api/services/requests');
const endTime = performance.now();
console.log(`API call took ${endTime - startTime}ms`);
```

---

### 🎉 Conclusion

You now have a **complete roadmap** for building the IDRM platform!

#### Key Takeaways

**Languages**:

- **JavaScript**: Frontend basics, DOM manipulation
- **TypeScript**: Type-safe React & Bun code
- **Python**: Backend APIs, geospatial, ML
- **Bash**: Deployment & automation

**Tools Mastered**:

- VS Code + PyCharm (IDEs)
- Docker + Docker Compose (Deployment)
- Git + GitHub (Version Control)
- PostgreSQL + PostGIS (Database)
- Bun + FastAPI (Runtime + Framework)

**Best Practices**:

- Test everything (Jest, Pytest)
- Automate deployment (CI/CD)
- Secure by default (DevSecOps)
- Monitor production (Sentry)
- Document code (Comments, README)

---

### 🚀 Next Steps

1. **Complete Prerequisites** from `setup-prerequisites.md`
2. **Setup Development Environment** with Docker
3. **Pick Your Track**:

   - Frontend: Start with HTML/Tailwind map interface
   - Backend: Build auth service with FastAPI
   - Mobile: Create React Native screens
   - DevOps: Setup CI/CD pipeline
   - Data Science: Train disaster prediction model
4. **Build One Feature End-to-End**
5. **Ship It!**

---

### 📞 Get Help

**Stuck? Don't Worry!**

- Check [GitHub Discussions](https://github.com/your-org/idrm-platform/discussions)
- Ask in [Slack/Discord](your-community-link)
- Review [API Documentation](api-docs-link)
- Read [Setup Guides](setup-guides-link)

**Remember**: Every expert was once a beginner. Start small, ship often, learn fast! 🚀

---

**Document Version**: 1.0
**Last Updated**: May 16, 2026
**Based on**: IDRM MVP PRD v2.0

**This guide is living documentation. Found an issue? Submit a PR!**
