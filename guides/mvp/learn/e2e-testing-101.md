# E2E Testing 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/QA · Status: MVP-aware (tooling matures in FFP) · Track: Quality (#27)*
> *Unit tests check pieces; end-to-end tests check the **whole journey** the way a real user experiences it. Read
> [Testing 101](testing-101.md) first — E2E is the top of its pyramid.*

---

## 1. What E2E testing is

**End-to-end (E2E) testing** drives the entire system — UI, API, database, storage — exactly as a real user would,
and checks the outcome. Not "does this function return the right value?" but "**can a citizen actually report a
help request, and does a coordinator see it?**" It's the most realistic test, and the most valuable for
confidence that the product *works*.

It's also the slowest and most brittle, so — per the [testing pyramid](testing-101.md) — you write **few** E2E
tests, covering only the **critical journeys**.

---

## 2. IDRM's critical journeys

The handful of flows that must never break:

1. **Report** — a citizen creates a help request (incident) with photo upload.
2. **Approve** — a coordinator approves a `critical` incident.
3. **Accept → complete** — a provider accepts, works, and completes it.
4. **Verify** — a coordinator verifies completion.
5. **Login/roles** — each role can do its job and *cannot* do others'.

These map directly to the incident lifecycle from [Incident Management 101](incident-management-101.md).

---

## 3. How E2E tests run

A test tool automates a real browser: click, type, submit, and assert what appears.

```
Given a logged-in citizen
When they submit a help request for "rescue", priority "high"
Then they see it listed as "created"
And a coordinator, logged in separately, sees it on the map/list
```

- **Tooling:** **Playwright** (or Cypress) drives the browser. IDRM's **FFP** React app is the primary E2E target;
  the MVP's server-rendered UI can be smoke-tested the same way.
- Run E2E in **CI** against a staging environment, *after* the faster unit/integration tests pass — they're the
  final gate ([CI/CD 101](ci-cd-101.md)).

---

## 4. Keeping E2E tests healthy

- **Test the journey, not the pixels** — locate elements by role/label (accessible selectors), not brittle CSS,
  so tests survive redesigns (and double as [accessibility](accessibility-testing-101.md) pressure).
- **Stable test data** — seed a known state; clean up after.
- **Few and meaningful** — an E2E suite that takes an hour and flakes is one nobody trusts.

---

## 5. Mastery check

1. Explain what E2E testing checks and how it differs from unit tests.
2. Say why you write **few** E2E tests (pyramid).
3. List IDRM's critical journeys worth an E2E test.
4. Describe how a browser-automation E2E test works, and name a tool.
5. Give two habits that keep E2E tests from becoming flaky.

---

## 6. Go deeper

- Playwright — playwright.dev · Cypress — cypress.io
- Related: [Testing 101](testing-101.md) · [API Testing 101](api-testing-101.md) · [Accessibility Testing 101](accessibility-testing-101.md)

---
*Next:* [Performance Testing 101](performance-testing-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
