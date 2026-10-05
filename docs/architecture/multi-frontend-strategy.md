# Multi-Frontend Strategy

## What this document is

IDRM ships three user interfaces. This document explains why, how they
co-exist, and how they share code without becoming entangled.

## The three interfaces

| Interface | Location | Technology | Purpose |
|---|---|---|---|
| Pure web | apps/web/ | HTML, CSS, vanilla JS | The MVP baseline |
| React web | apps/web-react/ | React + TypeScript + Vite | The FFP rich web experience |
| Mobile | apps/mobile/ | React Native via Expo | iOS and Android field app |

All three co-exist on purpose. During early development we do not know which
interface a user will prefer. Keeping all three in one repository lets us
compare them and converge without rewriting the backend.

## The core principle

Apps are independent. Packages are shared.

Each app has its own package.json, build configuration, and deployment
pipeline. But every app imports shared code from packages/.

## What gets shared

| Shared concern | Where it lives | Consumed by |
|---|---|---|
| Typed API client | packages/api-client/ | web-react, mobile |
| TypeScript types | packages/types/ | all apps |
| Pure utility functions | packages/utils/ | all apps |
| ESLint / TS configs | packages/config/ | all apps |
| UI components | packages/ui/ | web-react, mobile |

## What is not shared

The pure web app (apps/web/) does not use the React packages. It has no React
runtime. It consumes the OpenAPI contract directly.

No app imports from another app. The dependency arrow always points down to
packages/.

## Why the pure web app is separate

The pure web app is the simplest possible proof that the backend API works.
It uses no framework, no bundler, no build step. If the API can serve this
app, it can serve anything.

When the FFP begins and the React app becomes the primary experience, the
pure app may be retired or kept as a fallback. The decision waits until real
users tell us which they prefer.

## How a change flows

    1. Backend adds a field to an endpoint
    2. OpenAPI spec regenerated (make contracts-export)
    3. Typed client regenerated (make contracts-generate)
    4. Every app that imports the client sees the new field
    5. If the change is breaking, the app build fails
    6. Update the app; build passes; deploy

## Deployment independence

Each app deploys on its own schedule. A change to the mobile app does not
require redeploying the web apps.

| App | Deploy target |
|---|---|
| Pure web | served by the FastAPI monolith, or a CDN |
| React web | Vercel, Netlify, or a CDN |
| Mobile | EAS Build to App Store / Google Play |

## Convergence roadmap

- MVP: only the pure web app is populated.
- Early FFP: React web and mobile are scaffolded. Shared packages grow.
- Late FFP: based on usage, retire the unused interface. Or keep all three
  if each serves a distinct audience.

The structure does not change between phases. Only the contents do.

## Next steps

- Typed API clients: ./typed-api-clients.md
- Monorepo structure: ./monorepo-structure.md
