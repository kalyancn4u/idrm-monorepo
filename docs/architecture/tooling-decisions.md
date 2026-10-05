# Tooling Decisions - Bun, Turborepo, Expo

## What this document is

Why the IDRM monorepo is built on Bun for package management, Turborepo for
task orchestration, and Expo for the mobile app. Written as a companion to
the ADR folder: the ADRs record the decision; this document records the
reasoning at full length.

## The three tools and what each does

| Tool | Role | Replaces |
|---|---|---|
| Bun | Package manager, runtime, native TypeScript execution | npm, pnpm, Yarn, Node, ts-node |
| Turborepo | Task orchestration and dependency-aware caching | Manual npm run sequencing |
| Expo | React Native framework with monorepo support | Bare React Native toolchain |

The three are complementary, not overlapping. Bun installs. Turborepo runs
tasks in the right order. Expo packages the mobile app.

## Part 1 - Why Bun

### What Bun is

Bun is an all-in-one JavaScript and TypeScript toolkit. It is simultaneously:

- A package manager (bun install)
- A runtime (bun run)
- A bundler (bun build)
- A test runner (bun test)

Bun supports workspaces in package.json, the workspace protocol, glob
patterns, and dependency filtering.

### Bun strengths for IDRM

| Strength | Detail | Impact |
|---|---|---|
| Install speed | Installs the Remix monorepo in roughly 500ms on Linux, 28x faster than npm | Faster CI; faster first-time setup |
| Unified toolchain | One binary replaces Node, pnpm, and Jest | Fewer tools to install and version |
| Native TypeScript | Runs .ts files without a transpilation step | No ts-node or tsx needed |
| Workspace support | Full support for workspace protocol, glob patterns, and filter | Compatible with the IDRM layout |
| Expo compatibility | Expo Metro config detects Bun workspaces automatically | No manual Metro config from SDK 52+ |
| Turborepo compatibility | Turborepo 2.5+ prunes Bun repositories from bun.lock | Turborepo can slice the tree for deploy |
| pnpm migration | Running bun install in a pnpm repo migrates the lockfile | Zero-friction migration path |

### Bun limitations and risks

| Limitation | Detail | Mitigation |
|---|---|---|
| Hoisted vs isolated installs | Bun 1.3.0 switched to isolated installs, then 1.3.2 reverted for existing workspaces | Use hoisted installs; they maximise compatibility |
| Performance in some cases | A 2026 report showed Bun slower than pnpm in one repo | Benchmark in your environment; keep pnpm as fallback |
| Monorepo size limits | Install can hang on very large monorepos around 6000 packages | IDRM is far below this; monitor as it grows |
| Task runner immaturity | Bun task runner lacks dependency-aware ordering and caching | Use Turborepo for orchestration |
| Isolated install bugs | Bugs were reported with Bun 1.3.0 isolated installs | Use hoisted installs or pin to a stable version |

### The verdict

Bun is viable for IDRM, paired with Turborepo. Bun handles installation and
runtime. Turborepo handles task orchestration. Expo handles the mobile app.

Bun is younger than pnpm and has had monorepo stability issues. If stability
outranks speed for the team, pnpm remains the safer choice. The trade-off is
that pnpm requires a separate tool for the runtime, whereas Bun unifies them.

## Part 2 - Why Turborepo

Bun has a task runner (bun run --filter) but it lacks two things the IDRM
monorepo needs:

1. Dependency-aware ordering. When packages/api-client changes, every app
   that depends on it must be rebuilt. Bun does not understand this.
2. Caching. If nothing changed, nothing should rebuild. Bun does not cache.

Turborepo understands the dependency graph, orders tasks correctly, caches
results, and runs tasks in parallel where possible. The pairing is:

- Bun: the package manager and runtime.
- Turborepo: the task orchestrator.

Each does one job. Neither replaces the other.

## Part 3 - Why Expo

Expo is the fastest way to build React Native apps. It provides:

- One codebase for iOS and Android.
- Over-the-air updates via EAS Update, avoiding store review for small fixes.
- Built-in monorepo support since SDK 52.
- Optional web output via react-native-web.

Since SDK 52, Expo detects a Bun monorepo automatically and configures Metro
(the React Native bundler) without manual intervention. On older SDKs, you
must set watchFolders and resolver.nodeModulesPaths in
apps/mobile/metro.config.js.

## Part 4 - What a workspace is

A workspace is a set of directories in a monorepo that can import each other
without publishing to a registry. Bun reads the workspaces key in the root
package.json:

    "workspaces": ["apps/*", "packages/*"]

This tells Bun: everything in apps/ and packages/ is a workspace member. Bun
links them, so apps/web-react can import @idrm/api-client directly from
packages/api-client/.

## Part 5 - Catalogs (optional)

Bun supports catalogs for centralised dependency version management. Instead
of declaring a version in every package, declare it once:

    "workspaces": {
      "packages": ["apps/*", "packages/*"],
      "catalogs": {
        "default": { "typescript": "^5.4.0", "react": "^18.3.0" }
      }
    }

Then packages reference the catalog. Use this once the repo has three or more
apps that share a dependency.

## Glossary of Bun and Turborepo terms

| Term | Meaning |
|---|---|
| Bun | All-in-one JavaScript toolkit: package manager, runtime, bundler, test runner |
| Turborepo | Task orchestrator for monorepos with dependency-aware caching |
| Expo | React Native framework with monorepo support |
| Metro | The JavaScript bundler used by React Native |
| Workspace | A linked directory inside a monorepo |
| Catalog | Bun feature for centralised dependency version management |
| NativeWind | Tailwind CSS for React Native |
| Lockfile | A record of exact installed versions; bun.lock in this repo |

## Tool summary

| Tool | Purpose | Configured in |
|---|---|---|
| Bun | Package manager, runtime, native TS execution | package.json, bun.lock |
| Turborepo | Task orchestration and caching | turbo.json |
| Kubb | Typed API client generation | kubb.config.ts |
| Schemathesis | Python contract testing | services tests/contract/ |
| oasprey | JS/TS contract testing | apps tests/contract/ |
| apidiffx | API compatibility across versions | CI pipeline |
| Expo | Mobile app framework | apps/mobile/ |
| Metro | React Native bundler | Auto-configured by Expo SDK 52+ |

## Further reading

- Bun workspaces: https://bun.com/docs/pm/workspaces
- Bun lockfile: https://bun.com/docs/install/lockfile
- Turborepo documentation: https://turbo.build/repo/docs
- Turborepo and Bun prune: https://turborepo.dev/blog/turbo-2-5
- Expo monorepos: https://docs.expo.dev/guides/monorepos/
- OpenAPI specification: https://spec.openapis.org/oas/v3.1.0
- Kubb: https://kubb.dev
- Schemathesis: https://schemathesis.readthedocs.io

## Next steps

- The full build order: ../../playbooks/action-plan.md
- The Bun command reference: ../../playbooks/bun-commands.md
- The layered architecture: ./layered-architecture.md
