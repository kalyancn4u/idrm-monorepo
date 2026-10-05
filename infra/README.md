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
