# Observability 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/operators · Status: MVP — current · Track: Software Engineering (#17)*
> *When software is live and something goes wrong at 2 a.m. during a flood, can you tell **what** broke and
> **why**? Observability is how. This guide explains the idea, then IDRM's pragmatic MVP approach.*

---

## 1. What observability means

**Observability** is how well you can understand what a running system is doing **from the outside** — without
attaching a debugger. A system is "observable" when its signals let you answer new questions ("why are rescue
incidents slow in this district?") that you didn't hard-code in advance. For disaster software, this is a
reliability *and* a mission concern.

It's built from **three pillars** plus health signals.

---

## 2. The three pillars

- **Logs** — timestamped records of events ("incident 3f2a accepted by user X"). Answer *what happened*.
- **Metrics** — numbers measured over time (requests/sec, error rate, incidents created per hour). Answer *how
  much / how often*, and drive dashboards and alerts.
- **Traces** — the path of a single request across the system, with timing at each step. Answer *where the time
  went / where it failed*.

| Pillar | Answers | Example question |
|--------|---------|------------------|
| Logs | what happened | "why did this upload fail?" |
| Metrics | how much/often | "is the error rate rising?" |
| Traces | where/why slow | "which step made this request slow?" |

---

## 3. Health signals

Every service exposes small endpoints so operators and automation can check it:

- **`/health`** (liveness) — "am I alive?"
- **`/ready`** (readiness) — "am I ready to serve traffic (DB reachable, etc.)?"
- **`/metrics`** — the numbers, in a format a metrics system can scrape.

---

## 4. IDRM's approach (MVP vs FFP)

- **MVP (pragmatic):** **structured logs** (JSON, with levels, **no personal data, no tokens**), the `/health`,
  `/ready`, `/metrics` endpoints, and basic error reporting. Deliberately lightweight — no heavy stack yet.
- **FFP (full):** Prometheus (metrics) + Grafana (dashboards), OpenTelemetry → Jaeger/Zipkin (tracing),
  centralised logs (Loki/ELK), SLO-based alerting, and client-side **RUM** (Real User Monitoring). Detail:
  [`../../instructions/observability.md`](../../instructions/observability.md).

**Golden rule:** logs and metrics must **never** contain passwords, tokens, or personal data — privacy and
security don't stop at observability (see [Secure Coding 101](secure-coding-101.md)).

---

## 5. Tie it back to the mission

Observability isn't just uptime — it measures whether IDRM is *working*. The MVP's targets (response time
12h→2h, fulfilment 60%→80%) are, in the end, **metrics**. A dashboard of the incident funnel (created → accepted
→ completed → verified) turns the mission itself into something you can watch and improve.

---

## 6. Mastery check

1. Define **observability** in your own words.
2. Name the **three pillars** and what each answers.
3. Explain `/health` vs `/ready` vs `/metrics`.
4. Contrast IDRM's **MVP** vs **FFP** observability.
5. State the golden rule about what must never appear in logs.

---

## 7. Go deeper

- OpenTelemetry — opentelemetry.io/docs · Prometheus — prometheus.io/docs · Grafana — grafana.com/docs
- Google SRE (SLIs/SLOs) — sre.google/books · IDRM observability spoke: [`../../instructions/observability.md`](../../instructions/observability.md)

---
*Next:* IAM 101 (Security track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
