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
