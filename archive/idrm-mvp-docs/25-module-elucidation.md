# IDRM MVP — Module Elucidation (the what/why/how of each module)

> *Type: Document (elucidation / synthesis) · Audience: complete novices → engineers · Status: MVP — current*
> *The **module** companion to the component map in [`../idrm-mvp-guides/learn/tech-stack-101.md`](../idrm-mvp-guides/learn/tech-stack-101.md).
> Where tech-stack-101 explains each **technology**, this explains each **module** of the monolith: what it is, why
> it exists, and how it works — in plain language, then linked to the deep spec. Its normative twin is the
> conformance checklist [`26-conformance-pics.md`](26-conformance-pics.md). Grown document-wise from the `_removed`
> cleanup (see [`../_removed/_CLEANUP-LEDGER.md`](../_removed/_CLEANUP-LEDGER.md)).*

---

## How to read this

IDRM's MVP is a **modular monolith** — one deployable FastAPI app with **ten modules** (ten rooms in one house).
Each module repeats the same internal skeleton (`router → schemas → service → repository → models`, see
[`../instructions/domain.md`](../instructions/domain.md) §2). For each module below:
**What** (one sentence) · **Why** (the reason it exists) · **How** (the moving parts) · **Deep-dive** (links).

Modules: **USR** users · **INC** incidents · **RES** resources · **LOC** locations · **ALR** alerts ·
**NTF** notifications · **RPT** reports · **FIL** files · **AUD** audit · **ADM** administration.

---

## INC — Incidents (the heart of the system)
<!-- IDRM-ELUCID src=v0-10§4.4 src=v0-10§4.5 -->

**What.** An **incident** is a citizen's *help request* — the single most important object in IDRM. (Naming
bridge: users see "help request"; the API and database call it an `incident`.)

**Why.** Everything else exists to serve incidents: a citizen raises one, a provider fulfils it, a coordinator
oversees it, and the audit trail records it. If you understand incidents, you understand IDRM's core loop —
**sense → route → record**.

**How.**
- **Shape:** `service_type` (medical / food / rescue / water / shelter / other) · `priority` (low / medium /
  high / critical) · `location` (a PostGIS point) · `description` · reporter (a citizen).
- **Lifecycle (locked, 8 states):** `created → (approved, if critical) → accepted → in_progress → completed →
  verified`, plus `cancelled` / `rejected`. Each transition is guarded by role + current-state rules. *(FFP adds
  `disputed` + auto-close — see the FFP module doc.)*
- **Who may do what (RBAC):** a **citizen** creates/cancels their own; a **provider** accepts and progresses; a
  **coordinator/admin** approves critical ones, verifies completion, and can reject. Enforced per the role→API
  matrix in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).
- **Where it lives:** the `incidents` module (router/service/repository) over the `incidents` table in
  [`50-data-model.md`](50-data-model.md); the API contract is in [`40-api-specification.md`](40-api-specification.md).
- **ReVV (Review, Verification & Validation):** completion is *proven* (a provider marks `completed` with proof;
  a coordinator moves it to `verified`) — this is IDRM's accountability spine, not a separate module.

**Deep-dive:** lifecycle & acceptance → [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) ·
data path → [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) ·
guide → [`../idrm-mvp-guides/learn/incident-management-101.md`](../idrm-mvp-guides/learn/incident-management-101.md) ·
conformance → [`26-conformance-pics.md`](26-conformance-pics.md) `PICS-INC-*`.

---

## USR — Users (identity & access)
<!-- IDRM-ELUCID src=v0-20§3.2 src=v0-20§6.2 src=v0-20§6.3 -->

**What.** Accounts, the four roles (**citizen · provider · coordinator/admin**) + a narrow **guest** path, and the
rules for who may do what.

**Why.** Every meaningful action must be *authorized*, and disaster data is sensitive (DPDP Act 2023), so identity
is foundational. USR is also the **least-coupled** module — which is why it is the FFP's **first** extraction.

**How.**
- **Authentication:** **RS256 JWT** — a short-lived access token (~60 min) + a **rotating, revocable** refresh
  token (~7 d). Passwords hashed with **bcrypt** (cost 12); NIST-aligned policy (**length beats composition**);
  **5-attempt / 15-min lockout**. **Sessions live in PostgreSQL** (no Redis in the MVP).
- **Authorization (RBAC):** permissions attach to a **role**, enforced by a **role→operation matrix** on every
  endpoint (e.g. only a coordinator may `verify`).
- *Deferred to FFP:* OIDC/SSO, MFA, ABAC, the full role hierarchy + Auditor.

**Deep-dive:** [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) ·
[`../idrm-mvp-guides/learn/iam-101.md`](../idrm-mvp-guides/learn/iam-101.md) · [`../idrm-mvp-guides/learn/rbac-abac-101.md`](../idrm-mvp-guides/learn/rbac-abac-101.md) ·
conformance `PICS-USR-*`.

---

## LOC — Locations (the geography layer)
<!-- IDRM-ELUCID src=v0-20§3.4 -->

**What.** The places attached to incidents and resources, and the spatial queries over them ("what is near me?",
"is this inside the affected area?").

**Why.** IDRM is **map-driven** — matching a help request to the nearest capable provider is fundamentally a
*spatial* question, and it must be fast and correct during an emergency.

**How.**
- **PostGIS** geometry/geography columns; **SRID 4326** (GPS lat/long) on every location; a **GiST** spatial index
  makes proximity fast at scale.
- Proximity via `ST_DWithin` (e.g. providers within 10 km); geofence via point-in-polygon — **computed inside the
  database** (no separate GIS server in the MVP), then drawn on the web map with **Leaflet**.
- *Deferred to FFP:* a dedicated **Python GeoPandas/Shapely** geospatial service; COP / disaster-event entity.

**Deep-dive:** [`50-data-model.md`](50-data-model.md) · [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md) ·
[`../idrm-mvp-guides/learn/gis-for-emergency-response.md`](../idrm-mvp-guides/learn/gis-for-emergency-response.md) · conformance `PICS-LOC-*`.

---

## NTF — Notifications (keeping people informed)
<!-- IDRM-ELUCID src=v0-20§3.5 -->

**What.** Messages that tell the right people about incident events — a provider that a request was assigned, a
citizen that help is on the way, a coordinator that verification is due.

**Why.** Coordination collapses without timely awareness; notifications are how the *sense → route → record* loop
stays visible to the humans in it.

**How.**
- Generated on **incident lifecycle transitions** (created / approved / accepted / completed / verified), tied to
  the audit trail. Delivery is **in-app / near-real-time** in the MVP (light polling/push) — **no message broker**.
- *Deferred to FFP:* deep real-time push (websockets + brokers/workers), multi-channel (SMS/email) intake/out.

**Deep-dive:** [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) ·
[`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md) · FFP → [`../idrm-ffp-docs/25-module-elucidation.md`](../idrm-ffp-docs/25-module-elucidation.md) · conformance `PICS-NTF-*`.

---

## RES — Resources (what responders can offer)
<!-- IDRM-ELUCID src=v0-50§5.2 -->

**What.** The supplies, capacity, and skills a **provider** (NGO / hospital / volunteer) can bring to bear — plus
the provider organisations themselves.

**Why.** Matching a help request to the *right* responder is the other half of the core loop; resources make
"who can help, with what, where" concrete and searchable.

**How.**
- Resource records are **owned by providers** and typed to a `service_type` (medical / food / rescue / …), tagged
  with a **location** (via LOC) and an availability/status.
- **Matching (MVP):** rule- and geography-based — the nearest capable, available provider for an incident
  (PostGIS proximity). *AI-assisted matching is FFP.*

**Deep-dive:** [`50-data-model.md`](50-data-model.md) · [`../idrm-mvp-guides/learn/resource-management-101.md`](../idrm-mvp-guides/learn/resource-management-101.md) · conformance `PICS-RES-*`.

---

## FIL — Files (evidence & proof)
<!-- IDRM-ELUCID src=v0-50§5.7 -->

**What.** Uploaded media — incident photos, completion proof, provider documents.

**Why.** Accountability (ReVV) needs **proof**, and a citizen's photo conveys need faster and more credibly than
text during a crisis.

**How.**
- Stored in **MinIO** (S3-compatible); the **database stores only the key/URL, never the blob** (ADR-007).
- **Media rules:** files ≤ 10 MB (PDFs ≤ ~1.5 MB/page), photos resized ≤ 1920 px (≥ 640×480), blur-checked,
  **EXIF/GPS stripped**; an emergency "lite" path allows one ≤ ~500 KB photo.
- **Face DETECTION-only** quality gate — nothing biometric is stored. *FaceNet recognition/matching is FFP
  (DPDP Act 2023 consent).*

**Deep-dive:** ADR-007 in [`21-architecture-decisions.md`](21-architecture-decisions.md) · [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) (upload security) · conformance `PICS-FIL-*`.

---

## AUD — Audit (the accountability record)
<!-- IDRM-ELUCID src=v0-50§5.8 -->

**What.** A tamper-evident record of **who did what, when** — every incident transition, auth event, and admin
action.

**Why.** Disaster response demands accountability and transparency; disputes need evidence; DPDP compliance
requires it. Audit is IDRM's memory.

**How.**
- **Append-only** entries written by services on significant actions (never updated/deleted in place); each ties
  an actor (user) to an action on a resource, with a timestamp.
- Queryable by coordinators/admin. *Analytics/BI over the audit stream is FFP.*

**Deep-dive:** [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · [`50-data-model.md`](50-data-model.md) · conformance `PICS-AUD-*`.

---

## ADM — Administration (the control plane)
<!-- IDRM-ELUCID src=v0-50§5.3 -->

**What.** Reference/lookup data (disaster types, service categories), user & role administration, and system
configuration.

**Why.** Someone must configure the *domain* (which disaster types are active, which enum values exist) and manage
users/roles — keeping operational data consistent and correct.

**How.**
- **Admin-only** endpoints (guarded by RBAC) manage reference data and the **disaster-type configuration** that
  grounds incidents.
- *Deferred to FFP:* the disaster-**event** entity, per-request **privacy levels** (Public/Protected/Private),
  national rollout, full localization.

**Deep-dive:** [`90-governance-and-raci.md`](90-governance-and-raci.md) · [`../instructions/domain.md`](../instructions/domain.md) · conformance `PICS-ADM-*`.

---

## ALR — Alerts (proactive, area-scoped warnings)
<!-- IDRM-ELUCID src=v0-40§dis -->

**What.** Hazard/area advisories broadcast *to* users in an affected zone — a flood warning, an evacuation notice
— as opposed to notifications, which are *reactions* to a specific incident.

**Why.** Not every message is incident-specific; sometimes a coordinator must warn a whole area **proactively**.
Alerts are the platform's outbound, area-scoped voice.

**How.**
- A **coordinator/admin** issues an alert scoped to a **geographic area** (a LOC polygon) with a severity; users
  within that area receive it. MVP delivery is **basic in-app / area broadcast**.
- *Deferred to FFP:* multi-channel (SMS/email/push) and event-driven fan-out at scale.

**Deep-dive:** [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md) · [`../idrm-mvp-guides/learn/emergency-communications-101.md`](../idrm-mvp-guides/learn/emergency-communications-101.md) · conformance `PICS-ALR-*`.

---

## RPT — Reports (the operational picture)
<!-- IDRM-ELUCID src=v0-40§ana -->

**What.** Operational reporting and exports — counts and summaries such as incidents by status/type/area,
resolution and verification rates, activity over time.

**Why.** Coordinators and governance must *see* how the response is going and **evidence outcomes**; reports over
the live data + audit trail are how accountability becomes visible.

**How.**
- MVP = **essential operational reports/exports** built directly from the live tables + the audit trail (no
  separate analytics store).
- *Deferred to FFP:* advanced analytics, dashboards/BI, and DORA/ops metrics.

**Deep-dive:** [`90-governance-and-raci.md`](90-governance-and-raci.md) · [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) · conformance `PICS-RPT-*`.

---

> ✅ **All ten modules are now elucidated** (INC · USR · LOC · NTF · RES · FIL · AUD · ADM · ALR · RPT). Later
> passes deepen worked examples and add code/test evidence as the MVP is built.

---

*Related:* [`20-architecture-system.md`](20-architecture-system.md) · [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) ·
component map [`../idrm-mvp-guides/learn/tech-stack-101.md`](../idrm-mvp-guides/learn/tech-stack-101.md) ·
conformance [`26-conformance-pics.md`](26-conformance-pics.md) · builder's roadmap [`27-implementation-roadmap.md`](27-implementation-roadmap.md) · FFP delta [`../idrm-ffp-docs/25-module-elucidation.md`](../idrm-ffp-docs/25-module-elucidation.md).
