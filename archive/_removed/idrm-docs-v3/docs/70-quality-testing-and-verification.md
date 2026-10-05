# IDRM v3 · Testing Strategy & Verification

<!-- IDRM-CLEANUP doc=v3-70-testing status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — testing → `docs/mvp/70`
> → [`../../../../docs/mvp/70-quality-test-strategy.md`](../../../../docs/mvp/70-quality-test-strategy.md) (unit/API/
> integration via pytest, F1–F11 → tests, ≥80%) + guides `testing-101`, `api-testing-101`. Conformance `PICS-INC-012`.
> E2E/perf/chaos/DAST → FFP `docs/ffp/70`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Document (specification) · Audience: QA, developers · Status: Archived — v3 historical generation*
*Consolidated from: TESTING-STRATEGY-v3.md, 42-VERIFICATION-CHECKLISTS.md*

## Contents
- [IDRM: Testing Strategy - Version 3](#idrm-testing-strategy---version-3)
- [IDRM: Verification & Testing Checklists](#idrm-verification--testing-checklists)

---

## IDRM: Testing Strategy - Version 3

### Complete Testing Framework & Quality Assurance Plan

**Document Version**: 3.0  
**Date**: May 24, 2026  
**Status**: ✅ Production-Ready  
**Coverage Target**: 80% overall, 95% for critical paths  
**Target Audience**: QA engineers, developers, test automation engineers

---

### 📚 **Table of Contents**

1. [Testing Overview](#1-testing-overview)
2. [Test Pyramid](#2-test-pyramid)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [End-to-End Testing](#5-end-to-end-testing)
6. [Performance Testing](#6-performance-testing)
7. [Security Testing](#7-security-testing)
8. [Test Automation](#8-test-automation)
9. [CI/CD Integration](#9-cicd-integration)
10. [Quality Metrics](#10-quality-metrics)

---

## 1. **Testing Overview**

### 1.1 Testing Philosophy

```
PRINCIPLES:
├─ Test early, test often
├─ Automate everything possible
├─ Fast feedback loops
├─ Test in production-like environments
└─ Shift-left testing (catch bugs early)

COVERAGE TARGETS:
├─ Overall code coverage: 80%
├─ Critical paths (auth, services): 95%
├─ Business logic: 90%
├─ API endpoints: 85%
└─ Utilities: 70%

TEST ENVIRONMENTS:
├─ Local (developer machine)
├─ CI (GitHub Actions)
├─ Staging (pre-production)
└─ Production (smoke tests only)
```

---

## 2. **Test Pyramid**

```
                    ▲
                   ╱ ╲
                  ╱   ╲
                 ╱ E2E ╲        ~10 tests
                ╱ (Slow)╲       (10% of tests)
               ╱─────────╲
              ╱           ╲
             ╱Integration ╲     ~50 tests
            ╱   (Medium)   ╲    (20% of tests)
           ╱───────────────╲
          ╱                 ╱
         ╱   Unit Tests     ╱   ~200 tests
        ╱     (Fast)        ╱    (70% of tests)
       ╱───────────────────╱
      ▼                     ▼

DISTRIBUTION:
├─ 70% Unit Tests (fast, isolated, many)
├─ 20% Integration Tests (medium speed, API level)
└─ 10% E2E Tests (slow, full user flows)
```

---

## 3. **Unit Testing**

### 3.1 Backend Unit Tests (Python/Pytest)

```python
## backend/tests/test_services/test_service_matching.py

import pytest
from app.services.service_matching import ProviderMatcher
from app.models import ServiceRequest, Organization

class TestProviderMatcher:
    """Test provider matching algorithm"""
    
    def test_distance_score_under_5km(self):
        """Provider < 5km should get 100 points"""
        matcher = ProviderMatcher()
        score = matcher.calculate_distance_score(distance_km=3.0)
        assert score == 100
    
    def test_distance_score_5_to_10km(self):
        """Provider 5-10km should get 80 points"""
        matcher = ProviderMatcher()
        score = matcher.calculate_distance_score(distance_km=7.5)
        assert score == 80
    
    def test_capacity_score_full_capacity(self):
        """Provider with full capacity should get 100 points"""
        matcher = ProviderMatcher()
        provider = Organization(capacity=10, available_capacity=10)
        score = matcher.calculate_capacity_score(provider)
        assert score == 100
    
    def test_service_type_exact_match(self):
        """Exact service type match should get 100 points"""
        service = ServiceRequest(service_type='MEDICAL')
        provider = Organization(service_types=['MEDICAL', 'RESCUE'])
        matcher = ProviderMatcher(service=service)
        score = matcher.calculate_service_type_score(provider)
        assert score == 100

## Run: pytest backend/tests/ -v --cov=app --cov-report=html
```

---

### 3.2 Test Coverage Report

```bash
## Generate coverage report
pytest --cov=app --cov-report=html --cov-report=term

## Output example:
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
app/__init__.py                            2      0   100%
app/main.py                               45      3    93%
app/api/v1/auth.py                        89      8    91%
app/api/v1/services.py                   145     15    90%
app/services/service_matching.py          67      4    94%
app/crud/service.py                       92     10    89%
-----------------------------------------------------------
TOTAL                                   1543    123    80%

## HTML report at: htmlcov/index.html
```

---

## 4. **Integration Testing**

### 4.1 API Integration Tests

```python
## tests/integration/test_service_flow.py

from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

class TestServiceRequestFlow:
    """Test complete service request lifecycle"""
    
    @pytest.fixture
    def citizen_token(self):
        """Login as citizen and get token"""
        response = client.post("/api/v1/auth/login", json={
            "email": "citizen@test.com",
            "password": "TestPass123"
        })
        return response.json()["data"]["access_token"]
    
    @pytest.fixture
    def provider_token(self):
        """Login as provider and get token"""
        response = client.post("/api/v1/auth/login", json={
            "email": "provider@test.com",
            "password": "TestPass123"
        })
        return response.json()["data"]["access_token"]
    
    def test_create_service_request(self, citizen_token):
        """Test: Citizen creates service request"""
        response = client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {citizen_token}"},
            json={
                "service_type": "MEDICAL",
                "priority": "CRITICAL",
                "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
                "description": "Test emergency medical request"
            }
        )
        
        assert response.status_code == 201
        data = response.json()["data"]
        assert data["service_type"] == "MEDICAL"
        assert data["priority"] == "CRITICAL"
        assert data["status"] == "SUBMITTED"
        return data["service_id"]
    
    def test_accept_service(self, provider_token):
        """Test: Provider accepts service"""
        # First create a service
        service_id = self.test_create_service_request(citizen_token)
        
        # Provider accepts
        response = client.post(
            f"/api/v1/services/{service_id}/accept",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={"notes": "Ambulance dispatched"}
        )
        
        assert response.status_code == 200
        assert response.json()["data"]["status"] == "ACCEPTED"

## Run: pytest tests/integration/ -v
```

---

## 5. **End-to-End Testing**

### 5.1 E2E Test Framework (Playwright)

```javascript
// tests/e2e/citizen_journey.spec.js

const { test, expect } = require('@playwright/test');

test.describe('Citizen Emergency Request Journey', () => {
  
  test('complete emergency request flow', async ({ page }) => {
    // 1. Navigate to homepage
    await page.goto('http://localhost:3000');
    await expect(page).toHaveTitle(/IDRM/);
    
    // 2. Login
    await page.click('text=Login');
    await page.fill('[name=email]', 'citizen@test.com');
    await page.fill('[name=password]', 'TestPass123');
    await page.click('button:has-text("Login")');
    
    // 3. Wait for dashboard
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // 4. Create service request
    await page.click('text=Create Request');
    
    // 5. Fill form
    await page.selectOption('[name=service_type]', 'MEDICAL');
    await page.selectOption('[name=priority]', 'CRITICAL');
    
    // 6. Click map to set location (simulate)
    const map = await page.locator('#map');
    await map.click({ position: { x: 100, y: 100 } });
    
    // 7. Enter description
    await page.fill('[name=description]', 'Elderly man with chest pain, need ambulance urgently');
    
    // 8. Submit
    await page.click('button:has-text("Submit Request")');
    
    // 9. Verify success message
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Request created successfully');
    
    // 10. Verify request appears in list
    await page.click('text=My Requests');
    await expect(page.locator('.service-request')).toHaveCount(1);
  });
  
});

// Run: npx playwright test
```

---

## 6. **Performance Testing**

### 6.1 Load Testing (Locust)

```python
## tests/performance/locustfile.py

from locust import HttpUser, task, between
import random

class IDRMUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": f"user{random.randint(1, 1000)}@test.com",
            "password": "TestPass123"
        })
        if response.status_code == 200:
            self.token = response.json()["data"]["access_token"]
    
    @task(5)  # 5x more frequent
    def view_services(self):
        """View service list"""
        self.client.get(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def view_service_detail(self):
        """View single service"""
        service_id = "550e8400-e29b-41d4-a716-446655440000"
        self.client.get(
            f"/api/v1/services/{service_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def create_service(self):
        """Create service request"""
        self.client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "service_type": random.choice(["MEDICAL", "RESCUE", "FOOD"]),
                "priority": "HIGH",
                "location": {
                    "type": "Point",
                    "coordinates": [78.48, 17.38]
                },
                "description": "Load test request"
            }
        )

## Run: locust -f tests/performance/locustfile.py --host=http://localhost:3000
## Target: 1000 concurrent users, p95 response time < 500ms
```

---

## 7. **Security Testing**

### 7.1 Security Test Suite

```python
## tests/security/test_auth_security.py

class TestAuthenticationSecurity:
    
    def test_sql_injection_prevention(self):
        """Test SQL injection is blocked"""
        malicious_email = "admin@test.com'; DROP TABLE users; --"
        response = client.post("/api/v1/auth/login", json={
            "email": malicious_email,
            "password": "password"
        })
        # Should return 401, not 500 (SQL error)
        assert response.status_code == 401
    
    def test_password_strength_validation(self):
        """Test weak passwords are rejected"""
        weak_passwords = ["123456", "password", "abc", "aaaaaaaa"]
        
        for pwd in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@test.com",
                "password": pwd,
                "full_name": "Test User"
            })
            assert response.status_code == 400
    
    def test_rate_limiting(self):
        """Test rate limiting works"""
        # Try 11 logins (limit is 10/hour)
        for i in range(11):
            response = client.post("/api/v1/auth/login", json={
                "email": "test@test.com",
                "password": "wrong"
            })
            
            if i < 10:
                assert response.status_code in [401, 400]
            else:
                # 11th should be rate limited
                assert response.status_code == 429
    
    def test_jwt_expiration(self):
        """Test expired tokens are rejected"""
        # Create expired token
        from app.core.security import create_access_token
        from datetime import timedelta
        
        expired_token = create_access_token(
            data={"sub": "test-user"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
```

---

## 8. **Test Automation**

### 8.1 Test Execution Matrix

```yaml
## tests/test-matrix.yml
## Defines what tests run when

on_push:
  - unit_tests (fast)
  - integration_tests (API only)
  - security_tests (basic)

on_pull_request:
  - unit_tests
  - integration_tests
  - e2e_tests (smoke tests)
  - security_tests (full)

on_merge_to_main:
  - unit_tests
  - integration_tests
  - e2e_tests (full suite)
  - performance_tests (light load)
  - security_tests (full + OWASP ZAP)

nightly:
  - all_tests
  - performance_tests (full load: 1000 users)
  - database_migration_tests
  - backup_restore_tests
```

---

## 9. **CI/CD Integration**

### 9.1 GitHub Actions Workflow

```yaml
## .github/workflows/test.yml

name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install -r backend/requirements-dev.txt
      
      - name: Run unit tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml --cov-fail-under=80
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  integration-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7.2-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Run integration tests
        run: |
          pytest tests/integration/ -v
  
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install Playwright
        run: npx playwright install
      
      - name: Run E2E tests
        run: npx playwright test
```

---

## 10. **Quality Metrics**

### 10.1 Quality Gates

```yaml
## Define quality gates that must pass

CODE_COVERAGE:
  minimum: 80%
  critical_paths: 95%
  
API_RESPONSE_TIME:
  p95: < 500ms
  p99: < 1000ms
  
ERROR_RATE:
  maximum: 1%
  
SECURITY:
  - No high/critical vulnerabilities
  - All security tests pass
  - OWASP Top 10 coverage
  
CODE_QUALITY:
  - No code smells (SonarQube)
  - Complexity score < 10
  - Maintainability rating: A
```

---

### 10.2 Test Reporting

```bash
## Generate comprehensive test report

## Coverage report
pytest --cov=app --cov-report=html --cov-report=term

## Performance report (from Locust)
locust -f locustfile.py --headless -u 1000 -r 100 -t 5m --html=report.html

## Security report (OWASP ZAP)
zap-cli quick-scan --self-contained --start-options '-config api.disablekey=true' http://localhost:3000

## Combine all reports
python scripts/generate_test_report.py --output=test-report.html
```

---

## 11. **Accessibility Testing**

### 11.1 Accessibility Standards

**Target Compliance**: WCAG 2.1 Level AA

```yaml
Why Accessibility Matters:
  - Government service must be accessible to all citizens
  - Legal requirement under Indian disability laws
  - Ethical obligation to inclusive design
  - Better UX for everyone (not just disabled users)

Standards:
  WCAG 2.1 Level AA:
    - Perceivable: Content visible/audible to all
    - Operable: Interface usable by all
    - Understandable: Content and operations clear
    - Robust: Works with assistive technologies

Key Requirements:
  ✓ Keyboard navigation (no mouse required)
  ✓ Screen reader compatible
  ✓ Sufficient color contrast (4.5:1 for text)
  ✓ Text alternatives for images
  ✓ Form labels and error messages
  ✓ Focus indicators visible
  ✓ Skip navigation links
  ✓ Responsive text sizing
```

---

### 11.2 Automated Accessibility Testing

#### **Tool: axe-core**

```javascript
// tests/accessibility/axe.test.js
const { AxePuppeteer } = require('@axe-core/puppeteer');
const puppeteer = require('puppeteer');

describe('Accessibility Tests', () => {
  let browser;
  let page;

  beforeAll(async () => {
    browser = await puppeteer.launch();
    page = await browser.newPage();
  });

  afterAll(async () => {
    await browser.close();
  });

  test('Homepage has no accessibility violations', async () => {
    await page.goto('http://localhost:3000');
    
    const results = await new AxePuppeteer(page)
      .analyze();
    
    expect(results.violations).toHaveLength(0);
  });

  test('Service request form is accessible', async () => {
    await page.goto('http://localhost:3000/request-service');
    
    const results = await new AxePuppeteer(page)
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    
    // Log any violations
    if (results.violations.length > 0) {
      console.log('Accessibility violations:');
      results.violations.forEach(violation => {
        console.log(`- ${violation.id}: ${violation.description}`);
        console.log(`  Impact: ${violation.impact}`);
        console.log(`  Elements: ${violation.nodes.length}`);
      });
    }
    
    expect(results.violations).toHaveLength(0);
  });

  test('Map interface is keyboard accessible', async () => {
    await page.goto('http://localhost:3000');
    
    // Test keyboard navigation
    await page.keyboard.press('Tab'); // Should focus first interactive element
    const focusedElement = await page.evaluate(() => document.activeElement.tagName);
    expect(focusedElement).toBeTruthy();
    
    const results = await new AxePuppeteer(page).analyze();
    expect(results.violations).toHaveLength(0);
  });
});

// Run: npm run test:a11y
```

---

### 11.3 Manual Accessibility Testing

#### **Keyboard Navigation Tests**

```yaml
Test 1: Tab Navigation
  Steps:
    1. Load homepage
    2. Press Tab repeatedly
    3. Verify all interactive elements receive focus
    4. Verify focus indicator is visible
    5. Verify tab order is logical
  
  Expected:
    ✓ Can reach all buttons, links, form fields
    ✓ Focus ring clearly visible (2px solid)
    ✓ Order follows visual layout
    ✓ No focus traps

Test 2: Skip Navigation
  Steps:
    1. Load any page
    2. Press Tab once
    3. Verify "Skip to main content" link appears
    4. Press Enter
    5. Verify focus moves to main content
  
  Expected:
    ✓ Skip link visible on Tab
    ✓ Link functional
    ✓ Focus moves correctly

Test 3: Form Interaction
  Steps:
    1. Navigate to service request form
    2. Use only Tab, Enter, Space, Arrow keys
    3. Complete entire form
    4. Submit form
  
  Expected:
    ✓ All fields reachable
    ✓ Dropdowns open with Enter/Space
    ✓ Radio buttons toggle with Space
    ✓ Submit works with Enter
```

---

### 11.4 Screen Reader Testing

#### **Tools: NVDA (Windows), JAWS (Windows), VoiceOver (Mac)**

```yaml
Test Scenario 1: Homepage Navigation
  Tool: NVDA
  Steps:
    1. Open homepage with NVDA active
    2. Navigate using H key (headings)
    3. Navigate using D key (landmarks)
    4. Listen to page structure
  
  Expected Announcements:
    ✓ "IDRM - Disaster Response Management"
    ✓ "Main navigation landmark"
    ✓ "Heading level 1: Create Service Request"
    ✓ "Main landmark"
    ✓ All images have alt text

Test Scenario 2: Form Completion
  Tool: NVDA
  Steps:
    1. Navigate to service request form
    2. Tab through form fields
    3. Listen to field labels and instructions
    4. Enter data
    5. Submit form
  
  Expected Announcements:
    ✓ "Service Type, combo box"
    ✓ "Priority, required, combo box"
    ✓ "Description, required, edit"
    ✓ "Error: Description must be at least 10 characters"
    ✓ "Success: Service request submitted"

Test Scenario 3: Map Interaction
  Tool: NVDA
  Steps:
    1. Navigate to map view
    2. Listen to map description
    3. Access service markers
  
  Expected:
    ✓ "Interactive map showing service requests"
    ✓ "50 service requests in this area"
    ✓ Alternative list view available
    ✓ Marker details accessible via keyboard
```

---

### 11.5 Color Contrast Testing

#### **Tool: Chrome DevTools + axe DevTools**

```yaml
Test: Verify All Text Meets Contrast Ratios

Requirements:
  Normal Text (< 18pt): 4.5:1 contrast ratio
  Large Text (≥ 18pt): 3:1 contrast ratio
  UI Components: 3:1 contrast ratio

Test Process:
  1. Open Chrome DevTools
  2. Install axe DevTools extension
  3. Run "Scan page for accessibility issues"
  4. Check "Color contrast" results
  
  OR manual:
  1. Right-click any text
  2. Inspect
  3. Check "Contrast ratio" in DevTools
  4. Verify green checkmarks (AA, AAA)

Common Issues to Check:
  ✓ Light gray text on white background
  ✓ Button text colors
  ✓ Placeholder text (often too light)
  ✓ Disabled form fields
  ✓ Link colors
  ✓ Focus indicators

Fix Example:
  Before: color: #999999 on #FFFFFF (2.85:1) ❌
  After:  color: #767676 on #FFFFFF (4.54:1) ✅
```

---

### 11.6 Mobile Accessibility

```yaml
Test 1: Touch Target Size
  Requirement: Minimum 44x44 pixels
  
  Test:
    1. Open mobile view (375px width)
    2. Measure button sizes
    3. Verify all interactive elements ≥ 44px
  
  Tools:
    - Chrome DevTools device emulation
    - Measure tool in DevTools
  
  Expected:
    ✓ All buttons ≥ 44x44px
    ✓ Adequate spacing between targets
    ✓ Form fields large enough

Test 2: Zoom and Reflow
  Requirement: Content readable at 200% zoom
  
  Test:
    1. Set browser zoom to 200%
    2. Verify no horizontal scrolling
    3. Verify all content accessible
    4. Check text doesn't overflow
  
  Expected:
    ✓ Layout adapts to zoom
    ✓ Text reflows properly
    ✓ No content cutoff
```

---

### 11.7 Accessibility Test Checklist

```yaml
Pre-Release Checklist:

[ ] Automated Testing:
  [ ] axe-core tests pass (0 violations)
  [ ] Lighthouse accessibility score ≥ 90
  [ ] WAVE tool shows no errors

[ ] Keyboard Testing:
  [ ] All features accessible via keyboard
  [ ] Focus indicators visible throughout
  [ ] No keyboard traps
  [ ] Skip navigation works
  [ ] Tab order logical

[ ] Screen Reader Testing:
  [ ] Tested with NVDA (Windows)
  [ ] Tested with JAWS (Windows) - if available
  [ ] Tested with VoiceOver (Mac)
  [ ] All images have alt text
  [ ] Form labels announced correctly
  [ ] Error messages announced
  [ ] Success messages announced

[ ] Visual Testing:
  [ ] Color contrast ≥ 4.5:1 for text
  [ ] Color contrast ≥ 3:1 for UI components
  [ ] Content readable without color
  [ ] Focus indicators clearly visible

[ ] Mobile Testing:
  [ ] Touch targets ≥ 44x44 pixels
  [ ] Readable at 200% zoom
  [ ] No horizontal scrolling when zoomed
  [ ] VoiceOver tested on iOS

[ ] Forms:
  [ ] All fields have visible labels
  [ ] Required fields marked
  [ ] Error messages descriptive
  [ ] Error messages associated with fields
  [ ] Success confirmations clear

[ ] Documentation:
  [ ] Accessibility statement on website
  [ ] Contact for accessibility issues
  [ ] Known limitations documented
  [ ] Keyboard shortcuts documented
```

---

### 11.8 Accessibility CI/CD Integration

```yaml
## .github/workflows/accessibility.yml
name: Accessibility Tests

on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install dependencies
        run: npm install
      
      - name: Start application
        run: npm run dev &
        
      - name: Wait for app
        run: npx wait-on http://localhost:3000
      
      - name: Run axe tests
        run: npm run test:a11y
      
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun --collect.url=http://localhost:3000 \
            --assert.preset=lighthouse:accessibility
      
      - name: Upload accessibility report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: accessibility-report
          path: ./accessibility-report.html
```

---

### 11.9 Accessibility Metrics

```yaml
Key Metrics to Track:

Metric 1: Automated Test Pass Rate
  Target: 100% (0 axe violations)
  Measured: Every build
  Tool: axe-core

Metric 2: Lighthouse Accessibility Score
  Target: ≥ 90
  Measured: Every build
  Tool: Google Lighthouse

Metric 3: Manual Test Coverage
  Target: 100% of user flows
  Measured: Before each release
  Method: Manual testing checklist

Metric 4: Screen Reader Compatibility
  Target: Full compatibility (NVDA, JAWS, VoiceOver)
  Measured: Before each release
  Method: Manual testing

Metric 5: Keyboard Navigation
  Target: 100% of features accessible
  Measured: Before each release
  Method: Manual testing

Reporting:
  - Weekly: Automated metrics in CI/CD
  - Sprint End: Manual test results
  - Release: Full accessibility audit
```

---

**END OF TESTING-STRATEGY-v3.md**

**Total Pages**: ~35 pages (expanded)  
**Completeness**: 100% ✅  
**Status**: ✅ Production-ready testing strategy  
**Accessibility**: ✅ WCAG 2.1 AA compliant testing included

---

## IDRM: Verification & Testing Checklists

### Complete Guide to Quality Assurance

**Version**: 3.0 Consolidated  
**Audience**: Developers, QA Engineers, & Complete Beginners  
**Reading Time**: 55-70 minutes  
**Last Updated**: May 16, 2026

---

### 📚 **Table of Contents**

1. [What is Verification & Testing?](#1-what-is-verification--testing)
2. [Testing Strategy Overview](#2-testing-strategy-overview)
3. [Unit Testing](#3-unit-testing)
4. [Integration Testing](#4-integration-testing)
5. [End-to-End Testing](#5-end-to-end-testing)
6. [API Testing](#6-api-testing)
7. [Database Testing](#7-database-testing)
8. [Frontend Testing](#8-frontend-testing)
9. [Security Testing](#9-security-testing)
10. [Performance Testing](#10-performance-testing)
11. [Manual Testing Checklists](#11-manual-testing-checklists)
12. [Pre-Deployment Verification](#12-pre-deployment-verification)

---

### 1. **What is Verification & Testing?**

#### 1.1 The Simple Explanation

**Testing** = Making sure your code actually works!

Think of it like **proofreading an essay**:
- **Before submitting**: You check for typos, grammar mistakes, and logic errors
- **After submitting**: Teacher checks if it meets requirements
- **In production**: Everyone reads it and finds issues you missed!

**Software testing does the same thing** - catch problems BEFORE users find them!

#### 1.2 Real-World Analogy

**Building a House**:

```
WITHOUT Testing:
Build house → Move in → Discover leaky roof! 😱

WITH Testing:
1. Test foundation (Unit tests)
2. Test plumbing (Integration tests)
3. Test full house (E2E tests)
4. Stress test (Performance tests)
5. Move in safely! ✅
```

#### 1.3 Why Testing Matters for IDRM

**IDRM saves lives** - bugs can be deadly:
- ❌ Authentication bug → Unauthorized access to victim locations
- ❌ Geospatial bug → Ambulance goes to wrong location
- ❌ Status bug → Completed service marked as pending
- ❌ Performance bug → Map crashes during disaster

**Testing ensures reliability when it matters most!**

---

### 2. **Testing Strategy Overview**

#### 2.1 The Testing Pyramid

```
           /\
          /  \           E2E Tests (Few, Slow, Expensive)
         / E2E \         ├─ Full user workflows
        /______\         └─ All systems integrated
       /        \
      /  INTEG-  \       Integration Tests (Some, Medium)
     /   RATION   \      ├─ API endpoints
    /______________\     └─ Database operations
   /                \
  /   UNIT  TESTS    \   Unit Tests (Many, Fast, Cheap)
 /____________________\  ├─ Individual functions
                         └─ Business logic

GOAL: Most tests at bottom (fast), few at top (slow)
```

#### 2.2 Test Types & Coverage Targets

| Test Type | What It Tests | Coverage Target | Speed |
|-----------|---------------|-----------------|-------|
| **Unit** | Single functions | 80%+ | ⚡️ Milliseconds |
| **Integration** | API endpoints | 75%+ | 🚀 Seconds |
| **E2E** | Complete workflows | 60%+ | 🐢 Minutes |
| **Manual** | UX, edge cases | 100% critical paths | 🚶 Hours |

#### 2.3 Testing Timeline

```
┌──────────────────────────────────────┐
│  DEVELOPMENT CYCLE                   │
├──────────────────────────────────────┤
│  Write Code                          │
│  ↓                                   │
│  Write Unit Tests                    │
│  ↓                                   │
│  Run Unit Tests Locally              │
│  ↓                                   │
│  Commit & Push                       │
│  ↓                                   │
│  CI/CD: Run All Tests                │
│  ↓                                   │
│  Code Review                         │
│  ↓                                   │
│  Merge to Main                       │
│  ↓                                   │
│  Deploy to Staging                   │
│  ↓                                   │
│  Run Integration & E2E Tests         │
│  ↓                                   │
│  Manual QA Testing                   │
│  ↓                                   │
│  Deploy to Production                │
│  ↓                                   │
│  Monitor & Validate                  │
└──────────────────────────────────────┘
```

---

### 3. **Unit Testing**

#### 3.1 What Are Unit Tests?

**Definition**: Tests for the **smallest piece** of code (one function).

**Example**: Testing a calculator

```python
def add(a, b):
    """Add two numbers."""
    return a + b

## Unit test
def test_add():
    """Test the add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0
```

#### 3.2 Python Unit Tests (pytest)

**Setup**:
```bash
pip install pytest pytest-asyncio pytest-cov
```

**File Structure**:
```
backend/
├── app/
│   └── services/
│       └── service_manager.py
└── tests/
    └── unit/
        └── test_service_manager.py
```

**Example Test File**:
```python
import pytest
from uuid import uuid4
from app.services.service_manager import ServiceManager
from app.models import ServiceRequest

class TestServiceManager:
    """Test suite for ServiceManager."""
    
    @pytest.mark.asyncio
    async def test_create_service_success(self, db_session):
        """Test successful service creation."""
        # Arrange (Setup)
        service_data = {
            "service_type": "MEDICAL",
            "priority": "CRITICAL",
            "location": {"type": "Point", "coordinates": [78.48, 17.38]},
            "address": "Test Address",
            "description": "Test description"
        }
        
        # Act (Execute)
        service = await ServiceManager.create_service(db_session, service_data)
        
        # Assert (Verify)
        assert service.service_id is not None
        assert service.service_type == "MEDICAL"
        assert service.priority == "CRITICAL"
        assert service.status == "SUBMITTED"
        assert service.created_at is not None
    
    @pytest.mark.asyncio
    async def test_create_service_invalid_type(self, db_session):
        """Test service creation with invalid service type."""
        service_data = {
            "service_type": "INVALID_TYPE",  # ← Bad input
            "priority": "CRITICAL",
            "location": {"type": "Point", "coordinates": [78.48, 17.38]},
            "description": "Test"
        }
        
        # Should raise ValidationError
        with pytest.raises(ValidationError) as exc_info:
            await ServiceManager.create_service(db_session, service_data)
        
        assert "Invalid service type" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_find_nearby_services(self, db_session):
        """Test finding services near a location."""
        # Arrange: Create test services
        location1 = {"type": "Point", "coordinates": [78.48, 17.38]}
        location2 = {"type": "Point", "coordinates": [78.49, 17.39]}
        
        service1 = await create_test_service(db_session, location1)
        service2 = await create_test_service(db_session, location2)
        
        # Act: Search near location1
        search_location = {"type": "Point", "coordinates": [78.48, 17.38]}
        nearby = await ServiceManager.find_nearby(
            db_session,
            search_location,
            radius=5000  # 5km radius
        )
        
        # Assert
        assert len(nearby) >= 1
        assert service1.service_id in [s.service_id for s in nearby]
```

**Running Tests**:
```bash
## Run all tests
pytest

## Run with coverage
pytest --cov=app --cov-report=html

## Run specific test file
pytest tests/unit/test_service_manager.py

## Run specific test
pytest tests/unit/test_service_manager.py::TestServiceManager::test_create_service_success

## Run with verbose output
pytest -v

## Run and show print statements
pytest -s
```

---

#### 3.3 JavaScript Unit Tests (Jest/Vitest)

**For Node.js/Bun**:

**Setup**:
```bash
bun add -d vitest @vitest/ui
```

**Example Test**:
```javascript
import { describe, it, expect } from 'vitest';
import { validateServiceRequest } from '../utils/validation';

describe('validateServiceRequest', () => {
    it('should accept valid service request', () => {
        const validRequest = {
            service_type: 'MEDICAL',
            priority: 'CRITICAL',
            location: { type: 'Point', coordinates: [78.48, 17.38] },
            address: 'Test Address',
            description: 'Test description'
        };
        
        const result = validateServiceRequest(validRequest);
        expect(result.isValid).toBe(true);
        expect(result.errors).toHaveLength(0);
    });
    
    it('should reject invalid service type', () => {
        const invalidRequest = {
            service_type: 'INVALID',
            priority: 'CRITICAL',
            location: { type: 'Point', coordinates: [78.48, 17.38] },
            description: 'Test'
        };
        
        const result = validateServiceRequest(invalidRequest);
        expect(result.isValid).toBe(false);
        expect(result.errors).toContain('Invalid service type');
    });
    
    it('should reject missing required fields', () => {
        const incompleteRequest = {
            service_type: 'MEDICAL',
            priority: 'CRITICAL'
            // Missing location and description
        };
        
        const result = validateServiceRequest(incompleteRequest);
        expect(result.isValid).toBe(false);
        expect(result.errors.length).toBeGreaterThan(0);
    });
});
```

**Running Tests**:
```bash
## Run all tests
bun test

## Run with UI
bun test --ui

## Run with coverage
bun test --coverage

## Watch mode (re-run on file changes)
bun test --watch
```

---

#### 3.4 Unit Test Checklist

**Before Writing Tests**:
- [ ] Understand what the function does
- [ ] Identify inputs and expected outputs
- [ ] Think about edge cases

**Test Coverage**:
- [ ] **Happy path**: Normal, expected input
- [ ] **Edge cases**: Boundary values, empty inputs, null values
- [ ] **Error cases**: Invalid inputs, exceptions
- [ ] **Business logic**: All conditions and branches

**Example - Comprehensive Test Coverage**:
```python
@pytest.mark.asyncio
async def test_calculate_distance():
    """Test distance calculation function."""
    
    # Happy path - Normal case
    distance = calculate_distance(
        (0.0, 0.0),
        (3.0, 4.0)
    )
    assert distance == 5.0  # 3-4-5 triangle
    
    # Edge case - Same point
    distance = calculate_distance(
        (1.0, 1.0),
        (1.0, 1.0)
    )
    assert distance == 0.0
    
    # Edge case - Negative coordinates
    distance = calculate_distance(
        (-1.0, -1.0),
        (1.0, 1.0)
    )
    assert distance > 0
    
    # Error case - Invalid input type
    with pytest.raises(TypeError):
        calculate_distance("invalid", (1.0, 1.0))
    
    # Error case - Wrong number of coordinates
    with pytest.raises(ValueError):
        calculate_distance((1.0,), (1.0, 1.0))
```

---

### 4. **Integration Testing**

#### 4.1 What Are Integration Tests?

**Definition**: Tests that check how **multiple components work together**.

**Examples**:
- API endpoint → Database
- Frontend → Backend API
- Service A → Service B

#### 4.2 API Integration Tests

**Example - Testing Complete Auth Flow**:

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_auth_workflow(client: AsyncClient):
    """Test complete authentication workflow."""
    
    # 1. Register new user
    register_response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User",
            "phone": "9876543210",
            "role": "CITIZEN"
        }
    )
    
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["status"] == "success"
    assert "user_id" in data["data"]
    user_id = data["data"]["user_id"]
    
    # 2. Login with registered credentials
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
    )
    
    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data["data"]
    assert "refresh_token" in data["data"]
    access_token = data["data"]["access_token"]
    refresh_token = data["data"]["refresh_token"]
    
    # 3. Access protected endpoint with token
    profile_response = await client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    assert profile_response.status_code == 200
    profile = profile_response.json()["data"]
    assert profile["email"] == "newuser@example.com"
    
    # 4. Refresh token
    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    
    assert refresh_response.status_code == 200
    new_tokens = refresh_response.json()["data"]
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != access_token  # Should be different
```

---

#### 4.3 Database Integration Tests

**Example - Testing Service CRUD**:

```python
@pytest.mark.asyncio
async def test_service_crud_operations(db_session):
    """Test complete CRUD operations for services."""
    
    # CREATE
    service_data = {
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "location": {"type": "Point", "coordinates": [78.48, 17.38]},
        "address": "Test Address",
        "description": "Test description"
    }
    
    service = ServiceRequest(**service_data)
    db_session.add(service)
    await db_session.commit()
    await db_session.refresh(service)
    
    service_id = service.service_id
    assert service_id is not None
    
    # READ
    result = await db_session.execute(
        select(ServiceRequest).where(ServiceRequest.service_id == service_id)
    )
    fetched_service = result.scalar_one()
    assert fetched_service.service_type == "MEDICAL"
    
    # UPDATE
    fetched_service.status = "APPROVED"
    await db_session.commit()
    await db_session.refresh(fetched_service)
    assert fetched_service.status == "APPROVED"
    
    # DELETE
    await db_session.delete(fetched_service)
    await db_session.commit()
    
    # Verify deletion
    result = await db_session.execute(
        select(ServiceRequest).where(ServiceRequest.service_id == service_id)
    )
    deleted_service = result.scalar_one_or_none()
    assert deleted_service is None
```

---

#### 4.4 Integration Test Checklist

**API Integration Tests**:
- [ ] Test all HTTP methods (GET, POST, PUT, DELETE)
- [ ] Test request/response formats
- [ ] Test authentication & authorization
- [ ] Test error responses (400, 401, 403, 404, 500)
- [ ] Test edge cases (empty body, invalid JSON)

**Database Integration Tests**:
- [ ] Test CRUD operations
- [ ] Test transactions & rollbacks
- [ ] Test constraints (unique, foreign key)
- [ ] Test queries (filters, sorting, pagination)
- [ ] Test relationships (joins, cascades)

---

### 5. **End-to-End Testing**

#### 5.1 What Are E2E Tests?

**Definition**: Tests that simulate **real user interactions** from start to finish.

**Example User Journey**:
```
1. User opens browser
2. User navigates to IDRM website
3. User clicks "Login"
4. User enters email & password
5. User clicks "Submit"
6. User sees dashboard
7. User clicks "Create Service Request"
8. User fills form
9. User clicks "Submit"
10. User sees confirmation message
```

#### 5.2 E2E Testing Tools

**Popular Tools**:
- **Playwright** (recommended)
- **Cypress**
- **Selenium**

#### 5.3 E2E Test Example (Playwright)

**Setup**:
```bash
npm install -D @playwright/test
npx playwright install
```

**Test File**:
```javascript
import { test, expect } from '@playwright/test';

test.describe('Service Request Creation', () => {
    test('should create service request from login to submission', async ({ page }) => {
        // 1. Navigate to login page
        await page.goto('http://localhost:3000/login');
        
        // 2. Fill login form
        await page.fill('input[name="email"]', 'test@example.com');
        await page.fill('input[name="password"]', 'SecurePass123!');
        
        // 3. Submit login
        await page.click('button[type="submit"]');
        
        // 4. Wait for redirect to dashboard
        await expect(page).toHaveURL('http://localhost:3000/dashboard');
        
        // 5. Verify user is logged in
        await expect(page.locator('text=Welcome back')).toBeVisible();
        
        // 6. Navigate to create service page
        await page.click('text=Create Service Request');
        await expect(page).toHaveURL('http://localhost:3000/services/new');
        
        // 7. Fill service request form
        await page.selectOption('select[name="service_type"]', 'MEDICAL');
        await page.selectOption('select[name="priority"]', 'CRITICAL');
        await page.fill('input[name="address"]', 'Test Address, Hyderabad');
        await page.fill('textarea[name="description"]', 'Urgent medical attention needed for elderly person.');
        
        // 8. Set location (simulate map click)
        await page.click('#map'); // Clicks center of map
        
        // 9. Submit form
        await page.click('button:has-text("Submit Request")');
        
        // 10. Wait for success message
        await expect(page.locator('.success-message')).toContainText('Service request created successfully');
        
        // 11. Verify redirect to dashboard
        await expect(page).toHaveURL(/.*dashboard/);
        
        // 12. Verify new service appears in list
        const serviceCard = page.locator('.service-card').first();
        await expect(serviceCard).toContainText('MEDICAL');
        await expect(serviceCard).toContainText('CRITICAL');
    });
    
    test('should show validation errors for incomplete form', async ({ page }) => {
        // Login first
        await loginAsUser(page);
        
        // Navigate to form
        await page.goto('http://localhost:3000/services/new');
        
        // Try to submit empty form
        await page.click('button:has-text("Submit Request")');
        
        // Should show validation errors
        await expect(page.locator('.error-message')).toContainText('Service type is required');
        await expect(page.locator('.error-message')).toContainText('Priority is required');
        await expect(page.locator('.error-message')).toContainText('Description is required');
    });
});

// Helper function
async function loginAsUser(page) {
    await page.goto('http://localhost:3000/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
}
```

**Running Tests**:
```bash
## Run all E2E tests
npx playwright test

## Run in headed mode (see browser)
npx playwright test --headed

## Run specific test
npx playwright test service-request-creation.spec.js

## Debug mode
npx playwright test --debug
```

---

#### 5.4 E2E Test Checklist

**Critical User Flows** (Test These First):
- [ ] User registration & email verification
- [ ] User login & logout
- [ ] Create service request (all service types)
- [ ] Update service status
- [ ] View service on map
- [ ] Filter & search services
- [ ] Provider accepts service
- [ ] Complete & verify service
- [ ] View analytics dashboard (admin)

**For Each Flow**:
- [ ] Happy path works
- [ ] Validation errors shown for invalid input
- [ ] Loading states visible
- [ ] Success/error messages display
- [ ] Navigation works correctly
- [ ] Data persists across page reloads

---

### 6. **API Testing**

#### 6.1 Manual API Testing (Postman/Insomnia)

**Setup Postman Collection**:

```json
{
  "info": {
    "name": "IDRM API Tests",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Auth",
      "item": [
        {
          "name": "Register",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePass123!\",\n  \"full_name\": \"Test User\",\n  \"phone\": \"9876543210\",\n  \"role\": \"CITIZEN\"\n}"
            },
            "url": {
              "raw": "{{base_url}}/api/v1/auth/register",
              "host": ["{{base_url}}"],
              "path": ["api", "v1", "auth", "register"]
            }
          }
        },
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{base_url}}/api/v1/auth/login",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"test@example.com\",\n  \"password\": \"SecurePass123!\"\n}"
            }
          },
          "event": [
            {
              "listen": "test",
              "script": {
                "exec": [
                  "pm.test('Status code is 200', function () {",
                  "    pm.response.to.have.status(200);",
                  "});",
                  "",
                  "pm.test('Response has access token', function () {",
                  "    var jsonData = pm.response.json();",
                  "    pm.expect(jsonData.data).to.have.property('access_token');",
                  "    pm.environment.set('access_token', jsonData.data.access_token);",
                  "});"
                ]
              }
            }
          ]
        }
      ]
    },
    {
      "name": "Services",
      "item": [
        {
          "name": "Create Service",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{access_token}}"
              }
            ],
            "url": "{{base_url}}/api/v1/services",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"service_type\": \"MEDICAL\",\n  \"priority\": \"CRITICAL\",\n  \"location\": {\n    \"type\": \"Point\",\n    \"coordinates\": [78.4867, 17.3850]\n  },\n  \"address\": \"Charminar, Hyderabad\",\n  \"description\": \"Urgent medical attention needed\"\n}"
            }
          }
        }
      ]
    }
  ]
}
```

---

#### 6.2 Automated API Tests (pytest)

```python
import pytest
from httpx import AsyncClient

class TestServiceAPI:
    """Test service API endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_services_unauthenticated(self, client: AsyncClient):
        """Test that listing services without auth returns 401."""
        response = await client.get("/api/v1/services")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_services_authenticated(
        self,
        client: AsyncClient,
        auth_token: str
    ):
        """Test listing services with valid auth."""
        response = await client.get(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "services" in data["data"]
        assert isinstance(data["data"]["services"], list)
    
    @pytest.mark.asyncio
    async def test_create_service_missing_fields(
        self,
        client: AsyncClient,
        auth_token: str
    ):
        """Test creating service with missing required fields."""
        incomplete_data = {
            "service_type": "MEDICAL"
            # Missing priority, location, description
        }
        
        response = await client.post(
            "/api/v1/services",
            json=incomplete_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert data["status"] == "error"
        assert "validation" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_service(
        self,
        client: AsyncClient,
        auth_token: str
    ):
        """Test getting service that doesn't exist."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        
        response = await client.get(
            f"/api/v1/services/{fake_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert data["status"] == "error"
        assert "not found" in data["message"].lower()
```

---

#### 6.3 API Testing Checklist

**For Each Endpoint**:
- [ ] Test success case (200/201)
- [ ] Test without authentication (401)
- [ ] Test with wrong permissions (403)
- [ ] Test with invalid data (400)
- [ ] Test with non-existent resource (404)
- [ ] Test request/response format
- [ ] Test pagination (if applicable)
- [ ] Test filtering & sorting (if applicable)

**Security Tests**:
- [ ] SQL injection attempts blocked
- [ ] XSS attempts blocked
- [ ] CSRF protection enabled
- [ ] Rate limiting works
- [ ] Sensitive data not in responses

---

### 7. **Database Testing**

#### 7.1 Schema Validation

**Verify Database Schema**:
```sql
-- Check all required tables exist
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Expected tables:
-- ├─ users
-- ├─ organizations
-- ├─ service_requests
-- ├─ disaster_events
-- ├─ donations
-- ├─ audit_logs
-- └─ notifications

-- Check table columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name = 'service_requests'
ORDER BY ordinal_position;

-- Check indexes exist
SELECT indexname, indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename = 'service_requests';

-- Check constraints
SELECT conname, contype, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'service_requests'::regclass;
```

---

#### 7.2 Data Integrity Tests

```python
@pytest.mark.asyncio
async def test_unique_constraint_violation(db_session):
    """Test that duplicate emails are prevented."""
    user1 = User(
        email="duplicate@example.com",
        password="hash1",
        full_name="User One"
    )
    db_session.add(user1)
    await db_session.commit()
    
    # Try to create another user with same email
    user2 = User(
        email="duplicate@example.com",  # ← Same email
        password="hash2",
        full_name="User Two"
    )
    db_session.add(user2)
    
    # Should raise IntegrityError
    with pytest.raises(IntegrityError):
        await db_session.commit()

@pytest.mark.asyncio
async def test_foreign_key_constraint(db_session):
    """Test that foreign keys are enforced."""
    # Try to create service without valid user
    service = ServiceRequest(
        requestor_id="00000000-0000-0000-0000-000000000000",  # ← Doesn't exist
        service_type="MEDICAL",
        priority="CRITICAL"
    )
    db_session.add(service)
    
    # Should raise ForeignKeyViolation
    with pytest.raises(IntegrityError):
        await db_session.commit()
```

---

#### 7.3 Database Testing Checklist

**Schema Validation**:
- [ ] All required tables created
- [ ] All columns have correct types
- [ ] All indexes created
- [ ] All constraints defined
- [ ] All foreign keys set up

**Data Integrity**:
- [ ] Unique constraints work
- [ ] Foreign key constraints work
- [ ] Check constraints work
- [ ] Cascade deletes work
- [ ] Default values set correctly

**Performance**:
- [ ] Queries use indexes
- [ ] No N+1 query problems
- [ ] Pagination works
- [ ] Complex queries optimized

---

### 8. **Frontend Testing**

#### 8.1 Component Testing

**Example - Testing React Component**:
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import { ServiceCard } from '../components/ServiceCard';

describe('ServiceCard', () => {
    it('renders service information correctly', () => {
        const service = {
            service_id: '123',
            service_type: 'MEDICAL',
            priority: 'CRITICAL',
            address: 'Test Address',
            status: 'APPROVED',
            created_at: '2026-05-16T10:00:00Z'
        };
        
        render(<ServiceCard service={service} />);
        
        expect(screen.getByText('MEDICAL')).toBeInTheDocument();
        expect(screen.getByText('CRITICAL')).toBeInTheDocument();
        expect(screen.getByText('Test Address')).toBeInTheDocument();
    });
    
    it('calls onAccept when accept button clicked', () => {
        const service = { /* ... */ };
        const onAccept = jest.fn();
        
        render(<ServiceCard service={service} onAccept={onAccept} />);
        
        const acceptButton = screen.getByRole('button', { name: /accept/i });
        fireEvent.click(acceptButton);
        
        expect(onAccept).toHaveBeenCalledWith(service.service_id);
    });
    
    it('disables accept button when service is completed', () => {
        const service = {
            /* ... */
            status: 'COMPLETED'
        };
        
        render(<ServiceCard service={service} />);
        
        const acceptButton = screen.getByRole('button', { name: /accept/i });
        expect(acceptButton).toBeDisabled();
    });
});
```

---

#### 8.2 Frontend Testing Checklist

**Component Tests**:
- [ ] Renders correctly with props
- [ ] Handles user interactions (clicks, inputs)
- [ ] Shows loading states
- [ ] Shows error states
- [ ] Disabled states work correctly
- [ ] Conditional rendering works

**Form Validation**:
- [ ] Required fields enforced
- [ ] Format validation (email, phone)
- [ ] Error messages displayed
- [ ] Submit button disabled when invalid
- [ ] Success message after submission

**Accessibility**:
- [ ] Keyboard navigation works
- [ ] Screen reader labels present
- [ ] Focus indicators visible
- [ ] Color contrast sufficient
- [ ] ARIA attributes correct

---

### 9. **Security Testing**

#### 9.1 Authentication & Authorization

**Test Checklist**:
- [ ] Login requires valid credentials
- [ ] Login fails with wrong password
- [ ] Token expires after 15 minutes
- [ ] Refresh token works
- [ ] Logout invalidates tokens
- [ ] Protected routes require auth
- [ ] Role-based access enforced

**Example Tests**:
```python
@pytest.mark.asyncio
async def test_access_protected_route_without_token(client):
    """Test that protected route rejects request without token."""
    response = await client.get("/api/v1/admin/users")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_access_protected_route_with_expired_token(client):
    """Test that expired token is rejected."""
    # Create token that expired 1 hour ago
    expired_token = create_access_token(
        user_id="123",
        expires_delta=timedelta(hours=-1)
    )
    
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_citizen_cannot_access_admin_endpoint(client, citizen_token):
    """Test that citizen role cannot access admin endpoints."""
    response = await client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {citizen_token}"}
    )
    assert response.status_code == 403
```

---

#### 9.2 Input Validation & SQL Injection

**Test SQL Injection Attempts**:
```python
@pytest.mark.asyncio
async def test_sql_injection_attempt_in_search(client, auth_token):
    """Test that SQL injection attempts are blocked."""
    # Try SQL injection in search query
    malicious_query = "'; DROP TABLE users; --"
    
    response = await client.get(
        f"/api/v1/services?search={malicious_query}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # Should not execute SQL injection
    # Should either return 400 (invalid) or safely escape input
    assert response.status_code in [200, 400]
    
    # Verify users table still exists
    users_exist = await db.execute("SELECT COUNT(*) FROM users")
    assert users_exist.scalar() > 0  # Table not dropped!
```

---

#### 9.3 Security Testing Checklist

**Authentication**:
- [ ] Passwords hashed (never plain text)
- [ ] Token expiry enforced
- [ ] Refresh token rotation works
- [ ] Logout invalidates tokens
- [ ] Rate limiting on login endpoint

**Authorization**:
- [ ] RBAC enforced
- [ ] Users can only access own data
- [ ] Admin routes protected
- [ ] Service providers can only update assigned services

**Input Validation**:
- [ ] SQL injection blocked
- [ ] XSS attempts escaped
- [ ] File upload validation
- [ ] Max request size enforced
- [ ] Invalid JSON rejected

**Data Protection**:
- [ ] Sensitive data encrypted
- [ ] HTTPS enforced
- [ ] CORS configured correctly
- [ ] Security headers present
- [ ] No credentials in logs

---

### 10. **Performance Testing**

#### 10.1 Load Testing (Locust)

**Setup**:
```bash
pip install locust
```

**locustfile.py**:
```python
from locust import HttpUser, task, between

class IDRMUser(HttpUser):
    """Simulate IDRM user behavior."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Login when user starts."""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "SecurePass123!"
        })
        
        if response.status_code == 200:
            self.token = response.json()["data"]["access_token"]
        else:
            self.token = None
    
    @task(3)  # Weight: 3 (most common action)
    def view_services(self):
        """View list of services."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.get("/api/v1/services", headers=headers)
    
    @task(2)  # Weight: 2
    def view_single_service(self):
        """View specific service."""
        headers = {"Authorization": f"Bearer {self.token}"}
        # Assume we know a valid service ID
        self.client.get("/api/v1/services/some-uuid-here", headers=headers)
    
    @task(1)  # Weight: 1 (less common)
    def create_service(self):
        """Create new service request."""
        headers = {"Authorization": f"Bearer {self.token}"}
        self.client.post("/api/v1/services", headers=headers, json={
            "service_type": "MEDICAL",
            "priority": "CRITICAL",
            "location": {"type": "Point", "coordinates": [78.48, 17.38]},
            "address": "Load Test Address",
            "description": "Performance test service"
        })
```

**Running Load Tests**:
```bash
## Run with 100 users, spawn rate of 10 users/second
locust -f locustfile.py --host=http://localhost:8000 --users 100 --spawn-rate 10

## Run headless (no UI) for 60 seconds
locust -f locustfile.py --host=http://localhost:8000 \
    --users 100 --spawn-rate 10 \
    --run-time 60s --headless
```

---

#### 10.2 Performance Benchmarks

**Target Performance**:

| Metric | Target | Critical Threshold |
|--------|--------|-------------------|
| **API Response Time** | < 200ms (p95) | < 500ms |
| **Database Query Time** | < 50ms (p95) | < 200ms |
| **Page Load Time** | < 2 seconds | < 4 seconds |
| **Concurrent Users** | 10,000 | 5,000 |
| **Requests per Second** | 1,000 | 500 |

---

#### 10.3 Performance Testing Checklist

**Load Testing**:
- [ ] System handles target concurrent users
- [ ] Response times within limits under load
- [ ] No memory leaks during extended test
- [ ] Database connection pool adequate
- [ ] CPU/memory usage acceptable

**Stress Testing** (Find Breaking Point):
- [ ] Gradually increase load until failure
- [ ] Document failure point
- [ ] System recovers after load removed
- [ ] Error messages clear under stress

**Endurance Testing** (Long Duration):
- [ ] Run for 24+ hours at normal load
- [ ] No performance degradation
- [ ] No memory leaks
- [ ] Logs don't fill disk
- [ ] Connection pools stable

---

### 11. **Manual Testing Checklists**

#### 11.1 User Registration & Login

**Registration Flow**:
- [ ] Registration form loads correctly
- [ ] All fields visible and accessible
- [ ] Email validation works (format check)
- [ ] Password validation works (length, characters)
- [ ] Phone validation works (10 digits)
- [ ] Submit button enabled only when valid
- [ ] Success message displayed
- [ ] Verification email sent
- [ ] User can't login before verification
- [ ] Verification link works
- [ ] User can login after verification

**Login Flow**:
- [ ] Login form loads correctly
- [ ] Email/password fields work
- [ ] "Show password" toggle works
- [ ] Login succeeds with correct credentials
- [ ] Login fails with wrong password
- [ ] Error message clear and helpful
- [ ] "Forgot password" link works
- [ ] Redirect to dashboard after login
- [ ] Session persists after refresh
- [ ] Logout works correctly

---

#### 11.2 Service Request Creation

**Create Service Flow**:
- [ ] Form loads correctly
- [ ] All fields visible
- [ ] Service type dropdown populated
- [ ] Priority dropdown populated
- [ ] Map loads correctly
- [ ] Can click map to set location
- [ ] Location coordinates captured
- [ ] Address field auto-filled from map click
- [ ] Description textarea works
- [ ] Character count displayed
- [ ] File upload works (if applicable)
- [ ] Submit button disabled until valid
- [ ] Loading indicator during submit
- [ ] Success message displayed
- [ ] Redirect to dashboard
- [ ] New service visible in list
- [ ] Service appears on map

---

#### 11.3 Service Management (Provider View)

**Provider Workflow**:
- [ ] Provider can see available services
- [ ] Services filtered by provider's service types
- [ ] Map shows only relevant services
- [ ] Provider can accept service
- [ ] Acceptance sends notification to requester
- [ ] Provider can update status to "In Progress"
- [ ] Provider can add notes
- [ ] Provider can upload proof photo
- [ ] Provider can mark service complete
- [ ] Requester notified of completion
- [ ] Provider can view service history

---

#### 11.4 Admin Dashboard

**Admin Functions**:
- [ ] Dashboard loads with metrics
- [ ] Total requests count accurate
- [ ] Status breakdown chart correct
- [ ] Priority distribution chart correct
- [ ] Recent activity list updates
- [ ] Can filter by date range
- [ ] Can export reports
- [ ] User management panel accessible
- [ ] Can view all users
- [ ] Can edit user roles
- [ ] Can deactivate users
- [ ] Can verify organizations
- [ ] Audit log accessible
- [ ] System settings accessible

---

### 12. **Pre-Deployment Verification**

#### 12.1 Staging Deployment Checklist

**Before Deploying to Staging**:
- [ ] All tests passing locally
- [ ] Code reviewed and approved
- [ ] No console errors in browser
- [ ] No Python warnings
- [ ] Database migrations created
- [ ] Environment variables documented
- [ ] Dependencies updated in requirements.txt
- [ ] Configuration files updated

**After Deploying to Staging**:
- [ ] Database migrations applied successfully
- [ ] All services start without errors
- [ ] Health check endpoints responding
- [ ] Can register new user
- [ ] Can login
- [ ] Can create service request
- [ ] Map displays correctly
- [ ] No JavaScript errors in console
- [ ] No 500 errors in logs
- [ ] SSL certificate valid
- [ ] Email notifications work

---

#### 12.2 Production Deployment Checklist

**Pre-Deployment** (1 Week Before):
- [ ] All staging tests passed
- [ ] Performance tests completed
- [ ] Security audit completed
- [ ] Backup procedures tested
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured
- [ ] Documentation updated
- [ ] Team training completed

**Deployment Day**:
- [ ] Announcement sent to users
- [ ] Database backup created
- [ ] Code deployed
- [ ] Migrations run successfully
- [ ] Services restarted
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Monitoring dashboards green
- [ ] No errors in logs

**Post-Deployment** (24 Hours After):
- [ ] All critical paths tested manually
- [ ] User feedback monitored
- [ ] Error rates normal
- [ ] Performance metrics normal
- [ ] Database queries optimized
- [ ] No memory leaks detected
- [ ] Logs reviewed for anomalies
- [ ] Team debriefing completed

---

#### 12.3 Smoke Test Checklist

**Run These Tests Immediately After Deployment**:

```bash
#!/bin/bash
## smoke-test.sh - Quick validation after deployment

BASE_URL="https://api.idrm.gov.in"

echo "🔍 Running smoke tests..."

## Test 1: Health check
echo "✅ Testing health endpoint..."
curl -f "$BASE_URL/health" || exit 1

## Test 2: Register
echo "✅ Testing registration..."
curl -f -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "smoketest@example.com",
    "password": "Test123!",
    "full_name": "Smoke Test",
    "phone": "9999999999",
    "role": "CITIZEN"
  }' || exit 1

## Test 3: Login
echo "✅ Testing login..."
TOKEN=$(curl -f -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "smoketest@example.com", "password": "Test123!"}' \
  | jq -r '.data.access_token') || exit 1

## Test 4: List services
echo "✅ Testing service list..."
curl -f "$BASE_URL/api/v1/services" \
  -H "Authorization: Bearer $TOKEN" || exit 1

echo "✅ All smoke tests passed!"
```

---

### 🎉 **You're a Testing Expert!**

You now understand:

✅ **What testing is** (finding bugs before users do)  
✅ **Testing pyramid** (many unit tests, fewer E2E tests)  
✅ **Unit testing** (pytest, vitest, testing individual functions)  
✅ **Integration testing** (API endpoints, database operations)  
✅ **E2E testing** (Playwright, full user workflows)  
✅ **API testing** (Postman collections, automated tests)  
✅ **Database testing** (schema validation, data integrity)  
✅ **Frontend testing** (component tests, accessibility)  
✅ **Security testing** (auth, SQL injection, XSS)  
✅ **Performance testing** (Locust, load testing, benchmarks)  
✅ **Manual testing** (checklists for every user flow)  
✅ **Pre-deployment** (staging validation, production readiness)  

---

### 📚 **What's Next?**

- **[41-CODE-STANDARDS.md](41-CODE-STANDARDS.md)** - Write better code
- **[40-DATA-FORMATS.md](40-DATA-FORMATS.md)** - Understand data structures
- **[43-CONTRIBUTION-GUIDE.md](43-CONTRIBUTION-GUIDE.md)** - Contribute to IDRM

---

**Document Information**  
**Created**: May 16, 2026  
**Purpose**: Complete guide to IDRM testing and QA  
**Difficulty**: 🟡 Intermediate (beginner-friendly)  
**Estimated Reading Time**: 55-70 minutes  
**Part of**: IDRM Documentation Series (Document 42/43)
