# IDRM Admin SPA (web-react)

React 18 + TypeScript + Vite single-page app for **coordinators / admins**, served on
**port 5174**. It talks to the same Bun gateway (`/api/v1`) as the HTML citizen frontend
and reuses the **Slate + Emerald + Inter** design tokens (see
`instructions/instructions_ui_v3.md`).

> 🚩 **Build & run on the Ubuntu dev laptop — not the Windows authoring box.**
> See `docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`.

## Stack

| Concern        | Choice                         |
| -------------- | ------------------------------ |
| Build / dev    | Vite (`:5174`, proxies `/api`→`:3000`, `/ws`→`:3001`) |
| Routing        | react-router-dom v6            |
| Server state   | @tanstack/react-query v5       |
| Auth state     | zustand (sessionStorage-backed)|
| Charts         | recharts                       |
| Styling        | Tailwind (Slate + Emerald)     |

## Run (Ubuntu)

```bash
cd src/frontend/web-react
bun install          # or: npm install
bun run dev          # Vite dev server on http://localhost:5174
# Requires the gateway (:3000/:3001) + FastAPI (:8000) + Postgres/Redis running.
```

Build / preview:

```bash
bun run build        # tsc -b && vite build  → dist/
bun run preview
```

## What's implemented (Module D foundation)

- **Auth** — `/login`, token persistence + silent refresh, route guarding.
- **Dashboard** (`/`) — headline metrics + Recharts bar charts from `GET /analytics/dashboard`.
- **Approval queue** (`/requests`) — the distinctly-admin **DM_AUTHORITY** capability:
  lists `SUBMITTED` requests and approves/rejects them
  (`POST /services/{id}/approve` · `POST /services/{id}/reject`). The backend enforces
  the role; non-authorised accounts get a 403 surfaced inline.

## Deferred (post-foundation)

These are intentionally **not** built in the D foundation and are tracked in
`schedules/IDRM-BUILD-WORKFLOW.md`:

- Full **user management** (list users, `POST /users/{id}/role` role grants).
- **Provider / organization** management views.
- Admin **LiveMap** (react-leaflet) + clustering (`GET /geo/cluster`).
- Request **detail drawer** and richer filtering/pagination UI.
- Real-time updates over the WebSocket channel (`ws://…:3001`).

## Layout

```
src/
├── lib/api.ts            # typed fetch client (tokens, refresh, endpoints)
├── store/auth.ts         # zustand auth store
├── components/
│   ├── Layout.tsx        # admin shell (sidebar + top bar + <Outlet/>)
│   └── ProtectedRoute.tsx
├── pages/
│   ├── Login.tsx
│   ├── Dashboard.tsx     # Recharts analytics
│   └── Requests.tsx      # approval queue
├── App.tsx               # route table
└── main.tsx              # providers (React Query + Router)
```
