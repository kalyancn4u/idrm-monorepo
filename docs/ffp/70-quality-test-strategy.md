# IDRM FFP — Quality & Test Strategy (at Scale)

> *Type: Document (specification) · Audience: QA, developers · Status: FFP — next-phase (planned)*
> *Extends the MVP test strategy [`../idrm-mvp-docs/70-quality-test-strategy.md`](../mvp/70-quality-test-strategy.md). Adds the testing the MVP deferred — for **multiple services, rich clients, and enterprise SLAs**. Consolidates `v3/70-quality-testing-and-verification.md`, `71-quality-code-standards.md`.*

> **Invariant:** the MVP pyramid (Unit/API/Integration, ≥80% coverage, gates) **stays**. The FFP adds the
> upper/broader layers and cross-service assurance. Governing principle (blueprint): *test operational
> scenarios, not merely functions* — e.g. flood report → triage → command → task → responder → resource →
> resolution → audit → report.

---

## 1. What the FFP adds (vs MVP)

| Layer | MVP | FFP |
|---|---|---|
| Unit / API / Integration | ✅ core | ✅ per service |
| **Contract testing** | — | **consumer/provider contracts** across services (public API + events) |
| **End-to-end** | light | **full E2E** across clients (web/mobile) + cross-browser grids |
| **Performance / load** | intent only | **k6 / Locust** at surge (10k+ concurrent, 25k+ spike) |
| **Resilience / chaos** | — | fault injection, failover, DR drills |
| **Security (DAST)** | authz suite | **OWASP ZAP**, dependency/container scanning, SBOM |
| **Accessibility** | AA checks | automated + manual **WCAG 2.2** |
| **Delivery metrics** | gates | **full DORA** (deploy freq, lead time, CFR, MTTR) |

## 2. Contract testing (the microservices keystone)
As services extract, **contract tests** guarantee the **public API never breaks** and inter-service **event
schemas** stay compatible (provider verifies consumer expectations). This is what makes "evolution, not
rewrite" safe.

## 3. Scenario & drill testing
Enterprise readiness is proven by **operational drills** (disaster scenarios end-to-end across services and
clients), not unit counts. Each phase gate (roadmap) includes a drill.

## 4. CI/CD quality gates (extended)
MVP gates (Black/Ruff/mypy/pytest/≥80%) **per service**, plus SAST/SCA/SBOM/container-scan, contract tests,
and staged E2E/UAT before production ([`80-ops-platform-and-deployment.md`](80-ops-platform-and-deployment.md)).

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`20-architecture-system.md`](20-architecture-system.md) · [`80-ops-platform-and-deployment.md`](80-ops-platform-and-deployment.md) ·
MVP tests [`../idrm-mvp-docs/70-quality-test-strategy.md`](../mvp/70-quality-test-strategy.md) · [`../../docs/06-quality.md`](../../docs/06-quality.md).
