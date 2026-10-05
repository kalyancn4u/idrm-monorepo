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
