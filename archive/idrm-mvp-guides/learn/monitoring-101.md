# Monitoring 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/ops · Status: MVP-aware (deepens in FFP) · Track: Operations (#35)*
> *Monitoring is watching a live system's health and being told when something's wrong — before users suffer.
> It's the operational sibling of [Observability 101](observability-101.md); read that first.*

---

## 1. Monitoring vs observability (don't confuse them)

- **Monitoring** — watching **known** signals and **alerting** when they cross a threshold ("CPU > 90%", "error
  rate > 1%"). It answers questions you *already knew to ask*.
- **Observability** — the property that lets you investigate **new**, unforeseen questions from rich data.

You need both: monitoring tells you *something is wrong*; observability helps you find *why*.

---

## 2. What to monitor: the golden signals

Google's SRE "four golden signals" are a great default:

- **Latency** — how long requests take.
- **Traffic** — how much demand (requests/sec).
- **Errors** — the rate of failed requests.
- **Saturation** — how "full" resources are (CPU, memory, disk, DB connections).

Plus, for IDRM, **mission signals**: incidents created/accepted/completed per hour, time-in-state — is the
*response* actually working?

---

## 3. Alerting done right

- **Thresholds → alerts** — when a signal breaches a limit, notify a human.
- **Alert on symptoms, not noise** — page someone when *users are affected* (high error rate), not for every
  transient blip. Too many alerts cause **alert fatigue** and missed real ones.
- **Dashboards** — at-a-glance health (e.g. Grafana), so trends are visible before they become incidents.

---

## 4. IDRM context

- **MVP:** pragmatic — the `/health`, `/ready`, `/metrics` endpoints ([Observability 101](observability-101.md)),
  basic threshold alerts (service down, disk full, error spike), and a simple dashboard. Native systemd services
  are watched with `systemctl`/`journalctl` ([Linux 101](linux-101.md)).
- **FFP:** Prometheus (metrics) + Grafana (dashboards) + Alertmanager, SLO-based alerting, and per-service
  monitoring across the distributed system. See [`../../instructions/observability.md`](../../instructions/observability.md).

---

## 5. Mastery check

1. Distinguish **monitoring** from **observability**.
2. Name the **four golden signals** and an IDRM **mission signal**.
3. Explain "alert on symptoms" and **alert fatigue**.
4. Say what dashboards are for.
5. State IDRM's MVP vs FFP monitoring approach.

---

## 6. Go deeper

- Google SRE — Monitoring & the golden signals — sre.google/books · Prometheus — prometheus.io · Grafana — grafana.com
- Related: [Observability 101](observability-101.md) · [Incident Response 101](incident-response-101.md) · [SRE 101](sre-101.md)

---
*Next:* [Incident Response 101](incident-response-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
