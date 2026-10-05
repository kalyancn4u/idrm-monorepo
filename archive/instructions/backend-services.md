# IDRM Instructions — Backend Services & Runtimes

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Phase rule:** MVP = **one** FastAPI modular monolith. FFP = selective services around the same contract.

## MVP — the modular monolith (LOCKED)
- **Pure-Python FastAPI**, one deployable app, clean module boundaries. Stack: Pydantic, SQLAlchemy,
  GeoAlchemy2, Alembic, pytest, Git. Deploy: native **systemd on Ubuntu** (no Docker/K8s).
- Module shape: `router.py / schemas.py / models.py / service.py / repository.py / tests/`.
  **Service never touches the DB directly — always via the repository.**
- Modules: users, incidents, resources, locations, alerts, notifications, reports, files, audit, administration.

## FFP — selective services
- **Strangler Fig**: extract one module at a time, **least-coupled first (auth)**, only on a concrete
  trigger (scale / ownership / deploy independence / perf / reliability). Public `/api/v1` contract preserved.
- **Polyglot** runtimes: Java/Go/JS for scale/security/resilience-critical services; **Python kept** for rapid
  prototyping + DS/ML. Per-service data ownership; PostGIS stays system of record.
- **Edge/BFF** (Bun/Node/Deno) runs **behind** the gateway ([`api-gateway.md`](api-gateway.md)) — composes
  per-client responses, websocket/SSE fan-out; does **not** fork the contract.
- Python geospatial service (GeoPandas/Shapely) only if FFP needs it — **not** Java GeoServer.

## Health checks & utilities (both phases)
- Every service exposes `/health` (liveness), `/ready` (readiness), `/metrics` (Prometheus).
- Gateway runs active/passive upstream health checks. Jobs/schedulers, admin API, secrets/vault,
  etcd (APISIX config store) sit here. Observability wiring: [`observability.md`](observability.md).

## Canonical docs
- [`../idrm-ffp-docs/20-architecture-system.md`](../idrm-ffp-docs/20-architecture-system.md) ·
  [`../idrm-ffp-docs/21-architecture-decisions.md`](../idrm-ffp-docs/21-architecture-decisions.md)
- MVP architecture: [`../idrm-mvp-docs/20-architecture-system.md`](../idrm-mvp-docs/20-architecture-system.md)

## Trusted external references
- FastAPI — fastapi.tiangolo.com · 12-Factor App — 12factor.net
- Strangler Fig / microservices patterns — microservices.io · martinfowler.com/bliki/StranglerFigApplication.html
- gRPC — grpc.io · Bun — bun.sh/docs · Node.js — nodejs.org/docs
