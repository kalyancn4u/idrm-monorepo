# Quality — How We Know It Works

> **Part of:** IDRM Documentation · `06-quality.md`
> **Answers:** How do we know IDRM works, and how does code get safely shipped?
> **Source posters:** Posters 26–27 (Phase 6 Quality)
> **Audience:** Testers & developers (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [The testing pyramid](#1-the-testing-pyramid) — how we test, at every level.
2. [Types of testing](#2-types-of-testing) — what each one checks.
3. [Quality gates](#3-quality-gates) — the bar code must clear.
4. [The CI/CD pipeline](#4-the-cicd-pipeline) — from commit to deployment.
5. [Tooling](#5-tooling).

---

## 1. The testing pyramid

IDRM tests in layers, with many fast checks at the bottom and fewer, broader checks at the top. This catches
problems early and cheaply, while still proving whole user journeys work.

```
              ▲   fewer, slower, broader
        ┌─────────────┐
        │  E2E  ~5%   │   whole user workflows, end to end
        ├─────────────┤
        │Integ. ~15%  │   modules working together (+ database)
        ├─────────────┤
        │  API  ~20%  │   each endpoint behaves per contract
        ├─────────────┤
        │ Unit  ~60%  │   individual functions & models
        ├─────────────┤
        │ Test Data & Environment Foundation │   reliable · isolated · repeatable
        └─────────────┘
              ▼   many, fast, focused
```

Many fast unit tests enable rapid feedback; focused integration/API tests catch interface and configuration
issues; a few E2E tests validate critical user journeys — all on a reliable, repeatable **test-data foundation**.

**Our testing approach:** Understand requirements → Test planning → Test design → Test execution → Reporting &
insights. We **shift left** (test early, test often) and run tests **in CI/CD on every change**.

---

## 2. Types of testing

Beyond the pyramid's core levels, IDRM plans for the full range that a dependable system needs:

| Test type | What it checks |
|---|---|
| **Unit** | Individual functions, models, and utilities in isolation. |
| **Integration** | Modules working together, including real database operations. |
| **API** | Each endpoint's inputs, outputs, status codes, and rules. |
| **Database** | Schema, constraints, migrations, and query correctness. |
| **End-to-end (E2E)** | Complete workflows (e.g. report incident → assign → resolve). |
| **Performance** | Speed and behaviour under load and surge conditions. |
| **Security** | Access control, injection, and common-vulnerability checks. |
| **Contract** | APIs keep the promises their consumers depend on. |
| **User Acceptance (UAT)** | Real users confirm it meets their needs. |

---

## 3. Quality gates

Code must clear an automatic bar before it's accepted — no exceptions, so quality never depends on memory:

| Gate | Standard |
|---|---|
| **Formatting** | Consistent style, applied automatically (Black / isort). |
| **Linting** | No lint errors (Ruff). |
| **Type checks** | Types are consistent (mypy). |
| **Tests pass** | The full test suite is green. |
| **Coverage** | ≥ 80% overall (≥ 70% minimum gate; higher on critical paths). |
| **Security** | No high/critical vulnerabilities; performance SLAs met; all contracts verified. |

---

## 4. The CI/CD pipeline

Every change flows through the same automated pipeline, so shipping is repeatable and safe:

```
Commit / Push
   → Lint & Format   (Ruff, Black)
   → Type Check      (mypy)
   → Unit Tests      (pytest)
   → Integration Tests (pytest)
   → Coverage        (pytest-cov, must meet the gate)
   → Build / Package (build artifacts)
   → Deploy          (to staging, then production)
```

- **Continuous Integration (CI):** every push is automatically linted, type-checked, and tested.
- **Continuous Delivery (CD):** once green, the change is packaged and deployed through environments.
- **Automation host:** the pipeline runs on **GitHub Actions**.

If any stage fails, the change stops there — problems are caught *before* they reach users.

**Triggers:** push to main / release branch, pull requests, manual, scheduled, and tag/version releases.

### 4.1 Health metrics (DORA)

We watch a small set of delivery-health metrics:

| Metric | What it tells us |
|---|---|
| **Deployment frequency** | How often we ship. |
| **Lead time for changes** | Commit → production time. |
| **Change failure rate** | % of deploys causing issues. |
| **Mean time to recover (MTTR)** | How fast we recover from a failure. |
| **Test coverage · vulnerability count** | Quality and security signal. |

### 4.2 Release readiness (all must pass before production)

- ☑ All linting & formatting pass
- ☑ All tests pass (unit → E2E)
- ☑ Coverage threshold met (≥ 80%)
- ☑ No high/critical vulnerabilities
- ☑ Build & package succeed
- ☑ Smoke / health checks pass
- ☑ Approved for production release

---

## 5. Tooling

| Purpose | Tools (examples) |
|---|---|
| **Unit / coverage** | pytest, pytest-cov |
| **Lint / format / types** | Ruff, Black, isort, mypy |
| **API testing** | pytest + FastAPI test client (httpx), Postman/Newman |
| **End-to-end** | Playwright / Cypress / Selenium |
| **Performance** | k6 / Locust / JMeter |
| **Security** | OWASP ZAP, Snyk / dependency scanning |
| **CI/CD host** | GitHub Actions |

Test details connect directly to the qualities in [`02-architecture.md`](02-architecture.md) and the security
controls in [`05-security.md`](05-security.md) — quality is how we *prove* those promises.

---

## Where this leads

- How the tested system is deployed and run → [`07-operations.md`](07-operations.md)
- Who owns testing and CI/CD → [`08-organization.md`](08-organization.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"High test coverage. Reliable APIs. Quality by default."*
