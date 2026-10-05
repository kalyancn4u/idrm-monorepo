# IDRM Instructions — Spokes Index

These are the **auxiliary instruction files** ("spokes") routed to from the lean hub
[`../instructions.txt`](../instructions.txt). Read the hub FIRST; open a spoke only for the
topic you're working on.

**What a spoke is:** a *thin router* — the phase-scoped decisions + working guidance + pointers into
the canonical docs (`../idrm-mvp-docs/`, `../idrm-ffp-docs/`) + a few vetted external references.
**What a spoke is NOT:** a second copy of the docs. When a decision and a doc disagree, the **doc wins**
and the spoke is corrected. One source of truth per fact.

**Phase rule (applies to every spoke):** MVP = simple, build-first (FastAPI modular monolith,
HTML+Tailwind+JS, Postgres+PostGIS, MinIO, no Redis/React/Bun/Docker). FFP = the enterprise evolution
on the *same* `/api/v1` contract. Advanced tech is **FFP unless a spoke says otherwise**.

| #  | Spoke                                         | Topic                                                     | Primary canonical docs   |
| -- | --------------------------------------------- | --------------------------------------------------------- | ------------------------ |
| 1  | [`ui.md`](ui.md)                               | Web + React + Expo clients                                | 60, 61 (FFP) · 60 (MVP) |
| 2  | [`api-gateway.md`](api-gateway.md)             | APISIX (vs Kong), edge/BFF                                | 20 (FFP)                 |
| 3  | [`apis.md`](apis.md)                           | `/api/v1` contract, API types, integrations             | 40                       |
| 4  | [`data-stores.md`](data-stores.md)             | Postgres/PostGIS, Redis, MinIO — engines & ops           | 50, 80                   |
| 5  | [`data-modeling.md`](data-modeling.md)         | Schema modeling (relational/spatial/TS/KV)                | 50                       |
| 6  | [`security.md`](security.md)                   | AuthN/Z, OWASP, DPDP, TLS, secrets                        | 22, 61 §9–10           |
| 7  | [`observability.md`](observability.md)         | Metrics, tracing, logs, RUM                               | 80, 61 §18              |
| 8  | [`caching-messaging.md`](caching-messaging.md) | Redis/Streams → RabbitMQ/Kafka, real-time                | 81                       |
| 9  | [`backend-services.md`](backend-services.md)   | Runtimes/polyglot, extraction, health, jobs, BFF          | 20, 21                   |
| 10 | [`backup-and-dr.md`](backup-and-dr.md)         | Backups, PITR, restore drills, RPO/RTO                    | 80                       |
| 11 | [`domain.md`](domain.md)                       | Domain quick-reference —*elucidated* ground-truth card | 10, 50, 40, 22           |

**Process file (not a topic router):** [`definition-of-done.md`](definition-of-done.md) — the cross-cutting
**finalization checklist** for every doc/guide (blueprint T4). Apply before marking anything "done."

*Maintenance:* when a locked decision changes, update the **hub's** digest + the relevant **spoke** +
the canonical **doc** + the dated **CHANGELOG**. Keep the four in step.
