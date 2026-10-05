# IDRM MVP — Seed Data & Fixtures (the fake-but-real starter dataset)

> *Type: Document (data / deep-dive) · Audience: complete novices → backend & QA engineers · Status: MVP — current*
> *The row-by-row deep-dive behind [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §3.4 (the
> **signed-off** seed spec) and [`50-data-model.md`](50-data-model.md) §9. Where §3.4 gives the **shape** of the
> starter data, this gives the **exact rows** — and it is the written companion to the real script at
> [`../../services/monolith/scripts/seed.py`](../../services/monolith/scripts/seed.py), loaded by `make seed`.*

---

## 0. What this is, and why it exists

**Seed data** is realistic starter data we load into a *fresh, empty* database so that:

1. **the app looks alive** the first time you open it — real names, real map pins, requests in every stage —
   instead of blank screens; and
2. **tests and demos have something meaningful to work against** — you can exercise *every* rule (each lifecycle
   transition, each role's permissions, the map's "nearest responder" search) because the data deliberately
   contains at least one example of each.

Two words you will see throughout, defined once:

- **Fixture** — a small, fixed bundle of data prepared for a test so the test starts from a known state. Per
  [`70-quality-test-strategy.md`](70-quality-test-strategy.md), each module also owns *tiny* fixtures (built in
  `services/monolith/tests/factories.py`) so it can be tested **in isolation**, without loading this whole dataset.
- **Idempotent** — *"safe to run many times."* Running the seed twice must **not** create duplicate rows. We
  guarantee this by giving every seed row a **deterministic UUID** (a UUID computed from a stable text key, so the
  same row always gets the same id) and inserting it only if that id is not already present.

> **Where the truth lives.** This document *describes* the dataset; [`../../services/monolith/scripts/seed.py`](../../services/monolith/scripts/seed.py)
> *is* the dataset. If they ever disagree, the script wins and this doc should be updated to match.

---

## 1. How to load it (the mechanism)

The seed is a standalone, idempotent script wired to a `make` target (see
[`27-implementation-roadmap.md`](27-implementation-roadmap.md) §11):

```bash
cd code
make migrate     # 1. create the schema (Alembic revisions 0001–0006)
make seed        # 2. load this dataset  (python scripts/seed.py)
```

- It opens **one** async database session, inserts every row inside **one transaction**, and commits at the end.
- Every insert is guarded: `if the row's fixed id already exists → skip`. So `make seed` is safe to re-run after
  adding new rows, and safe to run on a database that was already seeded.
- **Passwords:** all seed accounts share one **dev-only** password, hashed once with bcrypt and reused. This is
  *only* for local development and demos. The Ubuntu bring-up (`PENDING.md` §1) generates real credentials.

> **Login for demos:** every seed user's password is `IDRMseed#2026`. Example: log in as
> `arjun@idrm.example` to act as a coordinator, or `lakshmi@idrm.example` for the admin views.

---

## 2. The people (users)

Grounded in the PRD personas ([`10-requirements-prd.md`](10-requirements-prd.md)). All are `status = active`,
`email_verified = true`.

| Email | Role | Name | Stands for | Home area (lat, lng) |
|---|---|---|---|---|
| `rajesh@idrm.example` | `citizen` | Rajesh Kumar | An affected citizen needing help | Hyderabad (17.385, 78.486) |
| `priya@idrm.example` | `provider` | Dr. Priya Sharma | A medical/NGO responder | Hyderabad (17.441, 78.391) |
| `arjun@idrm.example` | `coordinator` | Arjun Reddy | A volunteer coordinator | Warangal (17.978, 79.594) |
| `lakshmi@idrm.example` | `admin` | Lakshmi Iyer (IAS) | A senior government officer (oversight) | Vijayawada (16.506, 80.648) |
| `sita@idrm.example` | `citizen` | Sita Devi | Extra citizen — list/test volume | Hyderabad (17.400, 78.500) |
| `mohan@idrm.example` | `citizen` | Mohan Rao | Extra citizen — list/test volume | Warangal (17.960, 79.560) |
| `kiran@idrm.example` | `provider` | Kiran Varma | Extra provider (rescue) | Warangal (17.978, 79.594) |
| `ananya@idrm.example` | `provider` | Ananya Nair | Extra provider (NGO relief) | Hyderabad (17.385, 78.486) |

Plus a **guest** — *not* a user row at all: the guest is represented by an incident whose `requester_id` is `NULL`
(see §5, the `guest` incident). That is exactly how the real system records an anonymous, unauthenticated report.

---

## 3. The providers (organizations)

Each organization is **owned by** one provider user, has a PostGIS service-area centre + radius, and is either
verified (by Lakshmi, the admin) or pending — so you can see both states and exercise the "only a **verified** org
can claim requests" rule ([`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md)).

| Name | Type | Owner | Service categories | Centre (lat, lng) | Radius | Verified? | Capacity |
|---|---|---|---|---|---|---|---|
| Priya Care Hospital | `hospital` | Priya | `{medical}` | (17.441, 78.391) | 15 km | ✅ yes | 20 |
| Deccan Relief NGO | `ngo` | Ananya | `{food, shelter}` | (17.385, 78.486) | 25 km | ✅ yes | 50 |
| Warangal Volunteer Corps | `volunteer_group` | Kiran | `{rescue}` | (17.978, 79.594) | 30 km | ⏳ pending | 15 |

### Resources (each provider's assets on the map)

| Name | Organization | Kind | Qty | Location | Available? |
|---|---|---|---|---|---|
| Ambulance-01 | Priya Care Hospital | `ambulance` | 2 | (17.441, 78.391) | yes |
| Hospital Beds | Priya Care Hospital | `beds` | 40 | (17.441, 78.391) | yes |
| Rescue Boat | Warangal Volunteer Corps | `boat` | 1 | (17.978, 79.594) | yes |
| Water Tanker | Deccan Relief NGO | `water_tanker` | 3 | (17.385, 78.486) | yes |

---

## 4. The requests (incidents) — one in *every* lifecycle state

This is the heart of the dataset: **at least one incident in each of the eight lifecycle states**
([`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) §4), with varied
`service_type` and `priority`, real coordinates, and **one guest-submitted** request. Together they let you (and
the tests) walk every transition and every RBAC rule.

| Key | Service · Priority | Final status | Requester | Assigned org | Location | Description |
|---|---|---|---|---|---|---|
| `created` | water · high | `created` | Sita | — | (17.40, 78.50) | Borewell dry — need drinking water. |
| `approved` | rescue · critical | `approved` | Mohan | — | (17.98, 79.60) | Building collapse, people trapped. |
| `accepted` | medical · critical | `accepted` | Rajesh | Priya Care | (17.39, 78.47) | Injured, need medical help. |
| `in_progress` | medical · high | `in_progress` | Rajesh | Priya Care | (17.44, 78.40) | Elderly patient needs evacuation. |
| `completed` | food · medium | `completed` | Sita | Deccan Relief | (17.38, 78.49) | Food supplies needed at shelter. |
| `verified` | medical · high | `verified` (★5) | Rajesh | Priya Care | (17.42, 78.42) | Medical evacuation completed. |
| `cancelled` | shelter · low | `cancelled` | Mohan | — | (17.95, 79.55) | Shelter requested — family found on their own. |
| `rejected` | other · low | `rejected` | Sita | — | (17.41, 78.51) | Report could not be substantiated. |
| `guest` | other · medium | `created` | **guest (NULL)** | — | (16.506, 80.648) | Roadblock near market — need assistance. |

Notes that make these *correct*, not just present:

- The **guest** incident has `requester_id = NULL`, a `guest_contact` phone, and a `tracking_token` — the only way
  an anonymous reporter can later check status. (A signed-in citizen's incident gets **no** token.)
- The **critical** incidents (`approved`, `accepted`) go through **coordinator approval first**, because the
  lifecycle requires it for critical priority. The seed timeline reflects that (`created → approved → accepted`).
- The **verified** incident carries a `rating` (5) + `review` + `verified_at`; **rejected** carries a
  `rejection_reason`; **cancelled** carries a `cancellation_reason` — exactly as the real transitions set them.

### 4.1 The timeline (`incident_updates`) each one produces

Every incident's history is recorded as a row per transition (this is what feeds `GET /incidents/{id}/updates`).
The seed generates them from each incident's path, with **staggered timestamps** (30 minutes apart) so the
**response-time reports** ([`../../services/monolith/app/modules/reports`](../../services/monolith/app/modules/reports)) compute realistic
averages instead of zeros. Worked example for the `verified` incident:

```text
created  → accepted  → in_progress → completed → verified
(t-5h)     (t-4.5h)     (t-4h)        (t-3.5h)     (t-3h)   ... actor at each step:
requester  Priya(owner) Priya(owner)  Priya(owner) Rajesh(requester)
```

Who performs each action in the seed: **approve/reject** → Arjun (coordinator); **accept/start/complete** → the
assigned org's owner (provider); **verify/cancel** → the requester (citizen).

---

## 5. Supporting rows (alerts, notifications, files, audit)

To make the dashboards, maps, and read-only trails non-empty, the seed also loads:

- **Alerts** (2) — a **platform-wide** "Monsoon advisory" (`area = NULL`, `info`), and an **area** "Flood warning —
  Hyderabad" (`warning`) whose `area` is a MultiPolygon box over Hyderabad (≈17.2–17.6 lat, 78.3–78.7 lng). The
  second one demonstrates the point-in-polygon filter: `GET /alerts?latitude=17.39&longitude=78.48` returns both;
  a Delhi coordinate returns only the platform-wide one.
- **Notifications** (2) for Rajesh — an unread `incident_update` ("now 'accepted'") and a read `verification`.
- **Files** (2, metadata only — the bytes would live in MinIO) — an `incident_photo` on the `accepted` incident
  (uploaded by Rajesh) and a `completion_proof` on the `completed` incident (uploaded by Priya).
- **Audit logs** (2) — `organization.verified` (Lakshmi verifying Priya Care) and `incident.approve` (Arjun),
  so the append-only trail ([`../../services/monolith/app/modules/audit`](../../services/monolith/app/modules/audit)) has real entries.

---

## 6. Per-module fixtures (Task N — testing in isolation)

This full dataset is for **running the app** and **integration** tests. For **unit / API** tests, each module must
stay independently testable, so it does **not** load the whole world. Those small, per-module fixtures live in
[`../../services/monolith/tests/factories.py`](../../services/monolith/tests/factories.py) — e.g. `make_user(role=…)`,
`auth_provider_with_org(…)`, `make_org(…)` — and each module has its own `tests/{unit,api,integration}/<module>/`.
Keep the two layers distinct: **factories** = minimal, per-test; **seed** = the rich, whole-system starter set.

---

## 7. Extending the dataset (how to add a row safely)

1. Add the row to the matching list in [`../../services/monolith/scripts/seed.py`](../../services/monolith/scripts/seed.py) (e.g. `_USERS`,
   `_ORGS`, `_INCIDENTS`).
2. Give it a **stable key** so its `sid(...)` UUID is deterministic — that is what keeps `make seed` idempotent.
3. Re-run `make seed`: existing rows are skipped, only the new one is inserted.
4. Update **this document's** tables to match (one source of truth per fact; cross-link, don't duplicate).

---

## Related

- [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §3.4 — the signed-off seed spec (the *why* and shape)
- [`50-data-model.md`](50-data-model.md) — the 13 tables + enums these rows populate; §9 (idempotent seed)
- [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) — the 8-state lifecycle
- [`70-quality-test-strategy.md`](70-quality-test-strategy.md) — fixtures vs seed; the test layers
- [`../../services/monolith/scripts/seed.py`](../../services/monolith/scripts/seed.py) — the authoritative script this doc describes
