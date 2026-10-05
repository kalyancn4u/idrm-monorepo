# IDRM FFP — Module Elucidation (delta: how each module evolves)

> *Type: Document (elucidation / synthesis · DELTA on the MVP) · Audience: novices → architects · Status: FFP — trigger-gated*
> *The FFP counterpart of [`../idrm-mvp-docs/25-module-elucidation.md`](../idrm-mvp-docs/25-module-elucidation.md). It does **not** repeat the
> MVP explanation — it states, per module, **what changes in the FFP and on what trigger**. Its normative twin is
> [`26-conformance-pics.md`](26-conformance-pics.md). Nothing here alters the frozen `/api/v1` contract — the FFP only
> **adds**. Grown document-wise from the `_removed` cleanup (see [`../_removed/_CLEANUP-LEDGER.md`](../_removed/_CLEANUP-LEDGER.md)).*

---

## How to read this

Same ten modules as the MVP. For each: **Trigger** (what justifies the change) · **Delta** (what is added or
extracted) · **Contract** (why callers don't break). The MVP behaviour is the baseline; read
[`../idrm-mvp-docs/25-module-elucidation.md`](../idrm-mvp-docs/25-module-elucidation.md) first.

---

## INC — Incidents (delta)
<!-- IDRM-ELUCID src=v0-10§4.4 src=v0-10§3.2 -->

**Trigger.** Incident volume/coupling grows enough that the module needs independent scaling, ownership, or
richer workflow than the monolith should carry.

**Delta.**
- **Lifecycle extends:** add `disputed` and **auto-close** (the two states deliberately deferred from the MVP's
  lean 8-state model) with the evidence/appeal rules behind them.
- **Extraction (Strangler Fig):** incidents may become their own **microservice** behind **APISIX**, still on the
  same paths — extracted when a concrete trigger fires (it is *not* the least-coupled module, so it is a later
  extraction; auth goes first). See [`20-architecture-system.md`](20-architecture-system.md).
- **Events:** state transitions emit **versioned domain events** (outbox → broker → projections) for real-time
  push and analytics — see [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) §3.
- **Deep real-time:** live incident updates to web/mobile clients via the messaging tier.

**Contract.** The public incident endpoints keep their `/api/v1` paths and shapes; new capability arrives as
**added** fields/endpoints and events, never renames. → [`40-api-specification.md`](40-api-specification.md).

**Deep-dive:** [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) (trigger per capability) ·
conformance → [`26-conformance-pics.md`](26-conformance-pics.md) `PICS-INC-*` (phase FFP).

---

## USR — Users (delta)
<!-- IDRM-ELUCID src=v0-20§3.2 src=v0-20§6.2 -->

**Trigger.** The **first** extraction (auth is least-coupled) — done early, as the pattern-setter for Strangler Fig.
**Delta.** Auth becomes its **own microservice** behind APISIX; adds **OIDC/SSO, MFA, ABAC**, the full role
hierarchy + **Auditor** role; token introspection at the gateway.
**Contract.** Same login/refresh/`/api/v1` surfaces; new factors/claims are *added*, not renamed. → [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).

---

## LOC — Locations (delta)
<!-- IDRM-ELUCID src=v0-20§3.4 -->

**Trigger.** Heavy geoprocessing (routing, isochrones, large overlays) outgrows in-DB queries.
**Delta.** A dedicated **Python GeoPandas/Shapely** geospatial service over PostGIS (**not** Java GeoServer); adds
the disaster-event entity + live **Common Operational Picture**.
**Contract.** Basic proximity/geofence stay in the API unchanged; advanced ops arrive as added endpoints. → [`20-architecture-system.md`](20-architecture-system.md) §6.2.

---

## NTF — Notifications (delta)
<!-- IDRM-ELUCID src=v0-20§3.5 -->

**Trigger.** Need for **deep real-time** delivery and multi-channel reach at scale.
**Delta.** Broker-backed push (websockets/SSE via edge services + **RabbitMQ/Kafka** + workers); multi-channel
intake/out (SMS/email/push). Driven by the incident **domain events**.
**Contract.** In-app notifications keep working; new channels are additive. → [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md).

---

## The remaining six modules — concise deltas (full rows in [`26`](26-conformance-pics.md))

- **RES — Resources.** AI-assisted matching; per-service ownership of resource data.
- **ALR — Alerts.** Multi-channel intake/broadcast; event-driven fan-out at scale.
- **RPT — Reports.** Advanced analytics, dashboards, DORA/ops metrics.
- **FIL — Files.** Distributed MinIO / cloud S3; **FaceNet recognition** (consent-gated, ADR-011 / FFP-ADR-014, DPDP).
- **AUD — Audit.** Cross-service audit aggregation; Auditor role; zero-trust.
- **ADM — Administration.** Per-request privacy levels (Public/Protected/Private), national rollout, full localization.

> ✅ **All ten modules now have an FFP delta** (USR/LOC/NTF detailed above; the six here as concise deltas); the
> normative rows live in [`26-conformance-pics.md`](26-conformance-pics.md).

---

*Related:* MVP baseline [`../idrm-mvp-docs/25-module-elucidation.md`](../idrm-mvp-docs/25-module-elucidation.md) ·
[`20-architecture-system.md`](20-architecture-system.md) · [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) ·
conformance [`26-conformance-pics.md`](26-conformance-pics.md).
