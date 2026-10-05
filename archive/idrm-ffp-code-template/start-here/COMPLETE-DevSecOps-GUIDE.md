# IDRM Complete DevSecOps Guide
## Testing Strategy, Code Standards, Verification Checklists, and CI/CD

**Version**: 3.0  
**Coverage Target**: 80% overall · 95% for auth + service request paths  
**Sources**: `TESTING-STRATEGY-v3.md` · `41-CODE-STANDARDS.md` · `42-VERIFICATION-CHECKLISTS.md` · CI/CD from IDRM-DEPLOYMENT-GUIDE.md

---

## Table of Contents

1. [Testing Philosophy](#1-testing-philosophy)
2. [Test Pyramid](#2-test-pyramid)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [End-to-End Testing](#5-end-to-end-testing)
6. [Security Testing](#6-security-testing)
7. [Code Standards](#7-code-standards)
8. [Git Commit Standards](#8-git-commit-standards)
9. [Code Review Checklist](#9-code-review-checklist)
10. [Verification Checklists](#10-verification-checklists)
11. [CI/CD Quality Gates](#11-cicd-quality-gates)

---

## 1. Testing Philosophy

```
PRINCIPLES:
├─ Test early, test often (shift-left)
├─ Automate everything possible
├─ Fast feedback loops (<10s for unit tests)
├─ Test in production-like environments (real postgres + redis in CI)
└─ 80% code coverage minimum; 95% for critical paths

TEST ENVIRONMENTS:
├─ Local (developer machine) — unit + integration
├─ CI (GitHub Actions) — all layers on every PR
├─ Staging (Docker) — E2E + smoke tests
└─ Production — smoke tests only
```

---

## 2. Test Pyramid

```
                    ▲
                   / \
                  / E2E \           ~10 tests  (10%)
                 / (Slow) \         Full user flows
                /──────────\
               /            \
              / Integration  \      ~50 tests  (20%)
             /   (Medium)     \     API endpoint tests
            /──────────────────\
           /                    \
          /    Unit Tests         \  ~200 tests (70%)
         /       (Fast)            \ Isolated functions
        /──────────────────────────\
```

**Distribution target**: 70% unit · 20% integration · 10% E2E

---

## 3. Unit Testing

### Setup

```bash
conda activate idrm-mvp
cd src/backend/app-python
pip install pytest pytest-cov pytest-asyncio httpx
```

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

### conftest.py (Fixtures)

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.main import app
from httpx import AsyncClient

@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("postgresql://idrm_user:password@localhost/idrm_test")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
async def client(test_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def auth_headers(client):
    # Returns valid auth headers for a test citizen user
    ...
```

### Example Unit Test

```python
# tests/test_api/test_services.py
import pytest

class TestCreateServiceRequest:
    async def test_valid_request_creates_service(self, client, auth_headers):
        response = await client.post(
            "/api/v1/services",
            json={
                "service_type": "MEDICAL",
                "priority": "HIGH",
                "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
                "description": "Elderly person needs medical help",
                "num_people_affected": 1,
                "privacy_level": "PUBLIC"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["service_type"] == "MEDICAL"
        assert data["status"] == "SUBMITTED"

    async def test_unauthenticated_request_returns_401(self, client):
        response = await client.post("/api/v1/services", json={})
        assert response.status_code == 401

    async def test_invalid_coordinates_returns_400(self, client, auth_headers):
        response = await client.post(
            "/api/v1/services",
            json={"location": {"type": "Point", "coordinates": [200, 200]}},
            headers=auth_headers
        )
        assert response.status_code == 400
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html --cov-fail-under=80

# Specific test file
pytest tests/test_api/test_auth.py -v

# Specific test
pytest tests/test_api/test_services.py::TestCreateServiceRequest -v
```

---

## 4. Integration Testing

Integration tests use a **real PostgreSQL + Redis** instance (not mocks).

```python
# tests/integration/test_service_flow.py

class TestCompleteServiceFlow:
    async def test_full_service_lifecycle(self, real_db, real_redis):
        # 1. Citizen creates request
        # 2. DM Authority approves
        # 3. Provider accepts
        # 4. Provider marks complete
        # 5. Citizen verifies
        # 6. Rating submitted
        # Assert each step changes status correctly
        ...
```

```bash
# Run integration tests (requires running services)
pytest tests/integration/ -v -m integration
```

---

## 5. End-to-End Testing

E2E tests simulate complete user journeys across the full stack.

```python
# tests/e2e/test_complete_journey.py

class TestDisasterResponseJourney:
    def test_citizen_gets_help_in_emergency(self):
        """
        Full flow: citizen registers → creates CRITICAL request →
        provider accepts → completes → citizen verifies → rates 5 stars
        """
        ...

    def test_mass_casualty_event(self):
        """
        150 simultaneous requests → auto-matching → 89%+ fulfillment
        """
        ...
```

---

## 6. Security Testing

### OWASP Top 10 Checks

```bash
# SQL Injection — test with parameterized queries
# All DB queries use SQLAlchemy ORM or parameterized SQL

# XSS — sanitize all user inputs
pip install bleach
import bleach
clean_description = bleach.clean(user_input)

# CSRF — verify SameSite cookie and CSRF tokens
# Tested via integration test: cross-origin POST without token → 403

# Rate limiting — verify Bun gateway enforces limits
# 6 login attempts within 15 min → 429 on 6th

# JWT security
# - Verify expired token → 401
# - Verify tampered token → 401
# - Verify blacklisted token → 401
```

### Security Test Suite

```bash
# Run security-focused tests
pytest tests/ -v -m security

# Container vulnerability scan (CI/CD)
trivy image ghcr.io/your-org/idrm-backend:latest

# Dependency audit
pip-audit  # Python deps
bun audit  # JS deps
```

---

## 7. Code Standards

### Python Standards

```python
# Good: Descriptive names, type hints, docstring only when WHY is non-obvious
async def find_nearest_providers(
    location: tuple[float, float],
    service_type: str,
    radius_km: float = 25.0
) -> list[Organization]:
    lat, lon = location
    return await crud.organizations.find_within_radius(lat, lon, radius_km, service_type)

# Bad: unclear names, no types
async def get_orgs(loc, svc, r=25):
    return await crud.organizations.find_within_radius(*loc, r, svc)
```

**Rules**:
- Type hints on all function parameters and return types
- `snake_case` for all Python names
- Maximum function length: 50 lines — split if longer
- No `print()` statements in production code — use `logging`
- All async functions must be `await`-ed
- Pydantic schemas for all API request/response shapes

### TypeScript/Bun Standards

```typescript
// Good: explicit types, early return
async function validateToken(token: string): Promise<User | null> {
    if (!token || token.length === 0) return null;
    try {
        const payload = jwt.verify(token, JWT_SECRET) as JWTPayload;
        return await getUser(payload.user_id);
    } catch {
        return null;
    }
}

// Bad: any types, implicit returns
async function validateToken(token) {
    const payload = jwt.verify(token, JWT_SECRET);
    return getUser(payload.user_id);
}
```

**Rules**:
- `camelCase` for variables and functions, `PascalCase` for types and classes
- No `any` type — use proper TypeScript types
- Explicit return types on all exported functions
- ESLint + Prettier enforced via pre-commit hook

### SQL Standards

```sql
-- Good: uppercase keywords, readable formatting
SELECT
    s.service_id,
    s.service_type,
    u.full_name AS requestor_name,
    ST_Distance(s.location::geography, $1::geography) / 1000 AS distance_km
FROM service_requests s
JOIN users u ON s.requestor_id = u.user_id
WHERE s.status = 'SUBMITTED'
  AND s.service_type = $2
ORDER BY distance_km ASC
LIMIT 20;

-- Bad: lowercase, compressed
select s.service_id,s.service_type from service_requests s join users u on s.requestor_id=u.user_id where s.status='SUBMITTED';
```

**Rules**:
- SQL keywords in UPPERCASE
- One clause per line
- All joins explicit (not implicit comma-style)
- All queries parameterized (`$1`, `$2`) — never string-formatted

---

## 8. Git Commit Standards

### Conventional Commits Format

```
<type>(<scope>): <short description>

[optional body — explain WHY, not what]

[optional footer: BREAKING CHANGE, Closes #123]
```

**Types**:
| Type | When to Use |
|------|------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Adding or fixing tests |
| `refactor` | Code change that isn't a feature or fix |
| `docs` | Documentation only |
| `chore` | Build, CI, dependency updates |
| `perf` | Performance improvement |
| `security` | Security fix |

**Examples**:
```
feat(services): add priority auto-detection based on service type

fix(auth): prevent timing attack on login by using constant-time compare

test(geo): add spatial query coverage for radius search edge cases

security(jwt): blacklist token JTI on logout to prevent replay attacks
```

---

## 9. Code Review Checklist

### Security

- [ ] No secrets in code (API keys, passwords) — use env vars
- [ ] All user inputs validated and sanitized
- [ ] Authorization checked (not just authentication)
- [ ] Rate limiting appropriate for endpoint
- [ ] No sensitive data in logs or error messages
- [ ] SQL queries parameterized

### Functionality

- [ ] Happy path tested
- [ ] Edge cases handled (empty input, large values, invalid types)
- [ ] Error responses consistent with API standard format
- [ ] Database migrations included if schema changed

### Code Quality

- [ ] Coverage ≥ 80% for changed code
- [ ] No TODO/FIXME left without a tracking issue
- [ ] No unused imports or variables
- [ ] Function length ≤ 50 lines
- [ ] Breaking changes documented

---

## 10. Verification Checklists

### Before Pushing Code

```
□ Tests pass locally: pytest tests/ -v
□ Coverage met: pytest --cov=app --cov-fail-under=80
□ No linting errors: ruff check app/ or eslint src/
□ No security issues: pip-audit, bun audit
□ Migrations applied: alembic upgrade head
□ Swagger docs still load: http://localhost:8000/docs
□ Frontend still compiles: bun run build
```

### Before Merging PR

```
□ CI pipeline green (all checks pass)
□ Code review approved by at least 1 reviewer
□ No merge conflicts
□ Branch up to date with main
□ Documentation updated if API changed
□ CHANGELOG.md updated if user-visible change
```

### Before Staging Deploy

```
□ All unit + integration tests pass
□ Docker images build successfully
□ .env.staging values verified (no dev values)
□ Alembic migrations tested against staging DB backup
□ Smoke test checklist: auth, create service, geospatial query, WebSocket
```

### Before Production Deploy

```
□ Staging smoke tests pass
□ Database backup taken and verified restorable
□ Rollback plan documented and tested
□ Team notified of deploy window
□ Monitoring dashboards ready (Grafana)
□ On-call contact available during deploy
```

---

## 11. CI/CD Quality Gates

GitHub Actions enforces these gates on every PR. See [IDRM-DEPLOYMENT-GUIDE.md](../docs/IDRM-DEPLOYMENT-GUIDE.md) for full workflow YAML.

### Backend CI (`backend-ci.yml`)

```yaml
steps:
  - Lint + type check (ruff, mypy)
  - Run tests with real postgres + redis (no mocks!)
  - Coverage ≥ 80% (fails PR if not met)
  - Security scan (Trivy container, Snyk dependencies)
  - Docker image build + push to ghcr.io
```

### API Gateway CI (`api-gateway-ci.yml`)

```yaml
steps:
  - ESLint (zero errors allowed)
  - bun test
  - TypeScript type check
  - Docker image build
```

### Frontend CI

```yaml
steps:
  - ESLint + Prettier
  - bun test
  - bun run build (fails on TypeScript errors)
```

### Mobile CI (`mobile-ci.yml`)

```yaml
steps:
  - iOS build on macos-latest
  - Android build
  - Expo preview build
```

### Quality Gate Rules

| Gate | Threshold | Fail behavior |
|------|-----------|--------------|
| Code coverage | ≥ 80% | Block merge |
| ESLint errors | 0 | Block merge |
| TypeScript errors | 0 | Block merge |
| Security vulnerabilities (CRITICAL) | 0 | Block merge |
| Security vulnerabilities (HIGH) | — | Warning only |
| Test failures | 0 | Block merge |

---

**Full source documents**:
- Testing strategy: `docs/IDRM-Testing-Strategy.md`
- Code standards: `CONTRIBUTING.md`
- Verification checklists: `docs/IDRM-Testing-Strategy.md`
- CI/CD workflows: `docs/IDRM-DEPLOYMENT-GUIDE.md` CI/CD section
