# API Testing 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/QA · Status: MVP — current · Track: Quality (#26)*
> *IDRM's API is the contract every client depends on. API testing proves that contract holds. Read
> [Testing 101](testing-101.md) and [REST API 101](rest-api-101.md) first; this guide is where they meet.*

---

## 1. Why test the API specifically

The API is IDRM's **public contract** — the web UI, a future mobile app, and partner agencies all rely on it.
If an endpoint quietly changes shape, every client breaks. **API testing** checks each endpoint's *behaviour and
contract*: the right status code, the right response shape, the right rules enforced — independent of any UI.

---

## 2. What an API test checks

For each endpoint, verify:

- **Status code** — `201` on create, `200` on read, `400` on bad input, `401`/`403` on auth failures, `404` when
  missing.
- **Response shape** — matches the contract: `snake_case`, UUID ids, ISO-8601 `*_at`, lists wrapped
  `{ data, pagination }`, singles as bare objects, errors as the envelope with a `code`.
- **Business rules** — the action actually enforces the domain (a provider *can* accept; a citizen *cannot*
  verify; a `critical` incident needs approval).
- **Validation** — invalid `service_type`/`priority`, oversized uploads, missing fields → rejected with a clear
  `code`.

---

## 3. A worked example

```python
def test_create_incident_returns_201_and_created_state(client, citizen_token):
    resp = client.post(
        "/api/v1/incidents",
        headers={"Authorization": f"Bearer {citizen_token}"},
        json={"service_type": "rescue", "priority": "high", "description": "3 stranded"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "created"          # correct initial state
    assert "id" in body and "created_at" in body  # contract fields present
```

And the negative cases — just as important:

```python
def test_citizen_cannot_verify_incident(client, citizen_token, existing_incident):
    resp = client.patch(f"/api/v1/incidents/{existing_incident}",
                        headers={"Authorization": f"Bearer {citizen_token}"},
                        json={"status": "verified"})
    assert resp.status_code == 403   # RBAC enforced on the server
```

IDRM tests the API with **pytest** against the FastAPI app (using its test client), so these run fast, without a
browser.

---

## 4. Contract testing: don't let tests drift from the spec

The API is described in **OpenAPI** (`40-api-openapi.yaml`). **Contract testing** checks that the real responses
match that spec — so the documentation, the code, and the tests can't silently diverge. (In the future
multi-client phase, mock servers are generated from the same OpenAPI file for exactly this reason.)

---

## 5. Auth, roles, and edge cases

Because IDRM is permission-heavy, test the **same endpoint under different roles** (citizen / provider /
coordinator / guest) — confirming both what each role *can* and *cannot* do. Test token expiry, missing tokens,
and the lockout behaviour too.

---

## 6. Mastery check

1. Explain why the API deserves its own tests, separate from the UI.
2. List the four things an API test should verify.
3. Write a positive and a negative API test for `/api/v1/incidents`.
4. Explain **contract testing** and how OpenAPI prevents drift.
5. Say why you test one endpoint under multiple roles.

---

## 7. Go deeper

- IDRM API spec: [`../../idrm-mvp-docs/40-api-specification.md`](../../../docs/mvp/40-api-specification.md) ·
  test strategy [`../../idrm-mvp-docs/70-quality-test-strategy.md`](../../../docs/mvp/70-quality-test-strategy.md)
- FastAPI testing — fastapi.tiangolo.com/tutorial/testing · Schemathesis (OpenAPI-based testing) — schemathesis.readthedocs.io
- Related: [REST API 101](rest-api-101.md) · [Testing 101](testing-101.md) · [RBAC/ABAC 101](rbac-abac-101.md)

---
*Next:* [Accessibility Testing 101](accessibility-testing-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
