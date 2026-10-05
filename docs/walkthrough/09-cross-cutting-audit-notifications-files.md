# Chapter 9 — Cross-Cutting: Audit · Notifications · Files

*How a feature gains side-effects — a log entry, a notification, a stored file — without
losing its purity.*

**By the end of this chapter you will be able to:** explain router-edge composition, read
the append-only audit trail, follow a notification, and understand the storage abstraction
and the server-side image pipeline.

Files: [`audit/`](../../services/monolith/app/modules/audit/),
[`notifications/`](../../services/monolith/app/modules/notifications/),
[`files/service.py`](../../services/monolith/app/modules/files/service.py),
[`files/storage.py`](../../services/monolith/app/modules/files/storage.py),
[`files/imaging.py`](../../services/monolith/app/modules/files/imaging.py).

---

## Effects belong at the router edge

Recall Design Law #3 (Ch 1): a service does its **one** job; cross-cutting effects are
composed by the **router**, after the service returns.[1]

```python
# app/modules/incidents/router.py — _transition (trimmed)
updated = await svc.perform_transition(incident, action, actor_id, role, **kwargs)  # pure rule
await _notify_requester(db, updated, actor_id)                                       # + notification
await AuditService(AuditRepository(db)).record(f"incident.{action}", ...)            # + audit
```

The incident service does **not** import audit or notifications — it doesn't know they
exist. Coupling stays **one-directional** (feature → audit/notifications).[2]

> **Footnotes**
>
> - **[1]** ***Cross-cutting concern*** = something many features need (logging, audit, notifications) that isn't the feature itself. Bury it inside each service and you get tangled dependencies and untestable rules; compose it at the thin edge and the core stays clean.
> - **[2]** ***One-directional coupling*** means audit/notifications never call back into incidents. That acyclic shape is exactly what lets a module later become its own service — the Strangler Fig path (Ch 1).

---

## Audit: an append-only trail you cannot rewrite

The audit module records *who did what, when, from where*. Its defining property:
**append-only** — there is a `record` write and a read endpoint, but **no update or delete
path anywhere**.[1]

```python
# app/modules/audit/service.py (trimmed)
async def record(self, action, *, actor_id=None, resource_type=None, resource_id=None,
                 ip_address=None, old_values=None, new_values=None) -> AuditLog:
    entry = AuditLog(action=action, actor_id=actor_id, resource_type=resource_type,
                     resource_id=resource_id, ip_address=ip_address,
                     old_values=old_values, new_values=new_values)
    await self.repo.add(entry);  return entry
```

The router exposes only `GET /audit-logs` (coordinator/admin, filterable). You literally
cannot mutate the trail over the API.[2]

> **Footnotes**
>
> - **[1]** ***Append-only*** = writes add rows; nothing edits or removes them. For a disaster-response system, an unforgeable record of decisions is a governance requirement, not a nicety. The `ip_address` comes from the `client_ip_ctx` contextvar (Ch 3) — captured without threading `Request` through every call.
> - **[2]** Absence of a write endpoint is a *design guarantee*, not an oversight: the only way in is `AuditService.record`, invoked by trusted server code at the router edge (incident transitions, org verification, alert broadcast, admin user changes).

---

## Notifications: tell the requester, never yourself

When an incident changes, the requester is told — unless they *are* the actor, or the
requester is a guest:[1]

```python
# app/modules/incidents/router.py (trimmed)
async def _notify_requester(db, incident, actor_id):
    if incident.requester_id is None or incident.requester_id == actor_id:
        return                                   # skip guests + self-actions
    await NotificationService(NotificationRepository(db)).notify(
        user_id=incident.requester_id, ntype=NotificationType.incident_update,
        title="Update on your request", message=f"Your help request is now '{incident.status.value}'.",
        link=f"/incidents/{incident.id}")
```

Delivery is **pull-model** (the user lists their notifications) — no broker in the MVP.[2]

> **Footnotes**
>
> - **[1]** Skipping self-actions avoids the silly "you notified yourself" case; skipping guests is necessary because a guest has no account to notify (they use the tracking token instead, Ch 7). Every notification is strictly scoped to its owning user in the repository.
> - **[2]** **Honest scope note:** ***pull-model*** = the client fetches unread notifications; there's no server push. Real-time push (WebSockets) and channel fan-out (SMS/email brokers) are FFP. What would change it: needing instant delivery to an offline app — then a broker + push service is added behind the same `notify` seam. Preferences (email/sms/in_app) are already recorded for that day.

---

## Files: depend on a protocol, not on boto3

The files service must store bytes in **MinIO**, but it depends on a small **protocol**,
not on the S3 client directly — so tests inject an in-memory fake and production uses
boto3.[1]

```python
# app/modules/files/storage.py (trimmed)
class ObjectStorage(Protocol):           # the contract the service needs
    bucket: str
    def put(self, key: str, data: bytes, content_type: str) -> str: ...

class S3Storage:                         # the real one (boto3, lazy import) — talks to MinIO/S3
    def put(self, key, data, content_type) -> str: ...
```

🧠 **Nuance:** this is **dependency inversion** — the service owns the interface; the
concrete backend is a detail passed in.[2]

> **Footnotes**
>
> - **[1]** A ***Protocol*** (structural typing) says "anything with a `bucket` and a `put(...)` counts." No inheritance required. Tests pass a `FakeStorage` that writes to a dict; the service can't tell the difference — so upload logic is tested with **no MinIO running**.
> - **[2]** ***Dependency inversion***: high-level code (the service) depends on an abstraction it defines, and low-level code (S3Storage) conforms to it. That's what makes the storage backend swappable and the service testable.

---

## Never trust the client: the image pipeline

The client is asked to compress, but the **server re-processes every image** —
`imaging.py`, using Pillow:[1]

```python
# app/modules/files/imaging.py (trimmed)
image = ImageOps.exif_transpose(image)           # apply orientation…
clean = Image.new(image.mode, image.size)        # …then rebuild from raw pixels →
clean.putdata(list(image.getdata()))             #    strips ALL metadata, incl. GPS
clean.thumbnail((max_dim, max_dim))              # downscale (never upscale)
if width < min_w or height < min_h:  raise AppError(422, "image_too_small", ...)
if _blur_variance(clean) < floor:    raise AppError(422, "image_too_blurry", ...)
```

⚠️ **Pitfall:** stripping EXIF is a **privacy** must — phone photos embed GPS coordinates;
uploading one raw would leak a person's exact location.[2]

> **Footnotes**
>
> - **[1]** ***EXIF*** = metadata cameras embed in photos (orientation, timestamp, often GPS). Rebuilding the image from raw pixels discards *all* of it. Re-checking size/dimensions/blur server-side means a malicious or broken client can't bypass the rules — the server is the authority (doc 22 §7).
> - **[2]** The ***face-detection quality gate*** is a documented seam: per ADR-011 it's **client-side and advisory** (`frontend/static/js/face-quality.js`), and the server computes **nothing biometric** — `passes_face_quality_gate` is an intentional no-op. Detection-only, nothing stored; FaceNet *recognition* is FFP (DPDP consent).

---

## The database stores keys, never blobs

Design Law #1 in action: the `files` table holds **metadata + the object key/URL**; the
bytes live in MinIO. Uploads are type- and size-gated before they're ever stored:[1]

```python
# app/modules/files/service.py (trimmed)
if content_type not in _EXTENSIONS:  raise AppError(400, "invalid_file_type", ...)
if len(raw) > max_bytes:             raise AppError(413, "file_too_large", ...)   # 10MB (lite ~500KB)
data = await run_in_threadpool(process_image, raw, content_type, self.settings) if is_image else raw
url  = await run_in_threadpool(self.storage.put, key, data, content_type)         # → MinIO
```

Note `run_in_threadpool`: Pillow and boto3 are **synchronous**, so they run off the async
event loop to avoid blocking it.[2]

> **Footnotes**
>
> - **[1]** Storing keys not blobs keeps the database small and fast, lets the object store scale independently, and means a backup of PostgreSQL is metadata-light. `GET /files/{id}` returns metadata, role-scoped (uploader or staff).
> - **[2]** ***`run_in_threadpool`*** offloads blocking work to a thread so the single async worker isn't frozen while an image is processed or uploaded. Mixing sync libraries into async code without this is a classic way to tank throughput.

---

## Recap & what's next

- Cross-cutting effects compose at the **router edge**; services stay pure and coupling
  is **one-directional**.
- **Audit** is append-only (no write API); **notifications** are pull-model and skip
  guests/self; **files** depend on an `ObjectStorage` **protocol**.
- The server **re-processes every image** (EXIF/GPS stripped, downscaled, blur-checked)
  and stores **keys, not blobs**; sync libs run in a threadpool.

🛠️ **Try it:** search the incidents service for the word "audit" or "notify" — you won't
find them. The effects are added by the router, exactly as Design Law #3 promises.

**Next:** [Chapter 10 — The API Contract & Responses](10-the-api-contract-and-responses.md),
where all of this is presented under one frozen contract.
