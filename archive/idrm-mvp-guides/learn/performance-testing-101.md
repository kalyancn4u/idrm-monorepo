# Performance Testing 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/QA · Status: **FFP** — next-phase · Track: Quality (#28)*
> *Software that works for one user can collapse under a thousand. Performance testing measures how the system
> behaves under load — vital for IDRM, where load spikes exactly when a disaster hits.*

---

## 1. Why performance is a disaster-response concern

A disaster causes a **surge**: thousands of citizens reporting at once, coordinators hammering the map. If IDRM
slows or falls over precisely then, it fails when it matters most. **Performance testing** proves the system holds
up *before* the real surge — a reliability and a mission requirement.

---

## 2. The kinds of performance test

- **Load test** — normal-to-expected traffic: does it stay fast at, say, 1,000 concurrent users?
- **Stress test** — push past the limit to find the **breaking point** and how it fails (gracefully or
  catastrophically?).
- **Spike test** — a sudden jump (a disaster alert goes out) — can it absorb the shock?
- **Soak test** — sustained load over hours/days — reveals slow leaks (memory, connections).

---

## 3. What you measure

- **Latency / response time** — how long a request takes (often the **p95/p99** — the slowest 5%/1%, not just the
  average, because tail latency is what users feel).
- **Throughput** — requests handled per second.
- **Error rate** — the share of failed requests under load.
- **Resource use** — CPU, memory, DB connections.

Always test against a **target**: e.g. "p95 under 500 ms at 1,000 concurrent users."

---

## 4. IDRM context

- **MVP:** the modular monolith is sized for the pilot scale (2 states, 10k+ users). Basic load checks confirm it
  meets the pilot targets; deep performance engineering isn't the MVP's focus.
- **FFP:** as IDRM scales nationally, formal load/stress/spike/soak testing guides capacity, autoscaling, caching
  ([caching/messaging spoke](../../instructions/caching-messaging.md)), and the selective move to microservices.
  This is also where **map/geo-query performance** (PostGIS indexing, marker clustering) gets tuned.
- Common tools: **k6**, **Locust**, JMeter.

> Tie it back to the mission: the MVP's "response time 12h → 2h" target is an *operational* metric; performance
> testing protects the *technical* response time that underlies it.

---

## 5. Mastery check

1. Explain why performance matters most during a disaster surge.
2. Distinguish load, stress, spike, and soak tests.
3. Define latency (and why **p95/p99** beat the average), throughput, error rate.
4. Explain why tests need a concrete target.
5. State IDRM's MVP vs FFP performance posture, and name a tool.

---

## 6. Go deeper

- k6 — k6.io/docs · Locust — locust.io · Google SRE (load/latency) — sre.google/books
- Related: [Observability 101](observability-101.md) · [Testing 101](testing-101.md) · [PostgreSQL/PostGIS 101](postgresql-postgis-101.md)

---
*Next:* [Security Testing 101](security-testing-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
