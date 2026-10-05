# IDRM MVP: Contributor Guide v3.0
## Making Disaster Response Technology Accessible - Multi-Platform Edition

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**Platforms**: HTML/Tailwind + React SPA + React Native + Python Backend

Thank you for your interest in contributing to IDRM! This guide will help you get started with our multi-platform architecture.

---

## Project Vision

IDRM (Integrated Disaster Response Management) is building a unified, map-driven digital platform for coordinating disaster response in India. We believe disaster response technology should be:

- **Open**: Transparent code, open data standards
- **Accessible**: Easy to deploy, easy to contribute
- **Privacy-first**: Protect vulnerable populations
- **Community-driven**: Built by people who care
- **Multi-platform**: Web, admin dashboard, and mobile apps

---

## 🎯 What's New in v3.0

### Three Frontend Interfaces

Contributors can now work on:

1. **HTML/Tailwind (Primary Web)** - `src/frontend/web-html`
   - Main citizen-facing interface
   - Vanilla JS + Tailwind CSS
   - Built with Bun + Vite

2. **React SPA (Advanced Web)** - `src/frontend/web-react`
   - Admin dashboards and analytics
   - TypeScript + React 18 + Tailwind
   - Built with Bun + Vite

3. **React Native (Mobile)** - `src/frontend/mobile-expo`
   - iOS and Android apps
   - TypeScript + Expo
   - Native features (GPS, offline, push)

### Updated Tech Stack

- **Runtime**: Bun (replaced Node.js)
- **Python Env**: Miniconda (replaced venv)
- **Geospatial**: Python service (replaced Java GeoServer)
- **Cache**: Redis (NEW)
- **Three Frontends**: HTML, React, React Native

---

## Ways to Contribute

### 1. Code Contributions

#### Backend (Python/FastAPI)
**What we need**:
- Add new API endpoints
- Improve database queries
- Implement geospatial features
- Add tests
- Improve error handling
- Add validation

**Skills needed**: Python, FastAPI, PostgreSQL, PostGIS

**Good first issues**:
- Add input validation to existing endpoints
- Write tests for uncovered code
- Improve API documentation
- Add error messages
- Optimize database queries

#### Frontend 1: HTML/Tailwind (Primary Web)
**What we need**:
- Improve UI/UX
- Add map visualizations
- Create responsive designs
- Accessibility improvements
- Progressive enhancement
- Offline capabilities

**Skills needed**: HTML, CSS, JavaScript, Tailwind, Leaflet

**Good first issues**:
- Fix accessibility issues (WCAG 2.1)
- Improve mobile responsiveness
- Add loading states
- Improve error messages
- Add keyboard navigation

#### Frontend 2: React SPA (Admin Dashboard)
**What we need**:
- Build admin components
- Create data visualizations
- Implement complex forms
- Add state management
- Build analytics dashboards
- Add charts and graphs

**Skills needed**: React, TypeScript, Tailwind, Redux/Zustand, Charts

**Good first issues**:
- Create reusable components
- Add TypeScript types
- Build data tables
- Implement filtering
- Add pagination

#### Frontend 3: React Native (Mobile)
**What we need**:
- Build mobile screens
- Implement offline functionality
- Add GPS/location features
- Implement push notifications
- Optimize performance
- Add native animations

**Skills needed**: React Native, TypeScript, Expo, Native APIs

**Good first issues**:
- Build basic screens
- Add form validation
- Implement offline queue
- Add loading indicators
- Improve navigation

#### Python Geospatial Service (NEW)
**What we need**:
- Tile generation optimization
- GeoJSON serving
- Spatial query optimization
- Caching strategies
- Map styling

**Skills needed**: Python, GeoPandas, Shapely, PostGIS

**Good first issues**:
- Add caching to tile endpoint
- Optimize spatial queries
- Add more map styles
- Improve error handling

#### DevOps/Infrastructure
**What we need**:
- CI/CD improvements
- Deployment automation
- Monitoring setup
- Performance optimization
- Security hardening

**Skills needed**: Docker, NGINX, systemd, Linux, GitHub Actions

**Good first issues**:
- Add health check endpoints
- Improve logging
- Add monitoring metrics
- Optimize Docker images
- Add security headers

### 2. Documentation

**What we need**:
- API documentation
- User guides
- Deployment tutorials
- Architecture diagrams
- Code comments
- README improvements
- Translations (Hindi, regional languages)

**Good first issues**:
- Fix typos
- Improve code comments
- Add examples to API docs
- Create beginner tutorials
- Translate UI strings

### 3. Testing

**What we need**:
- Unit tests (backend)
- Integration tests
- E2E tests (frontend)
- Mobile app tests
- Load testing
- Security testing
- Accessibility testing

**Good first issues**:
- Add tests for uncovered functions
- Write E2E test cases
- Add accessibility tests
- Test edge cases

### 4. Design & UX

**What we need**:
- UI/UX improvements
- Accessibility enhancements
- Mobile-first designs
- Design system updates
- User research
- Usability testing

**Good first issues**:
- Improve color contrast
- Add loading states
- Improve error messages
- Create mockups
- Test on real devices

### 5. Translation

**What we need**:
- Hindi translation
- Regional language support (Tamil, Telugu, Bengali, etc.)
- RTL support (if needed)

**Good first issues**:
- Translate UI strings
- Add language files
- Test translations

---

## Getting Started

### Prerequisites

```bash
# Required software
- Ubuntu 22.04 or 24.04 (or WSL2 on Windows)
- Git
- Python 3.11 (via Miniconda)
- Bun 1.x
- PostgreSQL 16 + PostGIS 3.4
- Redis 7.2+
- Node.js 18+ (for React Native only)

# Optional
- VS Code / VSCodium
- DBeaver (database GUI)
- Expo Go app (for mobile testing)
```

### Setup Development Environment

**1. Clone Repository**

```bash
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp
```

**2. Install Backend Dependencies**

```bash
# Create Miniconda environment
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

# Install Python packages
cd src/backend/app-python
pip install --break-system-packages -r requirements.txt

# Install geospatial libraries
conda install -c conda-forge geopandas shapely gdal fiona -y
```

**3. Setup Database**

```bash
# Create database and user
sudo -u postgres psql -c "CREATE USER idrm_user WITH PASSWORD 'idrm_pass';"
sudo -u postgres psql -c "CREATE DATABASE idrm_db OWNER idrm_user;"
sudo -u postgres psql -d idrm_db -c "CREATE EXTENSION postgis;"

# Run migrations
cd src/backend/app-python
alembic upgrade head
```

**4. Install Frontend Dependencies**

```bash
# HTML/Tailwind frontend
cd src/frontend/web-html
bun install

# React SPA frontend
cd src/frontend/web-react
bun install

# React Native mobile
cd src/frontend/mobile-expo
bun install
```

**5. Start Development Servers**

> **Why 5 terminals?** Each service is an independent process that must run simultaneously.
> The API Gateway (Terminal 2) is the traffic director — ALL browser requests go through it first
> before reaching the Python backend. Skipping it makes the app unreachable from any frontend.

```bash
# Terminal 1: Python Backend (FastAPI monolith — all modules on port 8000)
cd src/backend/app-python
conda activate idrm-mvp
uvicorn main:app --reload --port 8000

# Terminal 2: API Gateway (Bun — the front door; routes, JWT checks, rate limiting)
cd src/backend/api-gateway
bun run dev              # Port 3000 (HTTP) + 3001 (WebSocket)

# Terminal 3: HTML/Tailwind Frontend (citizen-facing)
cd src/frontend/web-html
bun run dev              # Port 5173

# Terminal 4: React SPA Frontend (admin dashboards)
cd src/frontend/web-react
bun run dev              # Port 5174

# Terminal 5 (optional): React Native Mobile
cd src/frontend/mobile-expo
npx expo start
```

---

## Development Workflow

### Git Workflow

We use **GitHub Flow** (simplified Git workflow):

```bash
# 1. Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/add-search-filter

# 2. Make changes and commit
git add .
git commit -m "feat: add search filter to service list"

# 3. Push to your fork
git push origin feature/add-search-filter

# 4. Create Pull Request on GitHub
# - Add description
# - Link related issues
# - Request reviewers

# 5. Address review feedback
# Make changes
git add .
git commit -m "fix: address review comments"
git push origin feature/add-search-filter

# 6. Merge (after approval)
# Maintainers will merge your PR
```

### Commit Message Convention

We follow **Conventional Commits**:

```bash
# Format
<type>(<scope>): <subject>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation changes
style:    Code style (formatting, no code change)
refactor: Code refactoring
test:     Add or update tests
chore:    Maintenance tasks

# Examples
feat(api): add search endpoint for services
fix(map): correct marker positioning
docs(readme): update installation steps
style(frontend): format code with prettier
refactor(db): optimize service query
test(api): add tests for auth endpoints
chore(deps): update dependencies
```

### General Coding Principles

| Principle | Rule | Quick example |
|-----------|------|---------------|
| **DRY** | Don't Repeat Yourself — extract repeated logic into a function | `count_by_type(services, 'MEDICAL')` instead of three identical list comprehensions |
| **KISS** | Keep it simple — one clear way, not a clever one | `return priority == 'CRITICAL'` not `True if priority == 'CRITICAL' else False` |
| **YAGNI** | Build only what's needed now, not what might be needed later | Don't add `export_to_pdf()` until a feature card requests it |
| **Fail Fast** | Validate before acting, not after | `service.validate()` then `service.save()` — never the reverse |

---

### Code Style

#### Python (Backend)

```bash
# Format with black
black src/backend/app-python/

# Lint with ruff
ruff check src/backend/app-python/

# Type check with mypy
mypy src/backend/app-python/

# Before committing
black src/backend/app-python/ && ruff check src/backend/app-python/ && mypy src/backend/app-python/
```

**Naming conventions**:

| Identifier | Convention | Example |
|-----------|------------|---------|
| Variables & functions | `snake_case` | `service_request`, `get_user()` |
| Classes | `PascalCase` | `ServiceRequest`, `ProviderMatcher` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_RADIUS_KM` |
| Private methods | `_leading_underscore` | `_validate_and_approve()` |
| Modules | `snake_case` | `service_manager.py` |

**Code style**:
- Use type hints on all public functions
- Max line length: 88 (black default)
- Follow PEP 8
- Google-style docstrings (Args / Returns / Raises)

**Error handling** — always specific, never bare `except`:
```python
# Bad
try:
    service.approve()
except:
    print("Error")

# Good
try:
    service.approve()
except ServiceNotFoundError:
    raise HTTPException(status_code=404, detail="Service not found")
except InsufficientPermissionsError:
    raise HTTPException(status_code=403, detail="Forbidden")
except Exception as e:
    logger.exception("Unexpected error in service approval")
    raise HTTPException(status_code=500, detail="Internal server error")
```

```python
# Good
async def get_service_by_id(
    service_id: int,
    db: Session = Depends(get_db)
) -> ServiceResponse:
    """
    Get service request by ID.
    
    Args:
        service_id: Unique service identifier
        db: Database session
        
    Returns:
        ServiceResponse with service details
        
    Raises:
        HTTPException: If service not found
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return ServiceResponse.from_orm(service)
```

#### JavaScript/TypeScript (Frontend)

```bash
# Format with Prettier
bun run format

# Lint with ESLint
bun run lint

# Type check (TypeScript)
bun run type-check

# Before committing
bun run format && bun run lint && bun run type-check
```

**Code style**:
- Use TypeScript for React projects
- Use const/let, not var
- Use arrow functions
- Use template literals
- Follow Airbnb style guide

```typescript
// Good (React component)
import { useState, useEffect } from 'react';
import { ServiceCard } from '@/components';
import { getServices } from '@/services/api';
import type { Service } from '@/types';

export const ServiceList = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const fetchServices = async () => {
      try {
        const data = await getServices();
        setServices(data);
      } catch (error) {
        console.error('Failed to fetch services:', error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchServices();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <div className="space-y-4">
      {services.map(service => (
        <ServiceCard key={service.id} service={service} />
      ))}
    </div>
  );
};
```

#### SQL

**Keywords**: UPPERCASE · **Identifiers**: snake_case · **Indentation**: 4 spaces

```sql
-- Good SQL formatting
SELECT
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    ST_AsGeoJSON(s.location)::json AS location,
    u.full_name                     AS requestor_name,
    o.name                          AS provider_organization
FROM service_requests s
INNER JOIN users         u ON s.requestor_id = u.user_id
LEFT  JOIN organizations o ON s.provider_id  = o.org_id
WHERE s.status   IN ('APPROVED', 'IN_PROGRESS')
  AND s.priority IN ('CRITICAL', 'HIGH')
  AND s.created_at >= NOW() - INTERVAL '7 days'
ORDER BY s.priority DESC, s.created_at ASC
LIMIT 100;
```

**Always use parameterised queries — never string interpolation**:

```python
# BAD — SQL injection vulnerability
query = f"SELECT * FROM service_requests WHERE service_type = '{service_type}'"

# GOOD — parameterised (asyncpg / SQLAlchemy style)
query = "SELECT * FROM service_requests WHERE service_type = $1"
result = await db.execute(query, service_type)
```

**Comment complex queries**:

```sql
-- Find CRITICAL services waiting > 30 min without a provider.
-- Used by the alert system to notify coordinators.
WITH pending_critical AS (
    SELECT service_id,
           EXTRACT(EPOCH FROM (NOW() - created_at)) / 60 AS minutes_waiting
    FROM service_requests
    WHERE priority = 'CRITICAL'
      AND status   = 'APPROVED'
      AND provider_id IS NULL
)
SELECT * FROM pending_critical
WHERE minutes_waiting > 30
ORDER BY minutes_waiting DESC;
```

---

### API Design Standards

**URL pattern**: `/api/v{version}/{resource}`

```
GET    /api/v1/services              ← List
POST   /api/v1/services              ← Create
GET    /api/v1/services/{id}         ← Get one
PUT    /api/v1/services/{id}         ← Full update
DELETE /api/v1/services/{id}         ← Delete
POST   /api/v1/services/{id}/approve ← State action (verb sub-resource)
GET    /api/v1/users/{id}/services   ← Nested resource
```

**HTTP methods**:

| Method | Purpose | Idempotent? | Body? |
|--------|---------|-------------|-------|
| GET | Retrieve | ✅ Yes | ❌ No |
| POST | Create / action | ❌ No | ✅ Yes |
| PUT | Replace | ✅ Yes | ✅ Yes |
| PATCH | Partial update | ❌ No | ✅ Yes |
| DELETE | Remove | ✅ Yes | ❌ Usually no |

**Consistent response envelope**:

```json
// Success
{ "status": "success", "data": { ... } }

// List
{ "status": "success", "data": { "items": [...], "total": 45, "page": 1, "per_page": 20 } }

// Error
{ "detail": "Service not found", "code": "NOT_FOUND", "field": null }
```

**Status codes** — use the right one:

```python
# 201 Created  — new resource
return JSONResponse(status_code=201, content={"status": "success", "data": service})

# 204 No Content — success, nothing to return (DELETE)
return Response(status_code=204)

# 400 Bad Request — validation failed
raise HTTPException(status_code=400, detail="Invalid service type")

# 401 Unauthorized — not authenticated
raise HTTPException(status_code=401, detail="Authentication required")

# 403 Forbidden — authenticated but not allowed
raise HTTPException(status_code=403, detail="Only DM_Authority can approve")

# 404 Not Found — resource missing
raise HTTPException(status_code=404, detail=f"Service {service_id} not found")

# 429 Too Many Requests — rate limited
raise HTTPException(status_code=429, headers={"Retry-After": "60"})
```

---

## Testing

### Backend Tests (pytest)

```bash
cd src/backend/app-python

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/api/test_services.py -v

# Run tests matching pattern
pytest -k "test_create" -v

# Run only failed tests
pytest --lf
```

**Writing tests**:

```python
# tests/api/test_services.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_service():
    """Test creating a service request.

    Key points for contributors:
    - service_type and priority MUST be UPPERCASE — the DB CHECK constraint rejects lowercase.
    - There is no 'title' field; use 'description' instead.
    - location uses GeoJSON format: [longitude, latitude] (NOT latitude-first).
    """
    response = client.post(
        "/api/v1/services",
        json={
            "service_type": "MEDICAL",        # UPPERCASE — enforced by database
            "description": "Urgent medical supplies needed for flood victims",
            "priority": "HIGH",               # UPPERCASE — enforced by database
            "location": {
                "type": "Point",
                "coordinates": [72.8777, 19.0760]  # [longitude, latitude] — GeoJSON order
            },
            "address": "Dharavi, Mumbai, Maharashtra",
            "num_people_affected": 5,
            "privacy_level": "PUBLIC"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["data"]["service_type"] == "MEDICAL"
    assert data["data"]["status"] == "SUBMITTED"   # initial status is always SUBMITTED

def test_get_services():
    """Test listing services — response is a wrapped object, not a bare list."""
    response = client.get("/api/v1/services")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "items" in data["data"]
    assert isinstance(data["data"]["items"], list)
```

### Frontend Tests (Vitest)

```bash
cd src/frontend/web-react

# Run tests
bun test

# Watch mode
bun test:watch

# Coverage
bun test:coverage
```

**Writing tests**:

```typescript
// components/Button.test.tsx
import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    
    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledOnce();
  });
  
  it('applies variant styles', () => {
    render(<Button variant="danger">Delete</Button>);
    const button = screen.getByText('Delete');
    expect(button).toHaveClass('bg-error');
  });
});
```

---

## Pull Request Guidelines

### Before Submitting

- [ ] Code follows style guidelines (black, prettier, eslint)
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated (if needed)
- [ ] Commit messages follow convention
- [ ] No console.log or debug code
- [ ] Code is self-documenting or well-commented

### PR Description Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Closes #123

## How to Test
1. Start all 5 servers (see Setup Step 5 above — backend, gateway, frontends)
2. FastAPI interactive docs (for backend-only testing): http://localhost:8000/docs
3. Full stack via gateway: http://localhost:3000/api/v1
3. Test endpoint: POST /api/v1/services
4. Verify response

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] No breaking changes (or documented)
```

---

## Code Review Process

### As a Contributor

**When you submit a PR**:
1. Wait for automated checks (CI/CD) to pass
2. Address any failing tests or linting issues
3. Respond to reviewer comments
4. Make requested changes
5. Mark conversations as resolved
6. Request re-review when ready

**Responding to feedback**:
```markdown
# Good response
> Could we add error handling here?

Good catch! I've added try-catch and appropriate error messages.
Updated in commit abc123.

# Not helpful response
> Could we add error handling here?

Done.
```

### As a Reviewer

**What to check**:

| Category | Checklist items |
|----------|----------------|
| **Functionality** | Code does what it's supposed to · edge cases handled · no obvious bugs |
| **Code quality** | Follows PEP 8 / Airbnb · DRY · functions small and focused · no magic numbers |
| **Testing** | Unit tests included · tests actually test what they claim · coverage doesn't drop |
| **Documentation** | Docstrings on public functions · inline comments explain *why*, not *what* |
| **Security** | No SQL injection · no hardcoded secrets · input validated · ownership checked |
| **Performance** | No N+1 queries · proper indexes used · cache considered for hot paths |

**Feedback guidelines**:
- Be kind and constructive
- Explain the "why" behind suggestions
- Distinguish between required changes and suggestions
- Praise good solutions
- Use "we" not "you"

```markdown
# Good feedback
We could improve performance here by caching the result. 
This endpoint might be called frequently.

Suggestion: Add Redis caching with 5-minute TTL.

# Not helpful feedback
This is slow.
```

---

## Anti-Patterns to Avoid

### God Object — don't put everything in one class

```python
# Bad — one class doing 50 things
class ServiceManager:
    def create(self): ...
    def approve(self): ...
    def send_notification(self): ...
    def calculate_distance(self): ...
    def generate_report(self): ...
    def export_to_csv(self): ...   # ... 50 more

# Good — separate concerns
class ServiceRepository: ...      # data access only
class ServiceApprovalService: ... # approval logic only
class NotificationService: ...    # notifications only
```

### Hardcoded values — use constants or config

```python
# Bad
if len(critical_services) > 10:
    send_alert("admin@example.com")

# Good
from config import CRITICAL_SERVICE_THRESHOLD, ADMIN_EMAIL
if len(critical_services) > CRITICAL_SERVICE_THRESHOLD:
    send_alert(ADMIN_EMAIL)
```

### Premature optimisation — measure before caching

```python
# Bad — triple-caching a function called once per hour
@lru_cache(maxsize=1000)
@redis_cache(ttl=3600)
@memory_cache(size=500)
def calculate_monthly_stats(): ...

# Good — cache only what's proven hot
@redis_cache(ttl=300)          # called 10,000×/second — worth it
def get_nearby_services(location): ...
```

---

## Platform-Specific Guidelines

### HTML/Tailwind Frontend

**Component structure**:
```html
<!-- components/service-card.html -->
<div class="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
  <div class="flex items-start justify-between">
    <div class="flex-1">
      <h3 class="text-lg font-medium text-neutral-900 mb-1">
        {title}
      </h3>
      <p class="text-sm text-neutral-600">
        {description}
      </p>
    </div>
  </div>
</div>
```

**JavaScript modules**:
```javascript
// js/api.js
export class ApiClient {
  // Always point at the Bun API Gateway (port 3000), NOT the raw FastAPI backend (port 8000).
  // The gateway enforces JWT auth, rate limits, and CORS before requests reach Python.
  constructor(baseURL = 'http://localhost:3000/api/v1') {
    this.baseURL = baseURL;
  }
  
  async getServices() {
    const response = await fetch(`${this.baseURL}/services`);
    if (!response.ok) throw new Error('Failed to fetch services');
    return response.json();
  }
}
```

### React SPA Frontend

**Component structure**:
```typescript
// components/ServiceCard.tsx
import { Service } from '@/types';

interface ServiceCardProps {
  service: Service;
  onView?: (id: number) => void;
}

export const ServiceCard = ({ service, onView }: ServiceCardProps) => {
  return (
    <div className="bg-white rounded-lg shadow-sm border-l-4 border-priority-high p-6">
      <h3 className="text-lg font-medium text-neutral-900">
        {service.title}
      </h3>
      <p className="text-sm text-neutral-600">
        {service.description}
      </p>
      {onView && (
        <button onClick={() => onView(service.id)}>
          View Details
        </button>
      )}
    </div>
  );
};
```

### React Native Mobile

**Component structure**:
```typescript
// components/ServiceCard.tsx
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Colors, Typography } from '@/design-tokens';
import type { Service } from '@/types';

interface ServiceCardProps {
  service: Service;
  onPress?: () => void;
}

export const ServiceCard = ({ service, onPress }: ServiceCardProps) => {
  return (
    <TouchableOpacity 
      style={styles.card} 
      onPress={onPress}
      activeOpacity={0.7}
    >
      <Text style={styles.title}>{service.title}</Text>
      <Text style={styles.description}>{service.description}</Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 8,
    padding: 16,
    borderLeftWidth: 4,
    borderLeftColor: Colors.priority.high.default,
  },
  title: {
    fontSize: Typography.fontSize.lg,
    fontWeight: Typography.fontWeight.medium,
    color: Colors.neutral[900],
    marginBottom: 4,
  },
  description: {
    fontSize: Typography.fontSize.sm,
    color: Colors.neutral[600],
  },
});
```

---

## Community

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: Questions, ideas, general discussion
- **Pull Requests**: Code contributions
- **Discord** (optional): Real-time chat (if set up)

### Code of Conduct

We follow the [Contributor Covenant](https://www.contributor-covenant.org/):

- Be respectful and inclusive
- Welcome newcomers
- Focus on what's best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

**Not acceptable**:
- Harassment or discrimination
- Trolling or insulting comments
- Publishing others' private information
- Unwelcome sexual attention

---

## Recognition

Contributors are recognized:

- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- GitHub contributor badge
- Special recognition for major contributions

---

## Questions?

- Check existing [GitHub Issues](https://github.com/your-org/idrm-mvp/issues)
- Ask in [GitHub Discussions](https://github.com/your-org/idrm-mvp/discussions)
- Read the docs in `/docs`
- Reach out to maintainers

---

## Thank You!

Every contribution, no matter how small, helps make disaster response technology more accessible. Thank you for being part of this mission! 🙏

**Together, we're building technology that saves lives.** ❤️
