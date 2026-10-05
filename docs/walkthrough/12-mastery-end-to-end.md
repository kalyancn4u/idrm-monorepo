# Chapter 12 — Mastery: End-to-End & Exercises

*One request traced through every layer, then projects and a self-check to lock it in.*

**By the end of this chapter you will be able to:** narrate a full request through the
codebase from memory, extend the system confidently, and assess your own understanding.

Files: all of [`services/monolith/app/`](../../services/monolith/app/) — this chapter connects everything.

---

## The full journey of one request

Let's follow a **provider accepting a help request** —
`POST /api/v1/incidents/{id}/accept` — from the wire to the reply. Match each step to its
chapter.[1]

<!-- _class: diagram-text -->

```text
 1. Middleware   main.py stamps X-Request-Id, logs request.start                    (Ch 3-4)
 2. Router       incidents/router.accept() is matched                               (Ch 2)
 3. Guards       get_current_claims verifies the RS256 token → {sub, role}          (Ch 6)
                 (role must be "provider"; get_db opens the request's session)
 4. Resolve org  OrganizationService.resolve_active_for_owner(sub) → the provider's
                 OWN verified org (403 if none/unverified) — never from the body     (Ch 7,9)
 5. Load         IncidentService.get(id) → 404 if missing                           (Ch 7)
 6. Rules        perform_transition("accept"): role_allowed ✓ · not already
                 accepted ✓ · can_transition(created/approved) ✓ · critical needs
                 approval ✓ · sets status=accepted, assigned_organization_id=org.id  (Ch 7)
 7. Persist      repository.add_update(...) flushes the timeline row                 (Ch 5)
 8. Compose      _notify_requester(...) + AuditService.record("incident.accept")     (Ch 9)
 9. Commit       get_db commits the whole unit of work on success                    (Ch 5)
10. Respond      to_response(incident) → a bare IncidentResponse object; JSON        (Ch 10)
11. Middleware   logs request.end (status, latency); echoes X-Request-Id             (Ch 3-4)
```

Every arrow you learned in Chapter 1 just executed. If you can narrate these eleven steps,
you understand the system.[2]

> **Footnotes**
>
> - **[1]** Notice how the layers stay in their lanes: the router orchestrates, the guards authenticate, the service decides, the repository persists, and only `get_db` commits. No layer reached past its neighbour.
> - **[2]** If any step is fuzzy, its chapter is one click away. The whole design exists so this narration is *possible* — a tangled system can't be told as a clean story.

---

## A second trace — the guest path

Now the simplest meaningful flow: **a guest raising an emergency** —
`POST /api/v1/incidents` with no token.[1]

```text
1. Guards    get_optional_claims → None (no token = guest; a bad token still 401s)   (Ch 6)
2. Router    a provider would be 403 here; a guest is allowed                        (Ch 7)
3. Service   create(data, requester_id=None) → status "created", a tracking_token    (Ch 7)
4. Rate      the guest create limit (5/min) applies, stricter than signed-in         (Ch 6)
5. Respond   201 Created; the bare object includes the tracking_token to follow up   (Ch 10)
```

> **Footnotes**
>
> - **[1]** The guest path is the humane core of the product: in a disaster, someone may have no account. The design lets them ask for help in one call and still follow it — via the tracking token — without ever creating an account.

---

## Extension exercises (learn by changing it)

Each exercise touches the layers you now know. Start small.[1]

1. **Add a list filter.** Add `?assigned_organization_id=` to `GET /incidents`: extend the
   repository `list`, the service, and the router param — then the OpenAPI (Ch 10). *(The
   repository already accepts it internally; wire it to the query.)*
2. **Add an endpoint.** `GET /incidents/{id}/timeline-summary` returning counts per status
   from the `incident_updates` — a read-only service method + a router + a test. *(Ch 2,
   5, 11.)*
3. **Add a module.** Sketch a `feedback` module (models · schemas · repository · service ·
   router) for post-verification comments, composing audit at the router edge. *(Ch 2, 9.)*
4. **Implement F5-B's cousin** — a real reverse-geocoder behind `geo.reverse_geocode`
   (offline dataset), leaving the seam unchanged. *(Ch 8.)*

⚠️ **Pitfall:** for each, keep the layers honest — no SQL in the router, no HTTP in the
service — and add the test *and* the OpenAPI entry. That discipline is the whole point.[2]

> **Footnotes**
>
> - **[1]** The best way to prove mastery is a small, correct change that respects the architecture. Each exercise is deliberately a *vertical slice* — it forces you through router → service → repository → schema → test → contract.
> - **[2]** Every change should leave `make qa` green and the code = contract = schema in agreement (Ch 10). A feature isn't done when it works once; it's done when it's tested and documented.

---

## Where this grows — the FFP seams

You've seen the seams designed for the future, each add-able **without a rewrite**:[1]

| MVP now | FFP trigger | Where it plugs in |
|---|---|---|
| in-process rate limit | multiple app instances | APISIX gateway (Ch 6) |
| pull-model notifications | need instant push | broker + push behind `notify` (Ch 9) |
| offline reverse-geocode | street-level labels | real geocoder behind `geo` (Ch 8) |
| modular monolith | scale/ownership | extract a module → microservice (Strangler Fig, Ch 1) |
| FAQ chatbot stub | real NL help | an intelligence engine behind `/notifications/chat` |

> **Footnotes**
>
> - **[1]** Each row is a ***seam*** — a clean interface the current simple thing hides behind, so the powerful thing can replace it later. Designing seams up front is what makes "evolve, don't rewrite" real rather than aspirational. The rationale for each deferral is an ADR (`docs/mvp/21`).

---

## Self-assessment — can you…?

Tick these honestly; each maps to a chapter you can revisit.[1]

- [ ] Draw the request pipeline and name each layer's job. *(Ch 1–2)*
- [ ] Explain why settings are cached and what breaks if tests import before setting env. *(Ch 3)*
- [ ] Say what makes a log line queryable and how a secret is kept out of it. *(Ch 4)*
- [ ] Describe the Unit of Work and why a repository must not `commit` (and the one exception). *(Ch 5–6)*
- [ ] Verify an RS256 token by hand-waving the key flow; distinguish guest vs bad-token. *(Ch 6)*
- [ ] Recite the 8 incident states and what `single-claim` / `not_assigned` protect. *(Ch 7)*
- [ ] Write a `ST_DWithin` query and explain the geography cast + lat/lng order. *(Ch 8)*
- [ ] Explain router-edge composition and why the audit trail has no write API. *(Ch 9)*
- [ ] Name the three response shapes and why `sort` is whitelisted. *(Ch 10)*
- [ ] Say which tests run without a database, and what "done" means here. *(Ch 11)*

> **Footnotes**
>
> - **[1]** If you can do all ten, you can not only *run* IDRM — you can *change* it safely, review someone else's change, and explain the design to the next newcomer. That is mastery.

---

## Recap & where to go next

- One request touches **every layer in order**; you can now narrate it — and the guest
  path — end to end.
- You can **extend** the system with vertical slices that keep the layers honest and the
  contract in sync.
- The **FFP seams** let it grow without a rewrite; the **self-assessment** is your map back
  to any shaky spot.

🛠️ **Try it (capstone):** do Exercise 1 (add `assigned_organization_id` to the incidents
list), including the test and the OpenAPI entry, and run `make qa`. When it's green,
you've shipped a change through the whole architecture.

**Where to read on:** the product specs in [`docs/mvp/`](../mvp/), the decisions in
[`21-architecture-decisions.md`](../mvp/21-architecture-decisions.md), the roadmap
[`27`](../mvp/27-implementation-roadmap.md), and what's left in
[`PENDING.md`](../../PENDING.md). Thanks for reading — now go build.
