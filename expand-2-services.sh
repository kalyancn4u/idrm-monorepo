#!/usr/bin/env bash
set -u
[ -d "services" ] || { echo "Run from the idrm-monorepo root."; exit 1; }
w() { local p="$1"; mkdir -p "$(dirname "$p")"; cat > "$p"; echo "wrote $p"; }

w services/README.md <<'ENDREADME'
# Services

This folder holds every backend application in the IDRM monorepo.

A service is a program that responds to HTTP requests. It owns its own
data, enforces business rules, and exposes them through a versioned API
(/api/v1/...). Services are the only code allowed to talk to the database.

## What is inside

| Folder | What it is | Language | Status |
|---|---|---|---|
| monolith/                | The MVP: all ten domains in one FastAPI app | Python | Active |
| users-service/           | FFP extraction of the users domain         | TBD    | Placeholder |
| incidents-service/       | FFP extraction of the incidents domain     | TBD    | Placeholder |
| resources-service/       | FFP extraction of the resources domain     | TBD    | Placeholder |
| locations-service/       | FFP extraction of the locations domain     | TBD    | Placeholder |
| alerts-service/          | FFP extraction of the alerts domain        | TBD    | Placeholder |
| notifications-service/   | FFP extraction of notifications            | TBD    | Placeholder |
| reports-service/         | FFP extraction of reports                  | TBD    | Placeholder |
| files-service/           | FFP extraction of file handling            | TBD    | Placeholder |
| audit-service/           | FFP extraction of audit logging            | TBD    | Placeholder |
| administration-service/  | FFP extraction of administration           | TBD    | Placeholder |

In the MVP, all ten domains live inside monolith/. In the FFP, they are
extracted one at a time. The monolith shrinks as the FFP grows, until it is
empty and can be retired.

## The shape every service shares

    <service>/
      src/api/            HTTP handlers (controllers)
      src/domain/         business rules and models
      src/infrastructure/ database and external clients
      tests/              unit | integration | contract
      Makefile            make dev, make test, make lint
      README.md           what this service does

The folder shape is identical across languages. Only the files inside src/
differ between Python, Go, Java, or TypeScript.

## How a service talks to the world

- Down to data: through a repository, never raw SQL in business logic.
- Across to other services: through HTTP, using the shared contracts in
  ../shared/contracts/v1/.
- Up to frontends: through /api/v1/..., documented in OpenAPI.

## Where to start

- New to the codebase? Read ../docs/walkthrough/02-anatomy-of-a-module.md
- Adding a new service? Read ../docs/contributing/adding-a-service.md
ENDREADME

w gateway/README.md <<'ENDREADME'
# API Gateway

The single entry point for every HTTP request that reaches the IDRM backend.

## Why a gateway exists

Without one, every frontend must know the address of every backend service,
apply authentication itself, enforce rate limits itself, and retry failed
calls itself. With a gateway, that work happens once, in one place.

## What it does

| Concern | Handled by the gateway |
|---|---|
| Routing             | /api/v1/incidents/* goes to incidents service |
| Authentication      | Validates the JWT before forwarding |
| Rate limiting       | Per-client limits to prevent abuse |
| TLS termination     | HTTPS at the edge, HTTP inside the cluster |
| Request logging     | Adds correlation IDs for tracing |
| Circuit breaking    | Fails fast when a backend is unhealthy |

## What is inside

    gateway/
      README.md             this file
      config/
        routes.yaml         routing rules (documentation in MVP)
      docker/               (FFP) container build

## MVP vs FFP

- MVP: there is no running gateway. The FastAPI monolith serves /api/v1/*
  directly. The routes.yaml file exists as documentation of the routing
  that will activate in the FFP.
- FFP: APISIX starts up and reads routes.yaml. From then on, every request
  passes through the gateway.

## Why config-only in the MVP

Deploying an API gateway adds a process, a container, and a failure mode.
In the MVP there is only one backend service, so a gateway buys nothing.
The config is written now so the FFP switch is a one-line change, not a
re-architecture.

## Next steps

- Layered architecture: ../docs/architecture/layered-architecture.md
- Routing configuration: ./config/routes.yaml
ENDREADME

w infra/README.md <<'ENDREADME'
# Infrastructure

Everything required to run IDRM on real hardware: process managers,
containers, cluster manifests, cloud resources, and CI pipelines.

## What is inside

| Folder | What it holds | Used in |
|---|---|---|
| systemd/   | Unit files that start the monolith on a Linux VM | MVP |
| docker/    | Dockerfiles and Compose files | FFP |
| k8s/       | Kubernetes manifests and Helm charts | FFP |
| terraform/ | Cloud resources (databases, buckets, DNS) | FFP |
| ci/        | Pipeline definitions shared by every service | FFP |

## Why separate from services/

Code and the machines it runs on change for different reasons. A new
endpoint does not require a new systemd unit. A new deploy target does not
require a code change. Keeping them in separate trees keeps each pull
request focused.

## MVP path (today)

The MVP runs on a single Linux host:

1. Python environment created by:
     conda env create -f services/monolith/environment.yml
2. systemd/idrm.service starts uvicorn on port 8000.
3. systemd/idrm-migrate.service runs Alembic migrations once at boot.
4. PostgreSQL and MinIO run on the same host or as managed services.

## FFP path (later)

Each service becomes a container. Kubernetes schedules them. Terraform
provisions databases, buckets, and DNS. CI builds and pushes images on
every merge to main.

## What to read next

- Deploy the MVP: ../docs/mvp/80-ops-deployment-and-operations.md
- Plan the FFP: ../docs/ffp/80-ops-platform-and-deployment.md
ENDREADME

echo "Script 2 done."
