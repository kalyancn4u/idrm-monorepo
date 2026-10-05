# Event-Driven Architecture 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: **FFP** — next-phase · Track: Software Engineering (#14)*
> *A different way for parts of a system to talk: not by calling each other directly, but by announcing that
> things **happened**. This guide explains it and where IDRM uses it — which is **FFP, not the MVP**.*

---

## 1. Two ways for software to communicate

- **Request/response (synchronous)** — A calls B and waits for the answer. Simple, direct. **This is the IDRM
  MVP** — the FastAPI monolith handles a request start to finish.
- **Event-driven (asynchronous)** — A announces *"an incident was created"* and moves on; other parts react in
  their own time. No waiting, looser coupling.

An **event** is a record that something happened, in the past tense: `incident_created`, `incident_completed`.

---

## 2. The building blocks

- **Producer** — emits an event ("this happened").
- **Consumer** — subscribes and reacts ("when that happens, do this").
- **Broker / event bus** — the middle layer that carries events from producers to consumers (e.g. Redis Streams,
  RabbitMQ, Kafka).

Producers and consumers don't know about each other — they only know the event. That **decoupling** is the whole
point: you can add a new reaction (send an SMS when an incident is verified) without touching the producer.

---

## 3. Why (and when) it's worth it

**Benefits:** loose coupling, scalability (consumers work at their own pace), resilience (a slow consumer doesn't
block the producer), and easy extension.

**Costs:** it's harder to reason about ("where did this happen?"), needs a broker to run, and requires care around
ordering, duplicates, and failures — hence patterns like **idempotent consumers** (safe to process the same event
twice) and **dead-letter queues** (a holding pen for events that keep failing).

> Rule: don't reach for events until synchronous simplicity actually hurts. That's exactly why IDRM's **MVP stays
> synchronous** and defers this to FFP.

---

## 4. IDRM's phasing

- **MVP:** synchronous. An incident's lifecycle transitions happen inline; notifications are direct. No broker.
- **FFP:** an **event backbone** — Redis Streams first, then RabbitMQ/Kafka on a trigger — powers real-time COP
  updates, multi-service choreography, analytics, and cross-agency integration. Detail:
  [`../../instructions/caching-messaging.md`](../../instructions/caching-messaging.md) and
  [`../../idrm-ffp-docs/81-ops-messaging-and-async.md`](../../idrm-ffp-docs/81-ops-messaging-and-async.md).

---

## 5. Mastery check

1. Contrast synchronous request/response with event-driven communication.
2. Define **event**, **producer**, **consumer**, **broker**.
3. Explain the **decoupling** benefit with an IDRM example.
4. Name two costs and the patterns that address them (idempotency, DLQ).
5. Say why IDRM's MVP is synchronous and what FFP adds.

---

## 6. Go deeper

- Enterprise Integration Patterns — enterpriseintegrationpatterns.com · Kafka — kafka.apache.org · RabbitMQ — rabbitmq.com
- Related: [Observability 101](observability-101.md) · caching/messaging spoke [`../../instructions/caching-messaging.md`](../../instructions/caching-messaging.md)

---
*Next:* [Docker 101](docker-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
