# Chapter 7 — The Incident Lifecycle

*The eight states at the heart of the domain, and the rules that guard every move.*

**By the end of this chapter you will be able to:** name the eight incident states, read
the transition table, explain single-claim / critical-approval / ownership, and say why
modeling this as an explicit state machine prevents whole classes of bugs.

Files: [`incidents/lifecycle.py`](../../code/app/modules/incidents/lifecycle.py),
[`incidents/service.py`](../../code/app/modules/incidents/service.py),
[`incidents/router.py`](../../code/app/modules/incidents/router.py).

---

## A help request has a life

An incident is never just "open" or "closed." It moves through a small, strict set of
**states**, and only certain moves are legal:[1]

<!-- _class: diagram-text -->

```text
                 ┌── reject ──▶ rejected
   created ──────┤
      │          └── approve ─▶ approved
      │                              │
      │   (accept / assign)          │ (accept / assign)
      ▼                              ▼
   accepted ◀──────────────────────-┘
      │
      │ start
      ▼
  in_progress ── complete ─▶ completed ── verify ─▶ verified
      │
      └───────── cancel ─▶ cancelled     (cancel also allowed from created/approved/accepted)
```

Eight states in all: **created, approved, accepted, in_progress, completed, verified,
cancelled, rejected.**[2]

> **Footnotes**
>
> - **[1]** A ***state machine*** models a thing as a set of states plus the legal transitions between them. Making it explicit means "complete before accept" is *impossible by construction*, not something you hope every code path remembers to check.
> - **[2]** This is the **lean** MVP lifecycle. Richer states (disputed, auto-close) are deferred to the FFP. The eight here cover the real flow: raise → (approve if critical) → a provider claims → work → completes → the requester verifies; with cancel/reject as the exits.

---

## The rules are pure data

The whole machine is two dictionaries and three tiny functions — **no database, no
framework** — so it is trivially unit-testable.[1]

```python
# app/modules/incidents/lifecycle.py (trimmed)
TRANSITIONS = {   # action -> (allowed from-states, resulting to-state)
    "approve": (frozenset({S.created}), S.approved),
    "accept":  (frozenset({S.created, S.approved}), S.accepted),
    "start":   (frozenset({S.accepted}), S.in_progress),
    "complete":(frozenset({S.in_progress}), S.completed),
    "verify":  (frozenset({S.completed}), S.verified),
    "cancel":  (frozenset({S.created, S.approved, S.accepted, S.in_progress}), S.cancelled),
    ...
}
ACTION_ROLES = {  # action -> the roles permitted to perform it
    "accept": frozenset({"provider"}), "verify": frozenset({"citizen"}),
    "approve": frozenset({"coordinator", "admin"}), ...
}
```

🧠 **Nuance:** transitions and *who may perform them* are separate tables. "Is this move
legal?" and "may this role do it?" are different questions with different answers.[2]

> **Footnotes**
>
> - **[1]** Because `lifecycle.py` imports nothing heavy, its unit tests **actually run on any machine** — no PostgreSQL needed. Pulling the rules out of the service into pure data is what makes that possible (the same trick as `geo.py`, Ch 8).
> - **[2]** Data-driven rules beat scattered `if` chains: to see every legal move you read one table, not ten functions. Adding a state later is a table edit plus tests — the enforcement code below doesn't change.

---

## Three helpers read the tables

```python
# app/modules/incidents/lifecycle.py
def can_transition(action, current) -> bool:  return current in TRANSITIONS.get(action, (frozenset(),))[0]
def next_status(action):                      return TRANSITIONS[action][1]
def role_allowed(action, role) -> bool:       return role in ACTION_ROLES.get(action, frozenset())
```

These are the *only* things the service needs to ask about legality — everything else is
domain policy layered on top.[1]

> **Footnotes**
>
> - **[1]** Small, named, pure functions are self-documenting and each is one-line to test. `next_status` assumes the caller already validated with `can_transition` — a common, safe split of "check" from "apply."

---

## `perform_transition` — the guarded move

The service applies one transition, running the checks **in a deliberate order** before
touching state:[1]

```python
# app/modules/incidents/service.py (trimmed, order preserved)
if not role_allowed(action, actor_role):                 raise AppError(403, "forbidden", ...)
if action in {"accept","assign"} and incident.status == accepted:
    raise AppError(409, "already_accepted", ...)         # single-claim: first provider wins
if not can_transition(action, incident.status):          raise AppError(409, "invalid_transition", ...)
if action in {"accept","assign"} and priority==critical and status==created:
    raise AppError(409, "invalid_transition", "Critical requests require coordinator approval first.")
if actor_role=="citizen" and action in {"verify","cancel"} and incident.requester_id != actor_id:
    raise AppError(403, "forbidden", ...)                # citizen ownership
if actor_role=="provider" and action in {"start","complete"} and incident.assigned_organization_id != actor_org:
    raise AppError(403, "not_assigned", ...)             # only the assigned provider may progress
```

> **Footnotes**
>
> - **[1]** Order matters: role first (don't leak state info to someone who can't act), then the *single-claim* race guard, then legality, then domain policy (critical-approval), then ownership. Each raises a precise `code` a client can branch on. ***Single-claim*** — the first provider to accept wins; a second gets `409 already_accepted` — is how two responders don't both think they own the same emergency.

---

## Creating a request — including as a guest

Creation is where the **guest path** (Ch 6) pays off: an unauthenticated person can raise
an emergency and receive a **tracking token**; a *provider* may not raise requests.[1]

```python
# app/modules/incidents/router.py (trimmed)
async def create_incident(data: IncidentCreate, db, claims = Depends(get_optional_claims)):
    if claims is not None and claims.get("role") == "provider":
        raise AppError(403, "forbidden", "Providers cannot raise help requests.")
    requester_id = uuid.UUID(claims["sub"]) if claims else None      # None = guest
    incident = await _service(db).create(data, requester_id)
    return to_response(incident)
```

The service issues a `tracking_token` only for guests, so they can follow the request
without an account.[2]

> **Footnotes**
>
> - **[1]** Why block providers from creating? Roles model real responsibilities: providers *respond*, they don't *raise*. Encoding that in one check keeps the domain honest. Guests get a stricter rate limit (5/min) than signed-in citizens (20/min) — Ch 6.
> - **[2]** A ***tracking token*** is a random, unguessable string standing in for an account, so a guest can check status later. Real accounts get richer history; the token is the minimal viable "follow my request."

---

## Each transition is its own endpoint

Rather than one "change status" endpoint, each move is a **dedicated URL** with its own
body and side-effects — which is also where audit + notifications compose (Ch 9). `accept`
resolves the provider's own verified org **server-side**:

```python
# app/modules/incidents/router.py (trimmed)
@router.post("/{incident_id}/accept", response_model=IncidentResponse)
async def accept(incident_id, data: AcceptRequest, db, claims: Claims):
    org = await _org_service(db).resolve_active_for_owner(uuid.UUID(claims["sub"]))  # must be verified
    return await _transition(db, incident_id, claims, "accept", organization_id=org.id, note=data.eta)
```

⚠️ **Pitfall:** the client does **not** send which org is accepting — the server derives
it from the authenticated provider. Trusting a client-supplied org id would let anyone
claim on another org's behalf.[1]

> **Footnotes**
>
> - **[1]** Deriving authority from the *token*, never the *body*, is a core security habit (Ch 6). `resolve_active_for_owner` also enforces that the provider's organization is **verified** before it may claim — a coordinator gate covered in Chapter 9's cross-cutting view and the resources module.

---

## Recap & what's next

- An incident moves through **8 states**; legal moves live in **pure data tables**
  (`TRANSITIONS`, `ACTION_ROLES`) that are unit-testable without a database.
- `perform_transition` enforces, in order: **role → single-claim → legality →
  critical-approval → ownership → org-membership**, each with a precise error `code`.
- Creation supports the **guest path** (tracking token); each transition is its own
  endpoint, with the accepting org resolved **server-side**.

🛠️ **Try it:** trace `start` in `perform_transition`. Which checks fire if a provider
tries to `start` an incident assigned to a *different* org? (Answer: role ✓, legality ✓,
then `not_assigned` 403.)

**Next:** [Chapter 8 — Geospatial with PostGIS](08-geospatial-with-postgis.md), where
"near me" becomes a real query.
