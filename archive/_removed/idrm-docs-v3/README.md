# IDRM v3 — Documentation

> **Archived historical generation.** This is the v3 design generation (a "modular monolith"
> that still carried a Bun gateway + 3 frontends). It is **superseded** — the current source of
> truth is `../../posters/` + `../../docs/`. Kept here as clean, navigable reference history.
> See [`CHANGELOG.md`](CHANGELOG.md) for what changed in v3.

Everything is organised into two flat folders, named `<prefix>-<category>-<name>.md`
(the 2-digit prefix orders files; its tens-digit is the category):

- **[`docs/`](docs/)** — **specifications & project detail** (requirements, architecture, design, API, data, ops…). For practitioners and architects.
- **[`guides/`](guides/)** — **elaborate, novice-friendly** tutorials & how-tos (getting started, setup, walkthroughs). For complete beginners.

## Which should I read? (reading tracks)

| You are… | Start here | Then |
|---|---|---|
| **New / non-technical** | [`guides/00-start-getting-started.md`](guides/00-start-getting-started.md) | `guides/10-setup-*` → `guides/20-build-*` |
| **Setting up the system** | [`guides/10-setup-prerequisites.md`](guides/10-setup-prerequisites.md) | `11-development` → `12-staging` → `13-production` |
| **Developer (building it)** | [`docs/31-design-backend.md`](docs/31-design-backend.md) *(LLD → [`../analyses/v3-30-…`](../analyses/v3-30-design-detailed-lld.md))* | `docs/40-api-specification.md`, `docs/50-data-model.md`, `docs/32-design-frontend.md` |
| **Architect / reviewer** | [`docs/20-architecture-system.md`](docs/20-architecture-system.md) | `21-high-level-design`, `22-architecture-decisions`, `23-diagrams` |
| **Product / planning** | [`docs/10-requirements-prd.md`](docs/10-requirements-prd.md) *(overview → [`../analyses/v3-00-…`](../analyses/v3-00-overview-vision-and-scope.md))* | `docs/91-project-roadmap.md` |

## Category legend (shared across all generation folders)

**docs/** — `00` overview · `10` requirements · `20` architecture · `30` design · `40` api · `50` data · `60` uidesign · `70` quality · `80` ops · `90` project
**guides/** — `00` start · `10` setup · `20` build · `30` contribute · `40` reference

Full file lists: [`docs/README.md`](docs/README.md) · [`guides/README.md`](guides/README.md)
