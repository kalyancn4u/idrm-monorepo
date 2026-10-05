# Migration Mapping

## What this document is

The file-by-file map from the old `idrm-artifacts` repository to the new
`idrm-monorepo`. Keep it for reference; the migration itself is complete.

## What changed and why

The old repository was called `idrm-artifacts`. It was originally a
documentation and specification repository, with a single `code/` folder
containing the FastAPI monolith.

The new repository is a **polyglot monorepo**. It contains multiple frontends,
multiple backend services, shared packages, contracts, infrastructure, and
documentation — all in one tree.

The tree was designed to serve both the MVP (today) and the FFP (tomorrow)
without ever being restructured. The MVP is a populated subset; the FFP is an
additive extension.

## Root files

| Old | New | Notes |
|---|---|---|
| README.md | README.md | Updated to describe the monorepo |
| PENDING.md | PENDING.md | Paths updated |
| .gitignore | .gitignore | Extended for JS, Python, Docker artefacts |
| .gitattributes | .gitattributes | Now enforces LF line endings |
| .github/ | .github/ | Workflows updated for the new paths |
| .vscode/ | .vscode/ | Settings updated for the monorepo |
| docs/ | docs/ | Unchanged; new subfolders added |
| guides/ | guides/ | Unchanged |
| posters/ | posters/ | Unchanged |
| presentation/ | presentation/ | Unchanged |
| archive/ | archive/ | Unchanged |
| scripts/ | scripts/ | Root scripts unchanged |

## The code/ folder

The most important mapping. Everything inside code/ moved into the new
structure.

| Old | New |
|---|---|
| code/app/ | services/monolith/app/ |
| code/app/core/ | services/monolith/app/core/ |
| code/app/infrastructure/ | services/monolith/app/infrastructure/ |
| code/app/modules/ | services/monolith/app/modules/ |
| code/tests/ | services/monolith/tests/ |
| code/alembic/ | services/monolith/alembic/ |
| code/scripts/ | services/monolith/scripts/ |
| code/alembic.ini | services/monolith/alembic.ini |
| code/Makefile | services/monolith/Makefile |
| code/pyproject.toml | services/monolith/pyproject.toml |
| code/environment.yml | services/monolith/environment.yml |
| code/.env.example | services/monolith/.env.example |
| code/CHANGELOG.md | services/monolith/CHANGELOG.md |
| code/README.md | services/monolith/CODE-README.md |

## The frontend split

The one structural split in the migration. The old code/frontend/ folder held
two kinds of asset that belong in different places in the new tree.

| Old | New | Reason |
|---|---|---|
| code/frontend/templates/ | services/monolith/app/templates/ | Jinja2 templates are rendered by FastAPI; they stay with the monolith |
| code/frontend/static/ | apps/web/static/ | Static assets are served by the browser; they belong to the web app |

## New folders created by the migration

These have no counterpart in the old repository. They are placeholders for
the FFP or entirely new concerns.

| Folder | Purpose |
|---|---|
| apps/web-react/ | React web app (FFP) |
| apps/mobile/ | Expo mobile app (FFP) |
| packages/api-client/ | Generated typed API client |
| packages/types/ | Shared TypeScript types |
| packages/utils/ | Pure utility functions |
| packages/config/ | Shared lint and TS configs |
| packages/ui/ | Shared UI components |
| services/users-service/ | FFP service placeholder |
| services/incidents-service/ | FFP service placeholder |
| services/resources-service/ | FFP service placeholder |
| services/locations-service/ | FFP service placeholder |
| services/alerts-service/ | FFP service placeholder |
| services/notifications-service/ | FFP service placeholder |
| services/reports-service/ | FFP service placeholder |
| services/files-service/ | FFP service placeholder |
| services/audit-service/ | FFP service placeholder |
| services/administration-service/ | FFP service placeholder |
| shared/contracts/v1/ | OpenAPI specifications |
| shared/libs/python/ | Shared Python library |
| shared/libs/java/ | Shared Java library |
| shared/libs/go/ | Shared Go library |
| shared/libs/ts/ | Shared TypeScript library |
| shared/config/ | Cross-service configuration |
| infra/systemd/ | Deployment units |
| infra/docker/ | Docker configuration |
| infra/k8s/ | Kubernetes manifests |
| infra/terraform/ | Cloud resources |
| infra/ci/ | CI pipelines |
| tests/smoke/ | Cross-service smoke tests |
| tests/e2e/ | End-to-end tests |
| docs/architecture/ | Architecture documents |
| docs/adr/ | Architecture decision records |
| docs/playbooks/ | Operational playbooks |
| docs/contributing/ | Contribution guides |

## New root files

| File | Purpose |
|---|---|
| package.json | Bun workspace manifest |
| turbo.json | Turborepo task graph |
| bun.lock | Bun lockfile |
| Makefile | Language-neutral command surface |
| kubb.config.ts | Typed client generator config |
| .bun-version | Pinned Bun version |
| .editorconfig | Editor consistency |

## What stayed the same

Documentation. Everything under docs/mvp/, docs/ffp/, docs/walkthrough/,
docs/whitepapers/, docs/deep-dive/, and docs/user-guides/ was preserved. Only
internal path references were updated where they pointed to the old code/
folder.

Guides, posters, and presentation decks are unchanged.

## What is not migrated

The old repository remains in place as a frozen snapshot. It is not deleted.
Its purpose is historical: to preserve the state of the code at the moment
the monorepo was created.

## How to verify the migration

From the new repository root:

    ls services/monolith/app/modules/    # should list ten domains
    ls apps/web/static/                  # should list css, js, img
    ls shared/contracts/v1/              # should contain openapi.json
    make help                            # should print the target list

If all four commands succeed, the migration is complete.

## Summary

One code folder became services/monolith plus apps/web/static plus
services/monolith/app/templates. One repository became a polyglot monorepo
with three frontends, ten service placeholders, five shared packages, and a
single OpenAPI contract.

## Related

- Implementation playbook: ./implementation-playbook.md
- Makefile playbook: ./makefile-playbook.md
- Monorepo structure: ../architecture/monorepo-structure.md
