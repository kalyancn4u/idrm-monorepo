# IDRM Testing Strategy
## Unit · Integration · E2E · Performance · Security

**Version**: 3.0  
**Sources**: `backup/TESTING-STRATEGY-v3.md` + `backup/42-VERIFICATION-CHECKLISTS.md`  
**Coverage Target**: 80% overall · 95% critical paths (auth, services)  
**Last Updated**: May 30, 2026

---

## Test Pyramid

```
                    ▲
                   / \
                  / E2E \          ~10 tests  (10%)
                 / Slow  \         Full user flows
                /---------\
               /Integration \      ~50 tests  (20%)
              / Medium speed \     API + DB operations
             /----------------\
            /   Unit Tests     \   ~200 tests (70%)
           /  Fast · Isolated   \  Individual functions
          /______________________\
```

**Distribution**: 70% Unit · 20% Integration · 10% E2E

---

## Coverage Targets

| Scope | Target |
|-------|--------|
| Overall code coverage | ≥ 80% |
| Auth & service critical paths | ≥ 95% |
| Business logic | ≥ 90% |
| API endpoints | ≥ 85% |
| Utilities / helpers | ≥ 70% |

---

## Part 1 — Unit Testing (Pytest)

Unit tests cover individual functions in isolation. Run them locally before every commit.

### Example: Service matching algorithm

```python
# src/backend/app-python/tests/test_services/test_service_matching.py

import pytest
from app.services.service_matching import ProviderMatcher
from app.models import ServiceRequest, Organization

class TestProviderMatcher:

    def test_distance_score_under_5km(self):
        """Provider < 5 km → 100 points"""
        score = ProviderMatcher().calculate_distance_score(distance_km=3.0)
        assert score == 100

    def test_distance_score_5_to_10km(self):
        """Provider 5–10 km → 80 points"""
        score = ProviderMatcher().calculate_distance_score(distance_km=7.5)
        assert score == 80

    def test_capacity_score_full_capacity(self):
        """Full capacity → 100 points"""
        provider = Organization(capacity=10, available_capacity=10)
        score = ProviderMatcher().calculate_capacity_score(provider)
        assert score == 100

    def test_service_type_exact_match(self):
        """Exact service type match → 100 points"""
        service = ServiceRequest(service_type='MEDICAL')
        provider = Organization(service_types=['MEDICAL', 'RESCUE'])
        score = ProviderMatcher(service=service).calculate_service_type_score(provider)
        assert score == 100

    def test_priority_auto_elevation(self):
        """RESCUE requests are auto-elevated to CRITICAL"""
        from app.services.priority import auto_elevate_priority
        assert auto_elevate_priority('RESCUE', 'MEDIUM') == 'CRITICAL'
        assert auto_elevate_priority('FOOD', 'MEDIUM') == 'MEDIUM'
```

### Run unit tests

```bash
cd src/backend/app-python
conda activate idrm-mvp

# Run all tests with coverage
pytest tests/ -v --cov=app --cov-report=html --cov-report=term

# Run only unit tests (fast)
pytest tests/unit/ -v

# Check coverage threshold
pytest --cov=app --cov-fail-under=80
```

---

## Part 2 — Integration Testing (API Level)

Integration tests exercise full API endpoints against a real test database and Redis instance.

```python
# src/backend/app-python/tests/integration/test_service_flow.py

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

class TestServiceRequestFlow:
    """Full lifecycle: create → approve → accept → complete → verify"""

    @pytest.fixture
    def citizen_token(self):
        r = client.post("/api/v1/auth/login",
                        json={"email": "citizen@test.com", "password": "TestPass123!"})
        return r.json()["data"]["access_token"]

    @pytest.fixture
    def provider_token(self):
        r = client.post("/api/v1/auth/login",
                        json={"email": "provider@test.com", "password": "TestPass123!"})
        return r.json()["data"]["access_token"]

    def test_create_service_request(self, citizen_token):
        r = client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={
                "service_type": "MEDICAL",
                "priority": "CRITICAL",
                "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
                "description": "Elderly patient with chest pain, needs ambulance"
            }
        )
        assert r.status_code == 201
        data = r.json()["data"]
        assert data["status"] == "SUBMITTED"
        return data["service_id"]

    def test_provider_cannot_accept_before_approval(self, provider_token, citizen_token):
        """Status must be APPROVED before accept is allowed"""
        service_id = self.test_create_service_request(citizen_token)
        r = client.post(
            f"/api/v1/services/{service_id}/accept",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={"notes": "On the way"}
        )
        assert r.status_code == 400   # wrong status

    def test_full_lifecycle(self, citizen_token, provider_token, dm_token):
        service_id = self.test_create_service_request(citizen_token)

        # DM approves
        r = client.post(f"/api/v1/services/{service_id}/approve",
                        headers={"Authorization": f"Bearer {dm_token}"},
                        json={"notes": "Verified"})
        assert r.json()["data"]["status"] == "APPROVED"

        # Provider accepts
        r = client.post(f"/api/v1/services/{service_id}/accept",
                        headers={"Authorization": f"Bearer {provider_token}"},
                        json={"estimated_arrival": "2026-05-16T10:30:00Z"})
        assert r.json()["data"]["status"] == "ACCEPTED"
```

### Run integration tests

```bash
# Requires running PostgreSQL + Redis (start with docker-compose up)
pytest tests/integration/ -v
```

---

## Part 3 — End-to-End Testing (Playwright)

E2E tests simulate real user browser interactions across the full stack.

```javascript
// tests/e2e/citizen_journey.spec.js

const { test, expect } = require('@playwright/test');

test.describe('Citizen Emergency Request Journey', () => {

  test('complete emergency request flow', async ({ page }) => {
    await page.goto('http://localhost:5173');

    // Login
    await page.click('text=Login');
    await page.fill('[name=email]', 'citizen@test.com');
    await page.fill('[name=password]', 'TestPass123!');
    await page.click('button:has-text("Sign In")');
    await expect(page.locator('h1')).toContainText('Dashboard');

    // Create request
    await page.click('text=Request Help');
    await page.selectOption('[name=service_type]', 'MEDICAL');
    await page.selectOption('[name=priority]', 'CRITICAL');
    await page.locator('#map').click({ position: { x: 100, y: 100 } });
    await page.fill('[name=description]', 'Elderly man with chest pain, needs ambulance urgently');
    await page.click('button:has-text("Submit Request")');

    // Verify success
    await expect(page.locator('.toast-success')).toBeVisible();
    await expect(page.locator('.toast-success')).toContainText('Request created');

    // Verify it appears in My Requests
    await page.click('text=My Requests');
    await expect(page.locator('.service-request-card')).toHaveCount(1);
  });

});
```

### Run E2E tests

```bash
# Install Playwright (first time only)
npx playwright install

# Run all E2E tests (needs full stack running)
npx playwright test

# Run with browser visible
npx playwright test --headed

# Run specific test file
npx playwright test tests/e2e/citizen_journey.spec.js
```

---

## Part 4 — Performance Testing (Locust)

Load tests verify the system meets response-time SLAs under concurrent traffic.

```python
# tests/performance/locustfile.py

from locust import HttpUser, task, between
import random

class IDRMUser(HttpUser):
    wait_time = between(1, 3)   # 1–3 s between requests

    def on_start(self):
        r = self.client.post("/api/v1/auth/login", json={
            "email": f"user{random.randint(1,1000)}@test.com",
            "password": "TestPass123!"
        })
        self.token = r.json()["data"]["access_token"] if r.status_code == 200 else ""

    @task(5)
    def view_services(self):
        self.client.get("/api/v1/services",
                        headers={"Authorization": f"Bearer {self.token}"})

    @task(3)
    def nearby_search(self):
        self.client.get("/api/v1/geo/nearby?lat=17.3850&lon=78.4867&radius_km=10",
                        headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def create_service(self):
        self.client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "service_type": random.choice(["MEDICAL", "FOOD", "RESCUE"]),
                "priority": "HIGH",
                "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
                "description": "Load test synthetic request — safe to ignore"
            }
        )
```

### Performance targets

| Metric | Target |
|--------|--------|
| p95 API response time | < 500 ms |
| p99 API response time | < 1 000 ms |
| Concurrent users | 1 000 |
| Error rate | < 1% |
| Geo query (nearby) | < 200 ms (with Redis cache) |

```bash
# Start Locust web UI at http://localhost:8089
locust -f tests/performance/locustfile.py --host=http://localhost:3000

# Headless (CI mode): 100 users, 10 spawn/s, run for 60 s
locust -f tests/performance/locustfile.py --host=http://localhost:3000 \
       --users 100 --spawn-rate 10 --run-time 60s --headless
```

---

## Part 5 — Security Testing

```python
# tests/security/test_auth_security.py

class TestAuthenticationSecurity:

    def test_sql_injection_blocked(self):
        """Malicious email input must not cause 500 — only 401"""
        r = client.post("/api/v1/auth/login", json={
            "email": "admin@test.com'; DROP TABLE users; --",
            "password": "password"
        })
        assert r.status_code == 401   # Not 500

    def test_weak_passwords_rejected(self):
        for pwd in ["123456", "password", "abc", "aaaaaaaa"]:
            r = client.post("/api/v1/auth/register", json={
                "email": "test@test.com",
                "password": pwd,
                "full_name": "Test User"
            })
            assert r.status_code == 400

    def test_rate_limiting_on_login(self):
        """11th failed login attempt must return 429"""
        for i in range(11):
            r = client.post("/api/v1/auth/login",
                            json={"email": "x@x.com", "password": "wrong"})
        assert r.status_code == 429

    def test_expired_token_rejected(self):
        from app.core.security import create_access_token
        from datetime import timedelta
        expired = create_access_token(data={"sub": "test"}, expires_delta=timedelta(seconds=-1))
        r = client.get("/api/v1/users/me",
                       headers={"Authorization": f"Bearer {expired}"})
        assert r.status_code == 401

    def test_citizen_cannot_approve_services(self):
        """RBAC: only DM_Authority can approve"""
        r = client.post(
            f"/api/v1/services/{service_id}/approve",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={"notes": "Trying to self-approve"}
        )
        assert r.status_code == 403

    def test_user_cannot_read_private_service_of_another_user(self):
        """PRIVATE services must return 403 for non-requestors"""
        r = client.get(
            f"/api/v1/services/{private_service_id}",
            headers={"Authorization": f"Bearer {other_user_token}"}
        )
        assert r.status_code == 403
```

---

## Part 6 — CI/CD Integration

### When tests run

| Trigger | Tests run |
|---------|-----------|
| `git push` (any branch) | Unit · Integration · Security (basic) |
| Pull request to `main` | All above + E2E (smoke) · Security (full) |
| Merge to `main` | All above + E2E (full suite) · Performance (light) |
| Nightly cron | Full suite + Performance (1 000 users) + DB migration tests |

### GitHub Actions workflow excerpt

```yaml
# .github/workflows/test.yml
jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r src/backend/app-python/requirements.txt
      - run: |
          cd src/backend/app-python
          pytest tests/unit/ -v --cov=app --cov-report=xml --cov-fail-under=80
      - uses: codecov/codecov-action@v3

  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env: { POSTGRES_PASSWORD: postgres }
      redis:
        image: redis:7.2-alpine
    steps:
      - uses: actions/checkout@v4
      - run: pytest src/backend/app-python/tests/integration/ -v

  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npx playwright install --with-deps
      - run: npx playwright test --reporter=html
```

---

## Part 7 — Quality Gates

All of these must pass before a PR can merge to `main`:

```yaml
Quality Gate:
  code_coverage:
    overall:        ≥ 80%
    critical_paths: ≥ 95%

  api_response_time:
    p95: < 500 ms
    p99: < 1 000 ms

  error_rate:
    max: 1%

  security:
    - No high/critical vulnerabilities (Bandit + Trivy)
    - All auth security tests pass
    - OWASP Top 10 coverage

  static_analysis:
    - Ruff (Python linter) passes with 0 errors
    - TypeScript compiler (tsc) passes with 0 errors
```

---

## Quick Commands Reference

```bash
# Unit tests
pytest src/backend/app-python/tests/unit/ -v

# Integration tests (needs DB + Redis)
pytest src/backend/app-python/tests/integration/ -v

# Security tests
pytest src/backend/app-python/tests/security/ -v

# E2E tests (needs full stack)
npx playwright test

# Performance tests
locust -f tests/performance/locustfile.py --host=http://localhost:3000

# All tests + coverage
pytest src/backend/app-python/tests/ --cov=app --cov-report=html

# View HTML coverage report
open src/backend/app-python/htmlcov/index.html
```

---

**See also**:
- `backup/TESTING-STRATEGY-v3.md` — Full testing strategy with complete code examples
- `backup/42-VERIFICATION-CHECKLISTS.md` — Manual testing checklists and pre-deployment verification
- `docs/IDRM-Mock-Data-Guide.md` — How to seed test data before running tests
