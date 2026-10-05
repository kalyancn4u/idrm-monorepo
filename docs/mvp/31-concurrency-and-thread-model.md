# IDRM MVP — Concurrency & Thread Model (Low-Level Design)

> *Type: Document (LLD / deep-dive) · Audience: complete novices → backend & ops engineers · Status: MVP — current*
> *The deep-dive behind [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §6. It answers one question
> precisely: **on a single Ubuntu box, how many "things at once" should IDRM run — and how do we keep total CPU at
> or below ~70% so there is always headroom for a disaster-day surge?** Everything here is a **parameterized
> formula** anchored to the ops baseline (**4 vCPU / 16 GB**, [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md)),
> so the numbers auto-recompute for a bigger or smaller server. Numbers are **engineering starting points, confirmed
> by load testing** (§7) — an LLD is a plan to be measured, not a guess to be trusted.*

---

## 1. The problem, in plain terms

A web server must do **many things at once**: while it waits for the database to answer one person, it should be
serving the next. During a disaster, requests **surge** — hundreds of citizens and responders hit IDRM in minutes.
If the server tries to do *too* much at once it slows to a crawl or crashes; if it does *too little* at once it
wastes the machine and makes people wait. **Concurrency sizing** is choosing that "how many at once" number *on
purpose*, with enough **headroom** left over that a surge doesn't tip the box over.

Our rule, from you: **never plan to exceed ~70 % CPU.** The spare 30 % is not waste — it is the shock-absorber
that keeps IDRM responsive exactly when it matters most.

> **Words defined once (you'll meet them throughout):**
> - **vCPU (virtual CPU) / core** — one "worker brain" the server can compute with. 4 vCPU ≈ four things truly
>   simultaneously.
> - **Process** — a running program with its own memory (a *uvicorn worker* is a process). **Thread** — a lighter
>   worker inside a process that shares its memory. **Coroutine** — an even lighter "task" the async event loop
>   juggles.
> - **I/O-bound work** — work that mostly *waits* (for the database, for MinIO, for the network). Cheap on CPU.
> - **CPU-bound work** — work that mostly *computes* (hashing a password, shrinking a photo). Expensive on CPU.
> - **Blocking** — code that stops its thread until it finishes; blocking the async loop is the cardinal sin
>   (it freezes everyone else), so blocking work is pushed onto separate threads.

New to measuring server load? [`performance-testing-101.md`](../../guides/mvp/learn/performance-testing-101.md) and
[`linux-101.md`](../../guides/mvp/learn/linux-101.md) are the companion primers.

## 2. How FastAPI actually runs work

IDRM is a **FastAPI** app served by **uvicorn** (with a Gunicorn process manager). It runs work in three tiers —
knowing them is the whole game:

1. **Worker processes** — several identical copies of the app (uvicorn workers). Each is a real OS process on its
   own core, giving both parallelism and resilience (if one dies, others serve).
2. **The async event loop** (one per worker) — juggles many **I/O-bound** requests *concurrently* on a single
   thread: while request A waits for PostgreSQL, the loop serves B, C, D… This is why a *small* number of workers
   can hold a *large* number of waiting requests cheaply.
3. **A thread pool** (per worker) — for **blocking** work that would otherwise freeze the loop (password hashing,
   image processing). The loop hands these off to threads and stays free.

> **The golden rule that shapes every number below:** keep the event loop **free**. I/O waits on the loop; heavy
> computing goes to the bounded thread pool. Get this wrong and one blurry-photo upload freezes every other user.

## 3. The IDRM workload — classify every activity

You asked for the thread budget to account for *all* the activities. Here they are, sorted by the tier they belong
to:

| Activity | Kind | Runs where | Notes |
|---|---|---|---|
| Most API calls: read/write incidents, users, orgs, proximity search | **I/O-bound** | event loop (async DB driver) | the bulk of traffic; cheap per request |
| MinIO uploads/downloads (photos, proof) | **I/O-bound** | event loop (async) / small I/O threads | bytes go to MinIO, not the DB |
| **Password hashing** (bcrypt cost-12, login/register) | **CPU-bound** | bounded CPU thread pool | ~100–250 ms of pure CPU each |
| **Image processing** (resize ≤1920 px, blur check, EXIF strip) | **CPU-bound** | bounded CPU thread pool | short but heavy bursts |
| GeoJSON building / report aggregation | **CPU-bound (light)** | CPU pool / loop | small in the MVP |
| **Background jobs**: notification send + retry, report generation, image post-processing, expired-session/token cleanup | **mixed** | in-process scheduler + small pool | APScheduler / ThreadPoolExecutor (no Redis/broker in MVP) |
| Serving static files + HTML templates | **I/O-bound (front-end)** | reverse proxy (static) + loop (templates) | proxy offloads static files |
| **Chatbot / ML** | — | **none in the MVP** | zero threads reserved → **FFP seam** (§8) |

## 4. The co-tenancy reality (why the app can't have all the cores)

In the MVP, **one Ubuntu box hosts everything** — FastAPI **and** PostgreSQL **and** MinIO **and** the OS (no Redis,
no separate DB server; [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md)). So the ~70 %
CPU ceiling is a **whole-box** budget that must be **shared**. PostgreSQL in particular does real work — the
geospatial "who's nearby?" queries — and deserves a healthy slice.

## 5. The formula (parameterized; anchored to 4 vCPU / 16 GB)

Let **`C`** = vCPU count (default **4**), **`M`** = RAM in GB (default **16**), and the CPU ceiling
**`U = 0.70`** (30 % headroom). All figures below are *fractions of the whole box*, then rounded to whole
workers/threads.

**Step 1 — the whole-box CPU budget at peak:**
```
B_cpu = U × C            = 0.70 × 4 = 2.8 vCPU-equivalents (the most we plan to use)
```

**Step 2 — split that budget across the co-tenants (starting split, tune by measurement):**
```
PostgreSQL + PostGIS :  0.30 × C   = 1.2      (heavy geospatial queries)
MinIO + OS + misc    :  0.15 × C   = 0.6
FastAPI app (all of it): 0.25 × C  = 1.0      = B_cpu − 1.2 − 0.6
```

**Step 3 — size the app from its 1.0-vCPU slice:**
```
Uvicorn workers        W  = max(2, round(C / 2))          = 2
   → 2 processes: redundancy + parallel CPU; they idle-wait on I/O most of the time,
     so their AVERAGE CPU sits well inside the 1.0-vCPU app slice.

CPU-bound concurrency  L  = max(1, floor(0.25 × C))       = 1   (enforced by a semaphore)
   → at most ~1 heavy compute (bcrypt / image) at a time, so CPU spikes never blow past 70%.
     Extra heavy tasks queue for a few milliseconds rather than stampeding the cores.

Background pool        Bg = 2 threads (low priority)      = 2
   → notifications, report gen, cleanup; scheduled to avoid the request peak.

DB connection pool     P  = per-worker connections        = 5
   → total app DB connections = W × P + Bg = 2×5 + 2 = 12  (≪ Postgres max_connections 100).
```

**Step 4 — sanity-check memory (`M`):**
```
Postgres shared_buffers ≈ 0.25 × M = 4 GB   ·  effective_cache_size ≈ 0.50 × M = 8 GB
MinIO ≈ 0.5–1 GB   ·  uvicorn workers ≈ W × ~300 MB = 0.6 GB   ·  OS + page cache: the rest
→ comfortably inside 16 GB with room to spare.
```

> **Why these splits and not others?** They encode three ideas: (1) the database is a first-class CPU consumer, not
> an afterthought; (2) an I/O-bound app needs *few* workers but *disciplined* limits on CPU-bound bursts; (3) every
> number leaves headroom. They are **defaults to measure**, not laws — §7 says how to confirm and adjust them.

## 6. Worked examples (the formula in action)

**Baseline — 4 vCPU / 16 GB (the anchor):**

| Knob | Value | Meaning |
|---|---|---|
| CPU ceiling `B_cpu` | 2.8 vCPU | never plan past this |
| Uvicorn workers `W` | **2** | two app processes |
| CPU-bound limit `L` | **1** | ≤1 heavy compute at once |
| Background threads `Bg` | **2** | jobs, off-peak |
| DB connections total | **12** | 2×5 + 2 |
| Postgres `shared_buffers` | **4 GB** | 25 % of RAM |

**Scaling up — 8 vCPU / 32 GB (same formula, no rethink):**

| Knob | Value |
|---|---|
| CPU ceiling `B_cpu` | 5.6 vCPU |
| Uvicorn workers `W = round(8/2)` | **4** |
| CPU-bound limit `L = floor(0.25×8)` | **2** |
| DB connections total `4×5 + 2` | **22** |
| Postgres `shared_buffers` | **8 GB** |

This is exactly why we chose a *formula* over fixed numbers (your Round-1 decision): move the box, turn the crank,
get consistent, defensible sizing — **no surprises**.

## 7. Guardrails — how we confirm ≤ 70 % (an LLD is measured, not assumed)

Before trusting any number above, we **load-test** (see [`70-quality-test-strategy.md`](70-quality-test-strategy.md)
and [`performance-testing-101.md`](../../guides/mvp/learn/performance-testing-101.md)):

- **Drive** realistic traffic (a surge of incident creates, proximity searches, uploads) with a tool like k6 or
  Locust.
- **Watch:** total CPU % (must stay ≤ 70 at target peak), **p95 latency** (95 % of requests faster than X),
  **event-loop lag** (proof the loop isn't blocked), and **DB pool saturation** (are we starved of connections?).
- **Tune the knobs** in order: raise/lower `W`, the CPU-bound limit `L`, the DB pool `P`; move heavy work to the
  background; offload static files to the reverse proxy. Re-measure. Repeat until peak load fits under 70 % with
  healthy latency.

> **Timeouts & retries (the concurrency safety valves, from [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) §3):**
> clients set a sensible request **timeout**; **reads** (`GET`) are safe to retry, **writes are not auto-retried**
> (an idempotency key guards double-submits on flaky field networks). This prevents a slow spell from snowballing
> into a pile-up.

## 8. The FFP seam (what changes when we outgrow one box)

Everything above is deliberately a **single-box, in-process** design — simple, and enough for the MVP. The growth
path is already designed-in (habit #5), triggered only when load *measurably* demands it:

- **Background work → out of process:** the in-process scheduler/pool becomes **Redis Streams → RabbitMQ/Kafka
  workers** ([`21-architecture-decisions.md`](21-architecture-decisions.md); the FFP messaging doc).
- **Horizontal scale:** run many app instances behind the **APISIX** gateway; PostgreSQL and MinIO move to their
  own hosts, freeing whole cores.
- **Chatbot / ML get their own service** with their *own* CPU/GPU budget — which is why the MVP reserves **zero**
  threads for them now (honest sizing today, clean insertion later). The design memos are Task M
  ([`../../archive/instructions.txt`](../../archive/instructions.txt) §15).

---

*Related:* roadmap [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §6 · architecture [`20-architecture-system.md`](20-architecture-system.md) ·
ops/sizing [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md) · data flow [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) ·
decisions [`21-architecture-decisions.md`](21-architecture-decisions.md) · testing [`70-quality-test-strategy.md`](70-quality-test-strategy.md) ·
primers [`performance-testing-101.md`](../../guides/mvp/learn/performance-testing-101.md) · [`tech-stack-101.md`](../../guides/mvp/learn/tech-stack-101.md).
