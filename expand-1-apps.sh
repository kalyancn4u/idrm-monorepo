#!/usr/bin/env bash
set -u
[ -d "apps" ] || { echo "Run from the idrm-monorepo root."; exit 1; }
w() { local p="$1"; mkdir -p "$(dirname "$p")"; cat > "$p"; echo "wrote $p"; }

w apps/README.md <<'ENDREADME'
# Apps

This folder holds every user-facing application in the IDRM monorepo.

An app is something a person opens: a web page, a mobile screen. Apps talk
to the backend over HTTP; they never touch the database directly.

## What is inside

| Folder | What it is | Runs on | Status |
|---|---|---|---|
| web/       | Pure HTML, CSS, vanilla JS | Any modern browser | Active (MVP) |
| web-react/ | React + TypeScript web app | Any modern browser | Placeholder (FFP) |
| mobile/    | Expo React Native app | iOS + Android | Placeholder (FFP) |

The three apps co-exist on purpose. During early development we do not know
which frontend experience will win. Keeping all three in one place lets us
compare and converge without rewriting the backend.

## How the apps share code

Apps never import from each other. They only import from packages/ at the
repository root. This keeps each app independent while letting them share
types, utilities, and the typed API client.

## Which one should I work on?

- Building the MVP? Start with web/.
- Building the FFP web experience? See web-react/.
- Building the mobile experience? See mobile/.
- Not sure? Read ../docs/architecture/multi-frontend-strategy.md

## Adding a new app

1. Create a folder under apps/.
2. Add a README.md explaining what it is.
3. Add a package.json with a name field.
4. Run bun install from the repository root.
ENDREADME

w apps/web/README.md <<'ENDREADME'
# Pure Web Interface

A plain HTML, CSS, and JavaScript interface. No framework, no bundler, no
build step. This is the MVP primary user-facing surface.

## Why it exists

The pure web app is the simplest possible proof that the backend API works.
It loads static files, calls the API with fetch, and renders the results.
If the API can serve this app, it can serve anything.

## What is inside

    apps/web/
      README.md          this file
      Makefile           make serve starts a local server
      static/            every file the browser loads
        css/             app.css (all styles)
        img/             icons and images
        js/              client-side JavaScript

Templates that Jinja2 renders live separately, at
../../services/monolith/app/templates/ because FastAPI renders them, not
the browser.

## How to run it

Option A, through the backend (recommended):

    cd ../../services/monolith
    make dev
    # open http://localhost:8000

Option B, standalone static server (no API):

    cd apps/web
    make serve
    # open http://localhost:8080

## How to test it

No test suite for pure HTML. Manual verification:

1. Start the backend (make dev in services/monolith/).
2. Open the page in a browser.
3. Confirm each screen renders and fetches data.

## Next steps

- Typed API client: ../../docs/architecture/typed-api-clients.md
- Design system: ../../docs/mvp/33-design-system.md
ENDREADME

w apps/web-react/README.md <<'ENDREADME'
# React Web App

The FFP (Full-Fledged Product) web interface: React + TypeScript + Vite.

## Why it exists

The pure web app in apps/web/ proves the API works. This app is the
production-grade web experience: richer interactions, better state
management, a component library.

It is a placeholder during the MVP. It becomes active when the FFP begins.

## Why a separate app (not a replacement)

The two web apps co-exist. The pure app is the baseline; the React app is
the future. Keeping them separate lets us prove the API against the simpler
app while building the richer one.

## How to scaffold it (when you are ready)

    cd apps
    bun create vite web-react --template react-ts
    cd web-react
    bun install

Then add the workspace dependencies to apps/web-react/package.json:

    "dependencies": {
      "@idrm/api-client": "workspace:*",
      "@idrm/types": "workspace:*",
      "@idrm/utils": "workspace:*"
    }

## Planned contents

    apps/web-react/
      package.json
      tsconfig.json      extends @idrm/config
      vite.config.ts
      index.html
      src/
        main.tsx         React entry point
        App.tsx          root component
        routes/          page components
        components/      shared pieces
      tests/
        contract/        oasprey contract tests

## Next steps

- Multi-frontend strategy: ../../docs/architecture/multi-frontend-strategy.md
- Shared UI components: ../../packages/ui/README.md
ENDREADME

w apps/mobile/README.md <<'ENDREADME'
# Expo Mobile App

The FFP mobile interface: React Native built with Expo. Runs on iOS and
Android from the same codebase.

## Why it exists

Disaster responders work in the field, often outdoors, often with patchy
connectivity. They need a native mobile experience, not a browser.

This app is a placeholder during the MVP. It becomes active when the FFP
begins.

## Why Expo

Expo is the fastest way to build React Native apps:

- One codebase for iOS and Android.
- Over-the-air updates (EAS Update), no store review for small fixes.
- Built-in monorepo support since SDK 52.
- Runs on web too (via react-native-web) if needed later.

## How to scaffold it

    cd apps
    bun create expo-app mobile --template blank-typescript
    cd mobile
    bun install

Metro (the React Native bundler) is configured automatically for monorepos
in Expo SDK 52+. No manual metro.config.js needed.

## Planned contents

    apps/mobile/
      package.json
      app.json           Expo configuration (name, icons, splash)
      app/               Expo Router file-based routes
      assets/            icons and images
      components/        shared with web-react via packages/ui/

## Next steps

- Shared UI components: ../../packages/ui/README.md
- Expo monorepo guide: https://docs.expo.dev/guides/monorepos/
ENDREADME

echo "Script 1 done."
