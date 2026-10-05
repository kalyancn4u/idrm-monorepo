# 🚩 IDRM on Ubuntu — Ports & Environments (Dev · Staging · Production)

**Audience:** complete beginners. If you've never opened a port or run Docker, start here.
**Platform:** the IDRM dev/target machine is an **Ubuntu laptop/PC** (Ubuntu 22.04+).
**What you'll learn:** what "opening a port" really means, the exact IDRM ports, how to
**check** and **free** ports, when (and how) to open the **firewall**, and how to run the
**development → staging → production** environments **one after another on the same
Ubuntu machine** without them stepping on each other.

> 🚩 **The single most important rule** is in [§6](#6-): the three environments all use the
> **same ports**, so on one machine you run **only one at a time**. Skip there if that's all you need.

---

## Table of contents
1. [What "opening a port" actually means (the 2 layers)](#1-what-opening-a-port-actually-means)
2. [The IDRM port map](#2-the-idrm-port-map)
3. [Checking ports on Ubuntu (what's listening? who's using it? free it)](#3-checking-ports-on-ubuntu)
4. [Opening a port in the firewall (ufw) — only when you need it](#4-opening-a-port-in-the-firewall-ufw)
5. [Reaching a service from another device (phone/another laptop)](#5-reaching-a-service-from-another-device)
6. [🚩 Dev · Staging · Production on the SAME Ubuntu host, one at a time](#6-)
7. [Quick reference & troubleshooting](#7-quick-reference--troubleshooting)

---

## 1. What "opening a port" actually means

A **port** is just a numbered "door" on your machine (0–65535). A program **listens** on a
port so other programs can connect to it. `http://localhost:8000` means "connect to port
**8000** on **this machine**."

🚩 **"Opening a port" is really TWO separate things — beginners constantly confuse them:**

| Layer | Question it answers | Who controls it |
|-------|--------------------|-----------------|
| **1. Is a program listening on the port?** | "Is anything answering on 8000?" | the app (uvicorn, bun, vite, postgres…) |
| **2. Is the firewall letting connections through?** | "Will the OS allow a connection from outside?" | the Ubuntu firewall (`ufw`) + (on a cloud VM) the cloud security group |

🚩 **For normal local development you usually need NEITHER step.** When your browser on the
**same laptop** opens `http://localhost:5173`, the traffic goes over the **loopback**
interface (`127.0.0.1`), which **the firewall never blocks**. So: start the app → it just
works in your browser. You only deal with the firewall (§4) and `0.0.0.0` binding (§5) when
a **different device** (your phone, a colleague's laptop) needs to reach your machine.

---

## 2. The IDRM port map

These are the ports IDRM uses. (Source of truth: `.env`, `infra/docker/full-stack.yml`.)

| Port  | Service | Used in | Listens on by default | Open the firewall? |
|-------|---------|---------|------------------------|--------------------|
| **8000** | FastAPI backend (the monolith) | dev (uvicorn), staging/prod (container) | `127.0.0.1` in dev | No (internal; the gateway calls it) |
| **3000** | Bun API Gateway — HTTP | all | `0.0.0.0` (all interfaces) | Only for LAN access |
| **3001** | Bun API Gateway — WebSocket | all | `0.0.0.0` | Only for LAN access |
| **5173** | HTML/Tailwind frontend (Vite) | dev | `127.0.0.1` | Only for LAN access |
| **5174** | React SPA frontend (Vite) | dev | `127.0.0.1` | Only for LAN access |
| **5432** | PostgreSQL 16 + PostGIS | all | `127.0.0.1` | **No — keep the database private** |
| **6379** | Redis 7.2 | all | `127.0.0.1` | **No — keep Redis private** |
| **80**   | NGINX (TLS/static/reverse-proxy) | staging/prod (Docker) | `0.0.0.0` | Yes (it's the public entry point) |
| **19000**| Expo dev server (React Native) | 🔒 Post-MVP | — | Only to test on a phone |

🚩 **Never expose `5432` (Postgres) or `6379` (Redis) to the network or internet.** They hold
your data and (by default) trust whoever can connect. Keep them on `127.0.0.1`.

🚩 In **production**, the **only** port that should face the world is **443** (HTTPS, via
NGINX) — and **80** only to redirect to 443. Everything else (8000/3000/5432/6379) stays
internal to the host/Docker network.

---

## 3. Checking ports on Ubuntu

Three everyday questions, with copy-paste commands.

### a) "Is anything listening on this port?"
```bash
# ss = the modern tool (preinstalled). -t TCP, -u UDP, -l listening, -n numeric, -p program
ss -tulpn | grep ':8000'         # one port
sudo ss -tulpn | grep -E ':(3000|3001|8000|5173|5174|5432|6379|80)\b'   # all IDRM ports at once
```
- **Output line** → something is listening (a program "owns" that door).
- **No output** → the port is free.

> 🚩 Use `sudo` to see the **owning program/PID** (the `users:(("name",pid=1234,...))` part).
> Without `sudo` you still see the port, just not always who owns it.

### b) "Which program is using port 8000?"
```bash
sudo lsof -i :8000          # lists the process (COMMAND, PID, USER)
# or, just the PID:
sudo lsof -t -i :8000
```

### c) "Free the port" (stop whatever is using it)
```bash
# Cleanest for dev: go to the terminal running it and press Ctrl + C.

# If it's an orphaned process, find the PID then stop it:
sudo lsof -t -i :8000 | xargs -r kill        # polite stop (SIGTERM)
sudo lsof -t -i :8000 | xargs -r kill -9     # force, if it won't die

# Or in one shot:
sudo fuser -k 8000/tcp                        # kill whatever holds TCP port 8000
```
🚩 If the port is held by a **Docker** container, `kill` won't help — use Docker instead:
`docker compose -f infra/docker/full-stack.yml down` (see §6). If it's the **system
database** (5432) or **Redis** (6379): `sudo systemctl stop postgresql redis-server`.

---

## 4. Opening a port in the firewall (ufw)

Ubuntu's beginner-friendly firewall is **`ufw`** (Uncomplicated FireWall).

🚩 **First, check whether the firewall is even on:**
```bash
sudo ufw status verbose
```
- `Status: inactive` → there's **no firewall blocking anything**; you don't need to "open"
  ports at all (they're reachable subject only to §5). Many fresh Ubuntu desktops are like this.
- `Status: active` → only explicitly-allowed ports accept outside connections.

🚩🚩 **If your Ubuntu box is REMOTE (you SSH in), allow SSH BEFORE enabling ufw — or you will
lock yourself out:**
```bash
sudo ufw allow OpenSSH        # (or: sudo ufw allow 22/tcp)
sudo ufw enable
```

**Open a port** (only needed so **other devices** can reach a service — see §5):
```bash
sudo ufw allow 5173/tcp                 # open the HTML frontend to the LAN
sudo ufw allow 3000/tcp                 # open the API gateway to the LAN
sudo ufw status numbered                # list rules (with numbers, to delete later)
```

🚩 **Safer: allow only your local network, not the whole world.** Find your subnet with
`ip a` (e.g. `192.168.1.23` → subnet `192.168.1.0/24`), then:
```bash
sudo ufw allow from 192.168.1.0/24 to any port 3000 proto tcp
```

**Close a port again:**
```bash
sudo ufw status numbered                # find the rule number
sudo ufw delete <number>                # delete by number
# or delete by spec:
sudo ufw delete allow 5173/tcp
```

🚩 **Reminders**
- ufw does **not** affect `localhost`/`127.0.0.1` — same-machine browsing always works.
- **Never** `ufw allow` 5432 or 6379 (database/Redis) — that exposes your data.
- **Cloud VM?** The cloud provider has its **own** firewall (AWS "Security Group", GCP
  "firewall rule", Azure "NSG"). You must open the port **there too** — ufw alone isn't enough.

---

## 5. Reaching a service from another device

Two things must be true for your **phone** (or another laptop) to load
`http://<your-laptop-ip>:5173`:

1. 🚩 **The app must LISTEN on all interfaces (`0.0.0.0`), not just `127.0.0.1`.** "localhost
   only" means only the same machine can connect. Make each dev server listen widely:

   | Service | Localhost-only (default) | Reachable on the LAN |
   |---------|--------------------------|----------------------|
   | FastAPI | `uvicorn main:app --reload --port 8000` | `uvicorn main:app --reload --host 0.0.0.0 --port 8000` |
   | Vite (web-html / web-react) | `bun run dev` | `bun run dev --host` |
   | Bun gateway | already listens on `0.0.0.0` | (no change needed) |

2. **The firewall must allow it** (§4) — `sudo ufw allow 5173/tcp` (or the LAN-scoped form).

Then find your machine's LAN IP (`ip a` → e.g. `192.168.1.23`) and browse to
`http://192.168.1.23:5173` from the other device.

🚩 **Security:** only bind `0.0.0.0` on a **trusted** network. Dev servers run with debug on
and dev secrets — never expose them to the public internet. (For the mobile app, also update
`CORS_ORIGINS` in `.env` to include your machine's IP, e.g. `exp://192.168.1.23:19000`.)

---

## 6. 🚩 Dev · Staging · Production on the SAME Ubuntu host, one at a time

You can run all three on a single laptop **for learning/testing** — but **not at the same
time.**

🚩🚩 **THE GOLDEN RULE:** Development, Staging, and Production all use the **same ports**
(8000, 3000, 3001, 5432, 6379). **Only ONE environment may run at a time.** Starting a second
one while the first is up gives **"address already in use"** / **"port is already
allocated."** Always **fully stop the current environment before starting the next.**

🚩 A second clash hides underneath: **Development** uses the **system** PostgreSQL + Redis
(installed via `apt`, managed by `systemctl`), while **Staging/Production** run **their own**
PostgreSQL + Redis **in Docker** — both want `5432`/`6379`. So switching also means switching
**which** Postgres/Redis is running.

> 🚩 **Real-world note:** staging and production should live on **separate machines**. Running
> both on one laptop is fine for a demo, but they share the Docker project name (`idrm`) and
> data volumes (`pgdata`, `redisdata`) — so one can see the other's data unless you wipe it
> (`down -v`). Treat same-host staging+prod as throwaway testing only.

### The three environments at a glance

| | **Development** | **Staging** | **Production** |
|---|---|---|---|
| What runs it | native processes (5 terminals) | Docker Compose | Docker Compose |
| Setup script | `./scripts/setup-development-monolith.sh` | `./scripts/setup-staging.sh` | `./scripts/setup-production.sh` |
| Config file | `.env` (committed dev defaults) | `.env.staging` (git-ignored) | `.env.production` (git-ignored, **real secrets**) |
| Postgres/Redis | **system** services (`systemctl`) | **Docker** containers | **Docker** containers |
| Start | the 5 terminals (or `make dev`) | the script (`docker compose up -d`) | the script (guards + confirm) |
| Stop | `Ctrl + C` each terminal | `docker compose -f infra/docker/full-stack.yml down` | same `down` |
| Health check | `curl localhost:8000/api/v1/health` | `curl localhost:3000/api/v1/health` | via NGINX/HTTPS |

### Pre-flight you can run anytime
```bash
# "What IDRM ports are currently in use, and by what?"
sudo ss -tulpn | grep -E ':(80|3000|3001|8000|5173|5174|5432|6379)\b'
# "What Docker containers are running?"
docker compose -f infra/docker/full-stack.yml ps
```
🚩 **Before starting any environment, the relevant ports above should show NO output.**

### A. Start DEVELOPMENT (native)
```bash
# 1. Make sure no Docker stack is holding the ports:
docker compose -f infra/docker/full-stack.yml down 2>/dev/null

# 2. Start the SYSTEM database + Redis (dev uses these, not Docker):
sudo systemctl start postgresql redis-server

# 3. One-time / idempotent setup (creates conda env, DB, schema, installs deps):
./scripts/setup-development-monolith.sh

# 4. Start the stack in 5 terminals (the script prints these; or use `make dev`):
#   T1: cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000
#   T2: cd src/backend/api-gateway && bun run dev          # :3000 + :3001
#   T3: cd src/frontend/web-html  && bun run dev           # :5173
#   T4: cd src/frontend/web-react && bun run dev           # :5174
#   T5: (Post-MVP) cd src/frontend/mobile-expo && npx expo start

# 5. Verify:
curl -s localhost:8000/api/v1/health            # backend → {"status":"ok",...}
curl -s localhost:3000/api/v1/health            # via gateway → same JSON
```
🚩 Dev tip: prefer this when **editing code** — `--reload`/`--watch` give instant hot-reload,
which the Docker images do not.

### B. Switch DEVELOPMENT → STAGING
```bash
# 1. Stop all 5 dev terminals (Ctrl + C in each).
# 2. Free 5432/6379 for Docker by stopping the SYSTEM services:
sudo systemctl stop postgresql redis-server
# 3. Confirm the ports are clear (should print nothing):
sudo ss -tulpn | grep -E ':(3000|3001|8000|5173|5174|5432|6379)\b'
# 4. Bring up staging (Docker). Creates .env.staging from the example if missing:
./scripts/setup-staging.sh
# 5. Verify:
docker compose -f infra/docker/full-stack.yml ps     # services "healthy"
curl -s localhost:3000/api/v1/health
```
🚩 If step 4 says **"port is already allocated"**, a system service or dev process is still
up — re-run step 2/3. (`sudo lsof -i :5432` shows the culprit.)

### C. Switch STAGING → PRODUCTION
```bash
# 1. Take staging fully down. Add -v to also WIPE staging data volumes so prod starts clean:
docker compose -f infra/docker/full-stack.yml down -v
# 2. Ensure real production secrets exist (the script REFUSES dev defaults):
#    .env.production must NOT contain "idrm_secure_password_2024" or "change-in-production".
#    Generate a JWT secret, for example:  openssl rand -hex 32
# 3. Deploy (asks you to confirm; set ASSUME_YES=1 for unattended CI):
./scripts/setup-production.sh
# 4. Verify health, then the go-live checklist (TLS, backups, firewall, monitoring).
docker compose -f infra/docker/full-stack.yml ps
```
🚩 `setup-production.sh` **stops itself** if `.env.production` is missing or still holds dev
defaults — that's the guard working, not a bug.

### D. Switch back to DEVELOPMENT
```bash
docker compose -f infra/docker/full-stack.yml down     # stop containers, free the ports
sudo systemctl start postgresql redis-server           # bring the system DB/Redis back
sudo ss -tulpn | grep -E ':(3000|3001|8000|5173|5174)\b'   # should be empty (5432/6379 now system-owned)
./scripts/setup-development-monolith.sh                # then the 5 terminals
```

> 🚩 **Optional — use Docker for dev's data layer too.** Instead of system Postgres/Redis you
> may run just the Docker data layer for development:
> `docker compose -f infra/docker/full-stack.yml up -d postgres redis`. If you do, **don't**
> also start the system services (same 5432/6379 clash). Pick one source of Postgres/Redis.

---

## 7. Quick reference & troubleshooting

**Stop EVERYTHING (panic button):**
```bash
docker compose -f infra/docker/full-stack.yml down       # all Docker services
sudo systemctl stop postgresql redis-server              # system DB + Redis
# then Ctrl + C any native dev terminals still open
```

**"address already in use" / "port is already allocated"** — the #1 error when switching envs:
1. Find who's on the port: `sudo ss -tulpn | grep ':3000'` (or `sudo lsof -i :3000`).
2. If it's a **native** process → `Ctrl + C` its terminal, or `sudo fuser -k 3000/tcp`.
3. If it's a **Docker** container → `docker compose -f infra/docker/full-stack.yml down`.
4. If it's the **system DB/Redis** while you want Docker → `sudo systemctl stop postgresql redis-server`.
5. Re-check with step 1 (should be empty), then start your environment again.

**Useful one-liners**
```bash
sudo ss -tulpn | grep -E ':(80|3000|3001|8000|5173|5174|5432|6379)\b'   # IDRM ports in use
sudo ufw status verbose                                                  # firewall state + rules
docker compose -f infra/docker/full-stack.yml ps                         # Docker services + health
docker compose -f infra/docker/full-stack.yml logs -f backend            # follow a service's logs
ip a                                                                      # this machine's LAN IP
```

**Related docs**
- `docs/IDRM-DEVELOPMENT-GUIDE.md` — full local setup (prerequisites, conda, DB, the 5 terminals).
- `schedules/IDRM-BUILD-WORKFLOW.md` §2 — per-module verify commands (run them on this Ubuntu host).
- `scripts/setup-*.sh` — the idempotent scripts referenced above.
- `infra/docker/full-stack.yml` — the Compose file used by staging/production.
- `start-here/COMPLETE-DevSecOps-GUIDE.md` — TLS, hardening, and the production go-live checklist.
