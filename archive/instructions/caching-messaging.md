# IDRM Instructions — Caching & Messaging

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Phase rule:** **all of this is FFP.** MVP has **no Redis, no brokers** (sessions in Postgres, synchronous flows).

## Caching (FFP)
- **Redis** for cache / sessions-at-scale / rate-limit counters / ephemeral derived data.
- Cache is **never the source of truth** (that's Postgres/PostGIS — [`data-stores.md`](data-stores.md)).
  Model **TTLs + explicit invalidation**; prefer cache-aside; guard against stampedes.
- Gateway response caching (`proxy-cache`) covers cacheable GETs — see [`api-gateway.md`](api-gateway.md).

## Messaging / async (FFP, phased on a trigger)
- **Redis Streams** first for lightweight events/workers.
- **RabbitMQ** for reliable routing/work-queues (per-message ack, DLQ); **Kafka** for high-throughput,
  replayable event logs / analytics. Choose **per workload**, not dogmatically.
- Patterns: idempotent consumers, outbox for reliable publish, dead-letter queues, backpressure.
- Real-time delivery (COP, tasking, alerts) via WebSocket/SSE through the **edge/BFF** over this backbone.

## Offline-first (RN field client)
- Local queue + **background sync**; writes are **idempotent** and reconcile against server-authoritative
  state on reconnect. Conflicts resolve server-side.

## Canonical docs
- [`../idrm-ffp-docs/81-ops-messaging-and-async.md`](../idrm-ffp-docs/81-ops-messaging-and-async.md)
- [`../idrm-ffp-docs/20-architecture-system.md`](../idrm-ffp-docs/20-architecture-system.md)

## Trusted external references
- Redis — redis.io/docs · Redis Streams — redis.io/docs/data-types/streams
- RabbitMQ — rabbitmq.com/docs · Apache Kafka — kafka.apache.org/documentation
- Enterprise Integration Patterns — enterpriseintegrationpatterns.com · Transactional Outbox (microservices.io)
