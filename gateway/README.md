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
