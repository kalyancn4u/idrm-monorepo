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
