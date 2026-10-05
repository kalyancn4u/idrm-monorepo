# Bun Command Reference

## What this document is

Every Bun command you are likely to type in this repository, grouped by task.
A cheat sheet for daily use.

## Installation

    bun install                        Install every workspace dependency
    bun install --frozen-lockfile      Install exactly what is in bun.lock (CI)
    bun add <pkg>                      Add a dependency to the current package
    bun add -D <pkg>                   Add a dev dependency
    bun remove <pkg>                   Remove a dependency
    bun update                         Update dependencies within allowed ranges

## Running scripts

    bun run <script>                   Run a script from package.json
    bun run --filter <app> <script>    Run a script for one workspace member
    bunx <tool>                        Run a package binary without installing globally

## Turborepo commands

    bunx turbo run dev                 Start every dev server
    bunx turbo run build               Build everything, respecting dependencies
    bunx turbo run test                Run all tests
    bunx turbo run lint                Lint everything
    bunx turbo run generate            Regenerate the typed client
    bunx turbo run build --graph       Write a task-graph HTML file
    bunx turbo prune --scope=web-react Prepare a pruned bundle for deploy

## Contract and code generation

    bunx kubb generate                 Regenerate the typed API client
    bunx @redocly/cli lint <spec>      Validate the OpenAPI spec

## Working with the monorepo root

    bun run dev                        Runs turbo run dev (see package.json)
    bun run build                      Runs turbo run build
    bun run test                       Runs turbo run test
    bun run lint                       Runs turbo run lint

The root package.json maps these to Turborepo tasks.

## Working with one app

    cd apps/web-react
    bun run dev                        Start the Vite dev server
    bun run build                      Build for production
    bun run test                       Run Jest
    bun run lint                       Run ESLint

    cd apps/mobile
    bun run dev                        Start Expo
    bun run ios                        Start on iOS simulator
    bun run android                    Start on Android emulator
    bun run web                        Start on web (via react-native-web)

## Working with one package

    cd packages/api-client
    bun run generate                   Regenerate the client

    cd packages/types
    bun run build                      Compile the package

## Typical daily sequence

    bun install                        Once after pulling
    make dev                           Start the backend and dev servers
    make test                          Run tests
    make qa                            Lint, typecheck, test
    make contracts-sync                After a backend API change

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Cannot find module @idrm/api-client | Workspace not linked | Run bun install at the root |
| EACCES on install | Permissions on the cache | bun install --force, or clear the cache |
| Metro cannot find a package | Metro has stale cache | cd apps/mobile then bunx expo start -c |
| Turborepo does not see a task | Not in turbo.json | Add the task to turbo.json |
| CI fails on lockfile mismatch | bun.lock out of date | Run bun install locally and commit the lockfile |
| Generated client differs from committed | Forgot to regenerate | make contracts-generate then commit |

## Bun-specific tips

- Bun runs TypeScript natively. You do not need ts-node or tsx.
- Bun test runner works for simple cases; use Jest for the full app test
  suites so the mocking and matcher ecosystem is available.
- Bun reads bun.lock in CI. Always commit this file after running bun install.
- Bun honours the workspace protocol for internal dependencies.

## Related

- The tooling decisions: ../architecture/tooling-decisions.md
- The action plan: ./action-plan.md
- The Makefile playbook: ./makefile-playbook.md
