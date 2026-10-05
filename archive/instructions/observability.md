# IDRM Instructions — Observability

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Phase rule:** MVP = pragmatic logs + health endpoints. Deep distributed observability = **FFP**.

## The three pillars (+ client)
- **Metrics:** Prometheus scrapes per-service `/metrics`; dashboards in **Grafana**. Track the mission funnel
  (report → accept → complete → verify) and response/fulfilment SLAs.
- **Tracing:** **OpenTelemetry** SDKs → Jaeger / Zipkin / SkyWalking. Propagate a correlation/trace id from the
  gateway through services.
- **Logs:** **structured** (JSON, levels, **no PII, no tokens**) → Loki / ELK / ClickHouse.
- **Client (FFP):** RUM + error tracking (Core Web Vitals: LCP/CLS/INP; key funnels) — see doc 61 §18.

## MVP vs FFP
- **MVP:** structured app logs, `/health` + `/ready` + `/metrics` endpoints, basic error reporting. No heavy stack.
- **FFP:** gateway-level logging/tracing/**traffic-mirroring** feed the same backbone; alerting on SLOs;
  distributed tracing across extracted services.

## Rules
- Every service exposes health + metrics. Every request is traceable by id. Logs are searchable and PII-safe.
- Alerts map to **SLOs**, not raw noise; dashboards answer "is the mission working?" first.

## Canonical docs
- [`../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../idrm-mvp-docs/80-ops-deployment-and-operations.md)
- [`../idrm-ffp-docs/80-ops-platform-and-deployment.md`](../idrm-ffp-docs/80-ops-platform-and-deployment.md)
- Health endpoints & jobs: [`backend-services.md`](backend-services.md)

## Trusted external references
- OpenTelemetry — opentelemetry.io/docs · Prometheus — prometheus.io/docs · Grafana — grafana.com/docs
- Grafana Loki — grafana.com/oss/loki · Jaeger — jaegertracing.io · SkyWalking — skywalking.apache.org
- Google SRE (SLI/SLO/error budgets) — sre.google/books · Core Web Vitals — web.dev/vitals
