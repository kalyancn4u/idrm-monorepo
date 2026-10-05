#!/usr/bin/env bash
set -u
[ -d "packages" ] || { echo "Run from the idrm-monorepo root."; exit 1; }
w() { local p="$1"; mkdir -p "$(dirname "$p")"; cat > "$p"; echo "wrote $p"; }

w packages/README.md <<'ENDREADME'
# Packages

Shared TypeScript and JavaScript libraries used by every frontend app.

A package is not a running program. It is a library that other code imports.
Every package declares its name under the @idrm/ scope in its package.json.

## What is inside

| Package | Purpose | Consumed by |
|---|---|---|
| api-client/ | Typed HTTP client generated from the OpenAPI contract | apps/web-react/, apps/mobile/ |
| types/      | TypeScript types shared across apps | every frontend |
| utils/      | Framework-free helper functions | every frontend |
| config/     | Base ESLint and TypeScript configs | every frontend |
| ui/         | Shared React Native components | apps/web-react/, apps/mobile/ |

## Rules

1. Packages never import from apps/. The dependency arrow points the other
   way: apps depend on packages.
2. Packages must not depend on each other in a loop. Keep the graph a DAG.
3. api-client/src/gen/ is machine-generated. Never edit it by hand. See
   ../docs/architecture/typed-api-clients.md.

## How to add a package

1. Create a folder under packages/.
2. Add a package.json with "name": "@idrm/<name>".
3. Export the public surface from src/index.ts.
4. Run bun install from the repository root.
5. Import it from an app with "@idrm/<name>": "workspace:*".
ENDREADME

w packages/api-client/README.md <<'ENDREADME'
# @idrm/api-client

The typed HTTP client that every React-based frontend uses to call the
backend API.

## Why it exists

Without a shared client, each frontend writes its own HTTP calls and drifts
out of sync with the backend. This package is generated from the OpenAPI
contract in shared/contracts/v1/, so every request and response has a
TypeScript type.

When the backend changes and the contract is regenerated, every app that
imported this package fails to build if it relied on a removed field,
before the change reaches production.

## What is inside

    packages/api-client/
      package.json
      README.md          this file
      src/
        index.ts         public exports
        gen/             MACHINE-GENERATED, never edit by hand

## How to regenerate

From the repository root:

    make contracts-export      refresh the OpenAPI spec from the backend
    make contracts-generate    regenerate this package

Or in one step:

    make contracts-sync

## How apps use it

    import { createIncident, listIncidents } from '@idrm/api-client';

## Rules

1. Never hand-edit anything under src/gen/.
2. Never commit a regenerated client without the contract change it reflects.
3. If the client fails to build after regeneration, the app that imported it
   must be updated. Do not silently loosen the types.

## Next steps

- How it works: ../../docs/architecture/typed-api-clients.md
- The contract: ../../shared/contracts/README.md
ENDREADME

w packages/types/README.md <<'ENDREADME'
# @idrm/types

TypeScript types shared across every frontend app.

## Why it exists

A type declared once is understood by every app that imports it. A type
redeclared in three places drifts. This package is the single home for
cross-app types.

## What belongs here

- Primitive aliases (UUID, ISODate, CurrencyCode)
- Enums that span apps (IncidentStatus, UserRole)
- Interfaces for shape contracts not covered by the API client

## What does not belong here

- Types specific to one app (keep them in that app)
- Runtime code (use @idrm/utils instead)
- API response shapes (those come from @idrm/api-client)

## How to use it

    import type { UUID, ISODate } from '@idrm/types';

## How to add a type

1. Add the declaration to packages/types/src/index.ts.
2. Export it.
3. Re-run bun install from the root if the package has not been installed
   yet.
ENDREADME

w packages/utils/README.md <<'ENDREADME'
# @idrm/utils

Framework-free helper functions shared across every frontend app.

## Why it exists

Small, pure functions used in more than one app (date formatting,
validation, string manipulation) belong in one place, tested once.

## What belongs here

- Pure functions with no framework dependency
- Formatting helpers (dates, numbers, distances)
- Validation predicates (email shape, phone shape)
- Small algorithms that are identical across apps

## What does not belong here

- React components (use @idrm/ui)
- Framework-specific code (that belongs in each app)
- API calls (use @idrm/api-client)

## How to use it

    import { formatDistanceKm, isEmail } from '@idrm/utils';

## Rule of thumb

If a function is used by one app, keep it in that app. Move it here the
second time another app needs it.
ENDREADME

w packages/config/README.md <<'ENDREADME'
# @idrm/config

Shared ESLint, TypeScript, and build configuration used by every frontend
app.

## Why it exists

Without shared config, each app declares its own lint rules and TypeScript
strictness. Over time they drift, and a change that passes in one app fails
in another.

## What is inside

| File | What it does |
|---|---|
| eslint.js | Base ESLint config every app extends |
| tsconfig.base.json | Base TypeScript config every app extends |

## How apps use it

In tsconfig.json:

    { "extends": "@idrm/config/tsconfig.base.json" }

In .eslintrc.cjs:

    module.exports = { extends: ['@idrm/config/eslint'] };

## Rules

1. Changes here affect every app. Test in one app before merging.
2. Do not weaken strictness silently. Announce in the pull request.
3. Keep the base minimal. App-specific rules belong in the app.
ENDREADME

w packages/ui/README.md <<'ENDREADME'
# @idrm/ui

Shared UI components used by apps/web-react/ and apps/mobile/.

## Why it exists

React web and React Native can share a surprising amount of component code
when components are built on React Native primitives and styled with
NativeWind (Tailwind for React Native). One component serves both targets.

## How the sharing works

- Written once, using React Native primitives (View, Text, Pressable).
- On web, react-native-web renders them as HTML.
- On mobile, React Native renders them natively.
- Styling uses NativeWind, Tailwind class syntax that works on both.

## What belongs here

- Buttons, inputs, cards, list items, badges
- Layout primitives (stack, grid, container)
- Design tokens (colours, spacing, typography)

## What does not belong here

- The pure web app (apps/web/), which has no React runtime.
- App-specific screens, which live in each app's src/routes/.

## How to use it

    import { Button, Card } from '@idrm/ui';

## Next steps

- Multi-frontend strategy: ../../docs/architecture/multi-frontend-strategy.md
- Design system: ../../docs/mvp/33-design-system.md
ENDREADME

echo "Script 3 done."
