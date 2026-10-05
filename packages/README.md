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
