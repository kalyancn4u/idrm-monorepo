# IDRM v2 — Documentation

> **Archived historical generation** (microservices: Bun API gateway + Python services, "no
> GeoServer"). Superseded — current source of truth is `../../posters/` + `../../docs/`.
> See [`CHANGELOG.md`](CHANGELOG.md).

Organised into two flat folders, named `<prefix>-<category>-<name>.md` (2-digit prefix orders files; tens-digit = category):

- **[`docs/`](docs/)** — specifications & project detail (for practitioners/architects)
- **[`guides/`](guides/)** — novice-friendly tutorials & setup how-tos
- **`assets/`** — non-document files (e.g. the `setup-idrm-ubuntu.sh` script)

## Reading tracks
| You are… | Start here | Then |
|---|---|---|
| **New / non-technical** | [`guides/00-start-beginners-guide.md`](guides/00-start-beginners-guide.md) | `guides/11-setup-complete` |
| **Setting up** | [`guides/10-setup-prerequisites.md`](guides/10-setup-prerequisites.md) | `11-complete` → `12-development` → `13-staging` → `14-production` |
| **Developer** | [`docs/21-architecture-corrected-final.md`](docs/21-architecture-corrected-final.md) *(LLD → [`../analyses/v2-30-…`](../analyses/v2-30-design-detailed-lld.md))* | `docs/40/41-api-*`, `docs/60–62-uidesign-*` |
| **Architect** | [`docs/20-architecture-monolith.md`](docs/20-architecture-monolith.md) | `21-corrected-final`, `22-lightweight`, `23-hld`, `24-decisions` |
| **Product** | [`docs/10-requirements-prd.md`](docs/10-requirements-prd.md) *(overview → [`../analyses/v2-00-…`](../analyses/v2-00-overview-vision-and-scope.md))* | `docs/90-project-roadmap` |

> Note: v2 kept **three** architecture docs (`20`/`21`/`22`) on purpose — they record the monolith-vs-microservices design debate and are intentionally not merged.

## Category legend (shared across all generation folders)
**docs/** — `00` overview · `10` requirements · `20` architecture · `30` design · `40` api · `50` data · `60` uidesign · `70` quality · `80` ops · `90` project
**guides/** — `00` start · `10` setup · `20` build · `30` contribute · `40` reference

Full lists: [`docs/README.md`](docs/README.md) · [`guides/README.md`](guides/README.md)
