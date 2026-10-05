# IDRM-RFC Series — Master Plan, Module Breakdown & Resumption Prompt

**Status**: 📐 PLAN (scaffolding) · **series body COMPLETE & CONSOLIDATED** — **4 core RFCs** + README + living RFC-CLARIFY
**Author**: Claude (Auto-pilot mode)
**Created**: 2026-06-30
**Applies to**: IDRM v3.0 **MVP**, evolving to the **FFP** (Full-Fledged Product — the mature, post-MVP IDRM)
**Companion**: [`docs/rfc/RFC-CLARIFY.md`](../docs/rfc/RFC-CLARIFY.md) (doubts + decisions)

> **What this file is.** A blueprint for documenting IDRM the way John T. Moy documented OSPF —
> end-to-end, from *idea/inception* to *implementation/completion* — as a **named RFC-style series**
> (mnemonic names, **not** numbers). This file is the **instructions + comprehensive prompt** so the work
> can be **paused and resumed** across sessions without losing intent. Read §8 (Resumption Prompt) to continue.

> **Naming rule (per owner, 2026-06-30):** RFCs are **named, not numbered** — `RFC-<SHORTNAME>` where the
> short name clarifies the topic. No 0000/0001 ordinals anywhere.
>
> **🔁 CONSOLIDATION (per owner, 2026-06-30): the series is now 4 core documents**, matching Moy's four OSPF
> artifacts. The six contract RFCs (vocab/authz/lifecycle/api/geo/realtime) were merged into **RFC-PROTOCOL**
> §1–§6; RFC-OPS folded into **RFC-IMPL** §8–§14; RFC-SERIES folded into **`docs/rfc/README.md`**. The
> per-RFC catalog/outlines in §2–§3 below are **historical** (they describe the pre-merge split, now the
> *sections* of those four docs). The live index, conventions, and coverage matrix are in the README.

---

## 0. Why model IDRM docs on the OSPF corpus?

John Moy produced **four complementary artifacts** for OSPF, each at a different altitude and reader.
Together they cover a protocol's entire life — *concept → contract → operations → code*. That four-layer
separation is the backbone of this plan.

### 0.1 The four Moy artifacts (researched from trusted sources)

| Moy artifact | Altitude / audience | What it nails down | IETF/normative analog |
|--------------|---------------------|--------------------|-----------------------|
| **OSPF: Anatomy of an Internet Routing Protocol** (Addison-Wesley, 1998) | *Concept & rationale* — newcomers, architects | The "why": Internet-routing context, design history, trade-offs. **5 parts** (I routing overview, II OSPF in depth). | Informational / pedagogical |
| **OSPF Version 2 — RFC 2328** (J. Moy, 1998, STD 54) | *Normative contract* — implementers | The "what MUST happen": data structures, state machines, packet formats, flooding, SPF. **§1–16 + App A–G**. Uses **RFC 2119 MUST/SHOULD/MAY**. | Standards-track (RFC 2026) |
| **OSPF MIB — RFC 1850** (Baker & Coltun) | *Management & observability* — operators/NMS | Managed objects: counters, tables, knobs, what SNMP can read/set. The "how you watch & tune it." | Standards-track MIB |
| **OSPF Complete Implementation** (Addison-Wesley, 2000) | *Reference implementation* — porters/maintainers | The "how it's coded": I/O & data flow, data structures (AVL/Patricia/timers), the routing table, link-state DB & aging, neighbor FSM, flooding, SPF, **porting**, MOSPF. | Informative companion |

**Lesson for IDRM:** keep the **normative contract**, the **management/observability surface**, the
**implementation walkthrough**, and the **conceptual narrative** in **separate, cross-referenced documents**
under **one controlling vocabulary**, with RFC-2119 precision on the contract parts. IDRM has the raw
material (FS/PRD/HLD/LLD, API & DB guides, build workflow, diagrams) spread across 43+ files in different
voices; the RFC series **re-frames and consolidates** it into the Moy four-layer shape.

### 0.2 Sources consulted (methodology only)

- RFC 2328 — *OSPF Version 2* (§1–16 + App A–G). <https://datatracker.ietf.org/doc/html/rfc2328>
- RFC 2026 — *The Internet Standards Process*. <https://datatracker.ietf.org/doc/html/rfc2026>
- RFC 2119 — *Key words to Indicate Requirement Levels* (MUST/SHOULD/MAY).
- *OSPF: Anatomy of an Internet Routing Protocol* — 5-part structure.
- *OSPF Complete Implementation* — chapter map.

---

## 1. The OSPF → IDRM crosswalk (the core idea)

We mirror Moy's **four layers** as **four tracks**, and slot IDRM's existing knowledge into them.

| Moy layer | IDRM track | IDRM "protocol" equivalent | Primary existing sources to consolidate |
|-----------|-----------|----------------------------|------------------------------------------|
| **Anatomy** (concept) | **D — Narrative** | Why disaster-relief coordination; "Uber for relief"; monolith/Bun/conda rationale; decision history | `README.md`, `CLAUDE.md`, `IDRM-ARCHITECTURE-GUIDE.md`, `IDRM-PRD.md`, `IDRM-PROJECT-STATUS.md` (D1–D17) |
| **RFC 2328** (contract) | **A — Normative spec** | Service-request **lifecycle state machine**, role/permission matrix, enum vocabulary, API & auth contract, privacy | `IDRM-FS.md` (§3.3 matrix, §6.1 FSM), `COMPLETE-API-SPECS-GUIDE.md`, `instructions_json_formats_v3.md`, `dbmodels/enums.py` |
| **RFC 1850** (MIB) | **B — Management/observability** | Analytics objects, audit-log records, notification objects, rate-limit counters, health/readiness, metrics | API §Analytics, `COMPLETE-MONITORING-GUIDE.md`, `IDRM-Redis-Operations.md`, audit model |
| **Complete Implementation** | **C — Reference implementation** | M0–M6 backend, G1–G4 gateway, F0–F6 web-html, React Part D; PostGIS; Redis pub/sub; data structures | `IDRM-LLD.md`, `IDRM-HLD.md`, `IDRM-BUILD-WORKFLOW.md`, `IDRM-Database-Query-Reference.md`, live `src/` |

**The "routing protocol" of IDRM** is the **service-request lifecycle**:
`SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED`
(+ terminal `REJECTED / CANCELLED / EXPIRED`, and `DISPUTED` re-entry). This is to IDRM what the
neighbor/interface FSM + flooding is to OSPF — it gets its own RFC (**RFC-LIFECYCLE**) with a formal state
table, guards, actors, and request-payload format, exactly like RFC 2328 §10 (neighbor FSM).

---

## 2. The IDRM-RFC catalog (the deliverable set)

Twelve named documents. Home: **`docs/rfc/`**. Each cross-referenced and governed by the shared vocabulary
in **RFC-VOCAB**. Track letter shows the Moy layer. **Build order** is in §4.

| RFC (name) | Title | Track | One-line scope | Primary feeder docs |
|------------|-------|-------|----------------|---------------------|
| **RFC-SERIES** | The IDRM-RFC Series — Process, Conventions & Index | meta | How the series works: naming, RFC-2119 usage, template, status levels, index | this plan; RFC 2026/2119 |
| **RFC-ARCH** | Architecture & Conceptual Overview ("Anatomy") | D | The why, the domain, the metaphor, the 3-frontend monolith, decision history (D1–D17) | README, CLAUDE, ARCHITECTURE-GUIDE, PRD, PROJECT-STATUS |
| **RFC-VOCAB** | Domain Vocabulary & Normative Enumerations | A | The controlling glossary: roles, service types, priorities, statuses, privacy, languages, channels | `dbmodels/enums.py`, CLAUDE, FS §3, json_formats |
| **RFC-AUTHZ** | Identity, Roles & Authorization | A | 10 roles + Public tier; registration vs granted roles; the §3.3 permission matrix as a normative table | FS §3.3, API §RBAC, CLAUDE |
| **RFC-LIFECYCLE** ⭐ | Service-Request Lifecycle State Machine | A | **The core protocol.** States, transitions, guards, actor per action, auto-approve, dispute, payload | FS §6.1, Service-Management diagram, API guide, `service_service.py` |
| **RFC-API** | API Contract & Transport | A | GET/POST-only, `/api/v1`, action sub-endpoints, envelopes, error model, tokens (15m/7d), pagination | COMPLETE-API-SPECS-GUIDE, json_formats, CLAUDE |
| **RFC-GEO** | Geospatial Subsystem | A+C | GeoJSON `[lon,lat]`, `/geo/nearby` & `/geo/cluster`, PostGIS (`ST_DWithin`, `ST_ClusterKMeans`), SRID 4326 | DB Query Reference §Spatial, FS, M4 |
| **RFC-REALTIME** | Real-time, Notifications & Pub/Sub | A+C | WebSocket subscribe protocol, channels, event types, notification objects, Redis pub/sub bridge | API §WebSocket/§Notifications, Redis-Operations, M5/G4 |
| **RFC-MGMT** | Management, Observability & Analytics ("MIB") | B | Managed objects: dashboard metrics, audit-log records, health/readiness, rate-limit counters, SLOs (D11) | API §Analytics, MONITORING-GUIDE, Redis-Operations, audit model |
| **RFC-IMPL** | Reference Implementation Walkthrough | C | How the contract is realized: M0–M6 / G1–G4 / F0–F6 / React Part D; data flow; module-by-module | BUILD-WORKFLOW, LLD, HLD, live `src/` |
| **RFC-OPS** | Deployment, Environments & Operations | C | Ubuntu target, ports/firewall, dev/staging/prod, Docker, migrations, Windows-authoring caveat | UBUNTU-PORTS, DEPLOYMENT-GUIDE, DevSecOps, SETUP |
| **RFC-CLARIFY** | Clarifications, Open Questions & Recommended Path | meta | The doubts log + auto-pilot decisions + product-owner sign-offs (the user-requested doc) | PROJECT-STATUS §6, doc-reconciliation memory |

**Reserved for FFP** (authored when each module is built): `RFC-FINANCE`, `RFC-CHATBOT`, `RFC-MOBILE`,
`RFC-MAD`, `RFC-MICRO` (microservices migration). Until then, FFP scope lives inside the RFCs above as
`[FFP]` / `[MVP→FFP]` tags (see §7).

> RFC-CLARIFY is **living** — the audit trail of every judgment call made while writing the rest.

---

## 3. Per-RFC outline (what goes inside each)

Each follows the **standard template** in §5. Below is the section skeleton unique to each.

**RFC-SERIES (meta):** 1 Purpose & scope · 2 How to read the series · 3 Naming & status levels
(DRAFT/REVIEW/STABLE) · 4 RFC-2119 normative-language policy · 5 Document template · 6 Vocabulary authority
(→ RFC-VOCAB) · 7 The OSPF lineage (crosswalk) · 8 Full index w/ status · 9 Change process · App: glossary.

**RFC-ARCH (Anatomy/D):** 1 The disaster-response problem (India, 2-district pilot) · 2 The solution
metaphor & request journey · 3 Three frontends, one monolith — and why · 4 Technology decisions & rejected
alternatives (Bun≠Node, conda≠venv, PostGIS≠GeoServer, monolith≠microservices) · 5 Scope: MVP vs FFP
(Finance/Chatbot/Mobile/MAD) · 6 Decision history (D1–D17, dated) · 7 Forward map to the rest of the series.

**RFC-VOCAB (Vocabulary/A):** 1 Conventions (UPPERCASE, CHECK-enforced; the lowercase exceptions) · 2 Roles
(11 tiers) · 3 Service types (6) · 4 Priority (4) · 5 Statuses (10) · 6 Privacy (3) · 7 Org types (4) · 8
Languages (3) · 9 Notification type/channel/status · 10 Audit resource types (CamelCase) · 11 WebSocket event
tokens · 12 Reserved/Post-MVP values · App: the master enum table (the single source all other RFCs cite).

**RFC-AUTHZ (AuthZ/A):** 1 Role taxonomy & hierarchy (Public … ADMIN) · 2 Self-assignable vs granted roles ·
3 Role-grant endpoint contract · 4 **The permission matrix** (normative, FS §3.3) · 5 Privacy interaction
(who sees PROTECTED contact) · 6 Guest/OTP quick-start (D9, deferred) · 7 Worked authorization examples.

**RFC-LIFECYCLE (Lifecycle/A) — flagship:** 1 Overview (the IDRM "protocol") · 2 State definitions · 3
**Transition table** (from→to, trigger endpoint, actor role, guard) · 4 Auto-approve rule (CRITICAL/HIGH,
D5) · 5 Dispute sub-protocol · 6 Terminal states & expiry · 7 Request payload format (the "packet") · 8
Notifications emitted per transition · 9 Sequence diagrams · App: full state diagram + invariants.

**RFC-API (API/A):** 1 Transport & base URLs · 2 HTTP-method policy (GET/POST only; why) · 3 Auth: tokens,
refresh, Bearer/cookie · 4 Action sub-endpoint convention · 5 Response envelopes & pagination · 6 Error model
& codes · 7 Versioning · App: endpoint index (the ~37).

**RFC-GEO (Geo/A+C):** 1 Coordinate convention (`[lon,lat]`, SRID 4326) · 2 `/geo/nearby` · 3 `/geo/cluster`
· 4 PostGIS realization · 5 Privacy & live-only filtering · 6 Edge cases (radius clamp, bad bounds).

**RFC-REALTIME (Realtime/A+C):** 1 WebSocket endpoint & handshake · 2 Subscribe protocol & channels · 3 Event
types · 4 Notification object & lifecycle · 5 Redis pub/sub bridge · 6 Delivery guarantees & reconnection.

**RFC-MGMT (MIB/B):** 1 Managed-object model · 2 Dashboard metrics object · 3 Audit-log record schema · 4
Health & readiness · 5 Rate-limit counters & headers · 6 Cache keys & TTLs · 7 SLO/target table (D11) · 8
What is *not* yet observable (gaps).

**RFC-IMPL (Impl/C):** 1 Implementation architecture & data flow · 2 Backend M0–M6 · 3 Gateway G1–G4 · 4
Frontend F0–F6 + React Part D · 5 Key data structures & patterns · 6 Verification status · 7 Porting notes.

**RFC-OPS (Ops/C):** 1 Target platform (Ubuntu) & the Windows-authoring caveat · 2 Ports & firewall · 3
Dev/staging/prod on one host · 4 Docker Compose & images · 5 DB init & Alembic · 6 Secrets & production
guard · 7 Runbook & health checks.

**RFC-CLARIFY (meta):** see companion file — kept living.

---

## 4. Execution module breakdown (how to build the series, resumably)

Order is dependency-driven: vocabulary and the index first, then the contract, then management, then code,
then ops, with the narrative early for orientation.

| Phase | Produces | Depends on | Done when |
|-------|----------|------------|-----------|
| **P0 (done)** | this plan + RFC-CLARIFY seed + `docs/rfc/README.md` | corpus survey + OSPF research | plan emitted & reviewable |
| **P1 (this session)** | **RFC-SERIES** (template + index) | P0 | template & index frozen |
| **P1 (this session)** | **RFC-VOCAB** (vocabulary) | RFC-SERIES | every enum has one normative home |
| **P2 (this session)** | **RFC-ARCH** (anatomy) | RFC-VOCAB | decision history D1–D17 captured |
| P2 | **RFC-AUTHZ** | RFC-VOCAB | permission matrix is normative |
| P3 | **RFC-LIFECYCLE** ⭐ | RFC-VOCAB, RFC-AUTHZ | state table + invariants complete |
| P3 | **RFC-API** | RFC-VOCAB, RFC-LIFECYCLE | endpoint index reconciled to code |
| P4 | **RFC-GEO** | RFC-API | PostGIS contracts match `geo_service.py` |
| P4 | **RFC-REALTIME** | RFC-API | WS/pub-sub contract matches G4/M5 |
| P5 | **RFC-MGMT** | RFC-LIFECYCLE, RFC-API | managed objects + SLOs tabled |
| P5 | **RFC-IMPL** | RFC-GEO, RFC-REALTIME | M/G/F walkthrough matches `src/` |
| P6 | **RFC-OPS** | RFC-IMPL | dev/staging/prod runbook complete |
| P6 | finalize **RFC-CLARIFY** | all | every open question has a recommended path |

**Resumption granularity:** one RFC = one resumable unit. After each, update the index in RFC-SERIES and
the status table here/in README, then stop cleanly. A session can safely do 1–3 RFCs.

---

## 5. The RFC document template (every content RFC follows this)

```
# RFC-<SHORTNAME>: <Title>

| Field      | Value                                              |
|------------|----------------------------------------------------|
| RFC        | RFC-<SHORTNAME>                                    |
| Track      | A (normative) / B (mgmt) / C (impl) / D (narrative) / meta |
| Status     | DRAFT / REVIEW / STABLE                             |
| Requires   | <other RFCs this relies on normatively>            |
| Updates    | <RFCs/sections this supersedes>                    |
| Source docs| <existing repo files consolidated here>            |
| Created / Updated | <dates>                                     |

## Abstract           — 3–5 sentences: what & why
## 1. Introduction    — scope, audience, non-goals, normative-language note
## 2..N. Body         — per-RFC skeleton from §3
## Appendix A. <ref tables / diagrams>
## Appendix Z. Changes & open items (links to RFC-CLARIFY)
```

**Normative-language rule (RFC-2119):** Tracks A/B use **MUST / MUST NOT / SHOULD / SHOULD NOT / MAY** in the
precise RFC-2119 sense, called out in each intro. Tracks C/D are **informative**. Every enum value links back
to **RFC-VOCAB**. **Scope tags** `[MVP]` / `[FFP]` / `[MVP→FFP]` on every feature/clause (see §7).

---

## 6. Validation, closure & completeness criteria

Before any RFC is marked **STABLE**, it MUST pass:

1. **Vocabulary check** — every enum/role/status used appears in RFC-VOCAB with identical UPPERCASE spelling.
2. **Source-trace check** — every normative claim traces to a feeder doc *or* the live `src/`; on doc-vs-code
   conflict, **code wins** and the discrepancy is logged in RFC-CLARIFY.
3. **Cross-reference check** — all `Requires:` links resolve; no dangling RFC references.
4. **Coverage check** — the RFC's §3 skeleton sections are all present (no TODO stubs in STABLE).
5. **Decision-consistency check** — nothing contradicts D1–D17 in `IDRM-PROJECT-STATUS.md` without an
   explicit, dated override in RFC-CLARIFY.

**Series-level closure** = all twelve STABLE, RFC-CLARIFY has a recommended path for every open question, and
RFC-SERIES's index is green.

---

## 7. FFP — the MVP → Full-Fledged-Product evolution path

**FFP = Full-Fledged Product** — the mature, post-MVP IDRM, **same domain scaled up**, not a separate project.
It absorbs today's growth targets and Post-MVP modules: Finance/Donations, AI Chatbot, native mobile
(React Native/Expo), the MAD module, the `EXECUTIVE` role + `AUDITOR` credibility/expense scoring, pan-India /
100k-MAU scale, 12+ languages, and the eventual microservices migration
(`archive/MIGRATION-TO-MICROSERVICES-v3.md`).

The series is built so the **same RFCs grow with the product** rather than being cloned:

1. **Scope tags, not forks.** Every RFC marks each clause **`[MVP]`** / **`[FFP]`** / **`[MVP→FFP]`**. The
   naming stays single and continuous; FFP is a **maturity axis inside each doc**, mirroring how RFC 2328
   marked optional/extension behavior (Demand Circuits, MOSPF) rather than spawning a new spec.
2. **New modules get new named RFCs, appended.** When an FFP module lands it gets its own RFC in the same
   series: `RFC-FINANCE`, `RFC-CHATBOT`, `RFC-MOBILE`, `RFC-MAD`, `RFC-MICRO` — governed by the same
   RFC-SERIES template and RFC-VOCAB vocabulary.
3. **Contract stability.** Track-A RFCs (RFC-VOCAB … RFC-REALTIME) define the MVP contract precisely so FFP
   extends it **without breaking** existing MUST clauses — FFP additions are `SHOULD`/`MAY` until promoted.

**➡️ Path now:** write the twelve MVP RFCs with scope tags throughout so the FFP delta is visible. Author the
FFP-only module RFCs when those modules are built. See RFC-CLARIFY **S4** (resolved).

---

## 8. 🔁 Comprehensive Resumption Prompt (paste this to continue in a fresh session)

> **Context:** You are continuing the **IDRM-RFC documentation series** — an OSPF/Moy-style suite that
> documents IDRM end-to-end (concept → contract → management → implementation → ops), modeled on John Moy's
> four OSPF artifacts (Anatomy book = narrative; RFC 2328 = normative contract; RFC 1850 MIB = management;
> OSPF Complete Implementation = code walkthrough). RFCs are **named, not numbered** (`RFC-<SHORTNAME>`). The
> full plan, crosswalk, catalog, per-RFC outlines, execution order, template, and validation criteria are in
> **`instructions/IDRM-RFC-SERIES-PLAN.md`** — read it first. Then **`docs/rfc/README.md`** (live index +
> conventions + coverage) and **`docs/rfc/RFC-CLARIFY.md`** (living doubts log).
>
> **The series is COMPLETE and consolidated into 4 core docs:** **RFC-ARCH** (concept), **RFC-PROTOCOL** (the
> normative contract — §1 vocab · §2 authz · §3 lifecycle ⭐ · §4 API · §5 geo · §6 real-time), **RFC-MGMT**
> (MIB), **RFC-IMPL** (code + ops), plus living **RFC-CLARIFY**.
>
> **Remaining work (in priority order):** (1) run the README §"Validation gate" checks and promote the four
> core RFCs REVIEW→STABLE; (2) obtain product-owner answers to RFC-CLARIFY **S1–S5** and fold them in; (3)
> author an **FFP** module RFC (`RFC-FINANCE`/`RFC-CHATBOT`/`RFC-MOBILE`/`RFC-MAD`/`RFC-MICRO`) **only when
> that module is actually built**. Do NOT re-split RFC-PROTOCOL.
>
> **Rules:**
> 1. **Consolidate, don't invent.** Each RFC re-frames the existing feeder docs named in §2/§3 into the Moy
>    layer. Pull facts from those files and from the live `src/` tree.
> 2. **Single vocabulary.** All enums/roles/statuses come from **RFC-VOCAB** (UPPERCASE, CHECK-enforced;
>    lowercase exceptions = languages + WS event tokens + CamelCase audit types).
> 3. **Normative precision.** Tracks A/B use RFC-2119 MUST/SHOULD/MAY; Tracks C/D are informative. State which
>    in each intro.
> 4. **Code wins on conflict.** Where a doc and `src/` disagree, follow the code and log it in RFC-CLARIFY.
>    Honor locked decisions D1–D17 in `schedules/IDRM-PROJECT-STATUS.md`.
> 5. **Validate before STABLE.** Run the §6 checks. New judgment calls → append to RFC-CLARIFY.
> 6. **Update the index.** After each RFC, update RFC-SERIES's index, `docs/rfc/README.md`, and the §4 status
>    table in the plan.
> 7. **Do not build/run on Windows.** Authoring box; verification happens on Ubuntu. Documentation only here.
> 8. **Tag scope MVP vs FFP.** Mark each clause `[MVP]` / `[FFP]` / `[MVP→FFP]` (plan §7). FFP-only modules
>    become their own named RFCs (`RFC-FINANCE`, etc.) only when built.
>
> **The flagship is RFC-PROTOCOL §3** (service-request lifecycle state machine) — the IDRM analog of OSPF's
> neighbor FSM. It is grounded in `src/backend/app-python/services/service_service.py` + FS §6.1; keep it the
> most rigorous section.
>
> Begin by stating what you will do this session (validate-to-STABLE, fold an S-answer, or author an FFP RFC),
> then proceed.

---

## 9. Progress log

- **P0** — `instructions/IDRM-RFC-SERIES-PLAN.md` (this file), `docs/rfc/RFC-CLARIFY.md`, `docs/rfc/README.md`.
- **P1–P2 (2026-06-30)** — **RFC-SERIES** (definition + frozen template + index), **RFC-VOCAB** (grounded in
  `dbmodels/enums.py`), **RFC-ARCH** (anatomy/narrative). Switched the series from numbers to mnemonic names.
- **P3–P6 (2026-06-30, same session)** — **RFC-AUTHZ** (FS §3.3 matrix + `security.py`), **RFC-LIFECYCLE** ⭐
  (transition table from `service_service.py`), **RFC-API** (endpoint index from the routers), **RFC-GEO**,
  **RFC-REALTIME**, **RFC-MGMT** (the MIB), **RFC-IMPL**, **RFC-OPS** — all grounded in the live `src/` code.
  Finalized **RFC-CLARIFY** with §2b code-grounded findings (C-VOCAB-1, C-AUTHZ-1/2, C-LIFE-1/2, C-RT-1,
  C-MGMT-1/2, C-OPS-1/2) and resolved C6/C9/C10/C12.
- **Consolidation (2026-06-30, owner: "reduce the doc count").** Reduced 12 → **4 core docs** to match Moy's
  four artifacts: merged the six contract RFCs into **RFC-PROTOCOL §1–§6**, folded RFC-OPS into **RFC-IMPL
  §8–§14**, folded RFC-SERIES into **README**. Ran a coverage audit of the non-RFC repo (added to README) —
  surfaced **C-COV-1** (no `disaster_event` entity behind the "manage disaster events" permission).
- **Series body is complete.** Remaining: the **STABLE-promotion gate** + **product-owner sign-off** on
  RFC-CLARIFY **S1–S5**. FFP module RFCs authored when those modules are built.
