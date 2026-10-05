# Monorepo Structure

## What this document is

A guided tour of the IDRM monorepo layout. By the end you will know what every
top-level folder contains, why it exists, and where new code belongs.

## Why a monorepo (and not many repositories)

IDRM is one product with one team. Splitting it across many Git repositories
would mean every cross-cutting change needs several pull requests, shared
code is copied instead of imported, and a version bump in one place breaks
another without warning.

A monorepo keeps everything in one place. One pull request can change the
backend API and every frontend that consumes it, atomically. That is the
single most valuable property of this repository.

## The six top-level areas

    idrm-monorepo/
      apps/        user-facing applications
      packages/    shared libraries consumed by apps
      services/    backend applications that respond to HTTP
      shared/      contracts and cross-language assets
      infra/       infrastructure as code
      gateway/     the API gateway configuration

Everything else at the root is either documentation (docs, guides, posters,
presentation, archive), tooling (scripts, tests), or configuration
(Makefile, package.json, turbo.json, .github, .vscode).

## What goes in each folder

### apps/ - applications

An app is something a person opens. A web page. A mobile screen. Apps talk to
the backend over HTTP and never touch the database.

Current contents: web (pure HTML/CSS/JS), web-react (placeholder), mobile
(placeholder). See apps/README.md.

### packages/ - shared frontend libraries

A package is a library that apps import. It is never a running program. Every
package has an @idrm/ name in its package.json.

Current contents: api-client, types, utils, config, ui. See packages/README.md.

### services/ - backend services

A service responds to HTTP. It owns its data and enforces business rules. It
is the only code allowed to talk to the database.

Current contents: monolith (active), plus ten FFP placeholders. See
services/README.md.

### shared/ - cross-language assets

Contracts (OpenAPI specs), language-specific shared libraries, and
cross-service configuration. See shared/README.md.

### infra/ - infrastructure as code

Everything required to run IDRM on real hardware: systemd units, Docker
compose, Kubernetes manifests, Terraform. See infra/README.md.

### gateway/ - the API gateway

Routing rules and (in FFP) the APISIX container. In the MVP, the FastAPI
monolith serves /api/v1/* directly; the gateway config documents the future
routing. See gateway/README.md.

## The rules that keep the structure clean

1. Apps import from packages. Packages never import from apps.
2. Services import from shared contracts. Services never import from apps.
3. No circular dependencies between packages.
4. The api-client/src/gen/ folder is machine-generated. Never edit it.

## Where to put new code

| You are adding... | Put it in... |
|---|---|
| A new screen or page | the relevant app under apps/ |
| A helper used by two apps | packages/utils/ |
| A component used by two apps | packages/ui/ |
| A backend endpoint | services/monolith/app/modules/<domain>/ |
| A new API contract field | update the FastAPI route, then make contracts-sync |
| A deploy target | infra/ |
| A new CI workflow | .github/workflows/ |

## How to see the tree

    make tree

Prints the folder tree, skipping node_modules, .git, __pycache__, and build
artefacts.

## Next steps

- Why each choice was made: ../adr/
- The layered architecture: ./layered-architecture.md
- The multi-frontend strategy: ./multi-frontend-strategy.md
