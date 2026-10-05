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
