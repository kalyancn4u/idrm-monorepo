# Documentation Review & Improvement Backlog

> **Part of:** IDRM Documentation · `98-review-and-improvements.md`
> **Answers:** Is the documentation complete, cohesive, and conformant to the MVP posters — and how can it be improved?
> **Source posters:** all MVP-related posters (Phases 0–8 + MVP execution posters), reviewed 2026-08-09
> **Audience:** Owner / maintainers (working backlog) · **Depth:** Reference
> **Status:** Review complete — backlog open

---

## 1. Verdict

- **Complete:** Yes for the intended scope. Every poster maps to a document; the lean reader set (`00`–`08`),
  the developer deep-dive (`deep-dive/`), the user guides, and the presentation are all present.
- **Cohesive:** Yes. Consistent headers, numbering, terminology (`90-glossary.md`), cross-links, and a single
  forward-only voice. The data model, API, SRS, and traceability matrix tie together cleanly.
- **Conformant:** Yes at the overview level, with **two categories of follow-up**:
  1. **Conformance tensions** — a few places where the *ops/decision posters* lean fuller than the confirmed
     MVP monolith. These need a decision (§2).
  2. **Extension opportunities** — the posters carry concrete specifics (tables, targets, playbooks) that the
     overview docs summarize; adding them raises efficacy (§3).

The docs are safe to use today; §2–§3 are how to make them excellent.

---

## 2. Conformance tensions (need a decision)

These arise from the known **MVP-vs-broader-vision** split (see the Part 4 conformance map in
[`99-decisions-and-history.md`](99-decisions-and-history.md)). Recommended resolution given the confirmed
"MVP modular monolith now" decision:

| # | Tension | Posters | Recommended resolution |
|---|---|---|---|
| T1 | **Docker Compose vs native.** The Ubuntu deployment poster runs the app under **Docker Compose**; our `07-operations` + ADR use **native Gunicorn/Uvicorn + systemd** (Docker later). | 28 | Keep native for the MVP; add a short "Docker Compose is an equally valid packaging option" note. **Confirm.** |
| T2 | **API gateway (APISIX).** The Decision Matrix lists **APISIX** in the "typical MVP stack"; module/component posters show a distinct **API Gateway**. Our docs use **NGINX only**. | 33, 12, 13 | Keep NGINX (optional) for the monolith; record APISIX as an optional/future gateway. **Confirm.** |
| T3 | **Object storage naming.** Posters name **MinIO** (S3-compatible); our docs say "object storage (local/S3-compatible)". | 28, 33 | Name **MinIO** as the recommended on-prem option; keep local/S3 as alternatives. Low risk — will apply. |
| T4 | **Coverage target 70% vs 80%.** Testing Pyramid poster says unit coverage **≥70%**; our docs/ADR say **~80%**. | 26 | State "≥80% overall (≥70% minimum gate, higher on critical paths)". Low risk — will apply. |
| T5 | **Shelter Management.** Personas/component/module posters reference **Shelter Management**; the authoritative ER poster (22) has **no `shelters` table**. | 8, 12, 13 vs 22 | Model shelters via a **`resource_type` = SHELTER** for the MVP; note a future dedicated entity. Low risk — will apply. |
| T6 | **Search (Elasticsearch).** Posters show **Elasticsearch (optional)** for search/logs; our docs use a generic "search service" and Loki/ELK for logs. | 12, 29 | Keep generic for MVP; Elasticsearch is optional/FFP. No change needed. |

---

## 3. Extension backlog (by document)

Priority: **P1** high-value / P2 useful / P3 nice-to-have. Each item cites its source poster.

### `01-foundation.md`
- **P2** Add the **SDLC delivery roadmap** (Idea → PRD & Architecture → Development → Testing → Deployment → Operations → Continuous Improvement, with outputs). *Poster 4 — currently unrepresented.*
- **P2** Add specific **national agency names** (MHA, MoHFW, BRO, Railways) and the **cross-cutting enablers** (Trusted Access, Common Operating Picture, Mobility, Interoperability). *Poster 3.*

### `02-architecture.md`
- **P1** Align the evolution to the poster's exact stages — **Prototype → MVP → Production Monolith → Enterprise FFP** — with the **maturity questions** ("Can it work? / Does it solve the problem? / Can it run reliably at scale? / Can it evolve endlessly?") and per-stage focus/tech. *Poster 9.*
- **P3** Note **Administration Service** and **Integration Services** as components; add sync/async/data/control **flow legend**. *Posters 12, 13.*

### `03-engineering.md`
- **P1** Add the **principles-per-layer matrix** — SOLID/DRY/KISS/YAGNI/Clean Code applied to Frontend, API/Services, Data, Core/Domain, Infrastructure, Testing, DevOps, Documentation. *Poster 18 — directly answers the "elucidate for each layer in the full-stack" ask.*
- **P1** Add design-pattern **when-to-use + benefits + per-layer application** table. *Poster 19.*

### `04-data.md`
- **P2** Add **shelter handling** note (T5); name **MinIO** as the on-prem object store (T3).

### `05-security.md`
- **P1** **Expand the threat model** with: the **OWASP Top 10 (2021) → IDRM relevance → mitigations** table, the **assets** list, **threat actors**, and a **risk assessment matrix** (Likelihood × Impact). *Poster 25 — biggest single security gap.*
- **P2** Add the **4 security layers** (Application/Data/Infrastructure/Operational), the **6-step security workflow**, and the principles **Zero Trust · Defense in Depth · Least Privilege · Secure by Default · Visibility & Accountability**. Add **NIST CSF** and **OWASP ASVS** to compliance. *Poster 24, 25.*

### `06-quality.md`
- **P1** Add pyramid **proportions** (~60% Unit / 20% API / 15% Integration / 5% E2E) on a **Test Data & Environment foundation**; add the **testing approach** flow and **tool examples** (pytest, Postman/Newman, Playwright/Cypress, k6, OWASP ZAP). *Poster 26.*
- **P2** Add CI/CD **DORA metrics** (Deployment Frequency, Lead Time, Change Failure Rate, MTTR), the **quality-gates summary**, and **pipeline triggers**. Reconcile coverage (T4). *Poster 27.*

### `07-operations.md`  *(richest extension opportunity)*
- **P1 — Deployment:** add **server specification** (Ubuntu 22.04 LTS, ~4 vCPU / 16 GB / 500 GB SSD, static IP, hostname), **open ports** (22 SSH / 80→443 / rest blocked), **data & volume paths** (`/var/lib/postgresql`, `/data/…`, `/var/log/idrm`, `/backups/idrm`), and **hardening** (SSH key-based, Fail2Ban, UFW, Let's Encrypt, patch management). *Poster 28.* Resolve T1.
- **P1 — Observability:** add the **concrete stack** (Prometheus + Grafana; Loki or ELK; OpenTelemetry + Tempo; Alertmanager + email/SMS/webhook), **SLO/SLA targets** (99.5% uptime, API p95 < 800 ms, error < 1%, incident ack < 5 min, P1 < 1 hr), a **retention-guidelines** table, an **alerting playbook**, and **on-call escalation**. *Poster 29.*
- **P1 — Disaster recovery:** add the **backup plan** table (component/what/frequency/retention/location), **RPO/RTO targets** table, the **7-step DR runbook**, the **3-2-1 rule**, **testing cadence** (quarterly restore, semi-annual failover), **tools** (pg_dump/pg_basebackup, borgbackup/restic, rsync, cron), and a **restore checklist**. *Poster 30.*

### `08-organization.md`
- **P1** Expand **roles** to the full **8-SDLC-phase** mapping (primary roles + key responsibilities + success outcomes) plus **cross-cutting roles**. *Poster 31.*
- **P1** Upgrade the **ownership matrix** to a **RACI** table (Responsible/Accountable/Consulted/Informed) with supporting roles and responsibilities per domain. *Poster 32.*
- **P2** Enrich the **decision guide** with **strengths / trade-offs / fit-scores** per technology; note **APISIX** (T2). *Poster 33.*
- **P2** Expand the **evolution roadmap** to the **6-phase, 10-year** model (Foundation → Stabilization → Integration → Intelligence → Autonomy → Resilience 2.0) with year ranges and per-dimension evolution. *Poster 34.*

### Developer deep-dive (`deep-dive/`)
- **P2** Add a **deployment & operations runbook** (server setup, cron schedule, restore checklist) — the natural deep counterpart to `07-operations`. *Posters 28–30.*
- **P3** Fold the **OWASP mapping** and expanded NFR targets into `10-srs.md`; add shelter note to `13-data-model.md`.

### Cross-cutting
- **P3** Once §2/§3 land, refresh the **presentation** and **user guides** to reflect any new specifics (e.g., SLO targets, RACI).

---

## 4. "Latest information" notes

- Standards referenced remain current (WCAG 2.2 AA, ISO/IEC 27001, ISO 22301, DPDP Act 2023, OpenAPI 3.1,
  ISO/IEC/IEEE 29148/42010, NIST CSF, OWASP Top 10 2021). No version drift found.
- The posters add **NIST Cybersecurity Framework** and **OWASP ASVS** as security references not yet cited in
  the docs — worth adding (§3, `05-security`).

---

## 5. Suggested order of work

1. **Decide §2 tensions** (T1–T2 especially).
2. **P1 batch:** `07-operations` (deployment + observability + DR specifics), `05-security` (threat model),
   `03-engineering` (per-layer matrices), `08-organization` (roles + RACI), `02-architecture` (evolution),
   `06-quality` (pyramid proportions + tools).
3. **P2 batch:** foundation SDLC/agencies, CI/CD metrics, decision-guide enrichment, 10-year roadmap.
4. **Refresh** presentation/user guides; log changes in `99-decisions-and-history.md`.

---

---

## 6. Applied — 2026-08-09 (P1 batch + quick wins)

**Tensions resolved:** T1 (keep native systemd; Docker Compose noted as optional) · T2 (keep NGINX; APISIX
noted as optional) · T3 (MinIO named) · T4 (coverage ≥80%, ≥70% gate) · T5 (shelters modelled as
`resource_type` = SHELTER).

**P1 extensions applied:**
- `07-operations` — added server spec, ports, data paths, hardening; observability SLO/SLA + tooling +
  retention + alerting playbook + on-call; DR backup plan + RPO/RTO targets + runbook + 3-2-1 + tools.
- `05-security` — added four security layers, principles, the 6-step security workflow; expanded threat model
  (assets, threat actors, STRIDE table, **OWASP Top 10 → IDRM mapping**, risk assessment, practices); added
  NIST CSF & OWASP ASVS.
- `03-engineering` — added the **principles-per-layer matrix** and design-pattern **when-to-use + per-layer**
  tables.
- `08-organization` — expanded to the **8-phase SDLC roles** (+ cross-cutting roles) and upgraded ownership to
  a **RACI** matrix; noted APISIX.
- `02-architecture` — evolution aligned to **Prototype → MVP → Production Monolith → Enterprise FFP** with
  maturity questions.
- `06-quality` — added pyramid proportions (~60/20/15/5) + test-data foundation + approach; DORA metrics;
  per-type tool examples.

**P2 batch applied (2026-08-09):**
- `01-foundation` — added the **SDLC delivery roadmap** (Poster 4), specific national agencies + the
  **Common Operating Picture** / cross-cutting enablers (Poster 3).
- `08-organization` — added the **technology fit-score** table (Poster 33) and expanded the roadmap to the
  **6-phase, 10-year** model (Poster 34).
- `06-quality` — added the **release-readiness gates** checklist (Poster 27).

**P3 batch applied (2026-08-09):**
- `02-architecture` — added the **Administration & Integration Services** note and the **four flow types**
  (sync / async / data / control).
- New `deep-dive/15-ops-runbook.md` — server setup, deploy, backup cron, restore checklist, routine ops.
- `10-srs.md` — folded the **OWASP Top 10** reference and performance targets into the NFRs.
- **Presentation refreshed** — observability slide now shows **SLO/SLA targets**; ownership slide is a **RACI**
  view; roadmap slide is the **6-phase 10-year** model. Re-validated and visually QA'd.

**Backlog complete.** (User guides were reviewed and need no change — they're task-oriented and don't surface
SLO/RACI-type detail.) All review findings are now resolved.

---

*Review performed against all MVP-related posters on 2026-08-09. Findings are additive — the current
documents remain conformant and usable as-is.*
