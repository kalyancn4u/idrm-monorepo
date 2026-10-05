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
