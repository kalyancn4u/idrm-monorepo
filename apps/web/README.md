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
