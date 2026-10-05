# IDRM MVP — Security & IAM Design

> *Type: Document (specification) · Audience: security reviewers, developers · Status: MVP — current*
> *Who can do what, and how the system is protected. Consolidated from the authoritative [`../../docs/05-security.md`](../../docs/05-security.md), the v3 functional spec's security requirements, and the locked API/data model. Every API operation maps to a permission here. Advanced controls (OIDC/SSO, MFA, ABAC, per-request privacy, biometric, gateway/WAF) are **→ FFP**.*

> **Principle:** security is **built in, not bolted on** — *Zero Trust* (never trust, always verify),
> *Least Privilege* (minimum access), *Secure by Default*, *Defense in Depth*, *Accountability* (everything
> significant is audited). It sits **before** serious implementation so access rules exist from day one.

---

## 1. How to read this document

- **§2 Authentication** — proving *who you are* (accounts, tokens, passwords, lockout, guest access).
- **§3 Authorization (RBAC)** — *what you may do*: the **role → permission → API operation** map (the heart
  of this doc; every locked endpoint appears here).
- **§4 Data protection** · **§5 Audit** · **§6 Rate limiting** · **§7 Threat model** · **§8 Compliance**.
- **§9 Deferred → FFP** · **§10 Traceability**.

The four MVP roles (from the PRD/scope, locked): **`citizen` · `provider` · `coordinator` · `admin`**
(`admin` = platform administrator, a superset of `coordinator`). Plus **`guest`** — an unauthenticated
person allowed a narrow life-safety path (§2.5).

> **Acronym key (expanded once, for this doc):** **IAM** = Identity & Access Management (the whole "who are you /
> what may you do" system) · **JWT** = JSON Web Token (a signed, self-contained login token) · **RS256** = RSA
> signature with SHA-256 (asymmetric: private key signs, public key verifies) · **RBAC** = Role-Based Access
> Control · **ABAC** = Attribute-Based Access Control · **PII** = Personally Identifiable Information · **TLS** =
> Transport Layer Security (the encryption behind HTTPS) · **OWASP** = Open Worldwide Application Security Project
> (a web-security authority; its "Top 10" is the standard risk list) · **STRIDE** = a method for classifying
> threats · **DPDP** = India's Digital Personal Data Protection Act, 2023 · **MFA / OTP** = Multi-Factor Auth /
> One-Time Password · **OIDC / SSO** = OpenID Connect / Single Sign-On · **WAF** = Web Application Firewall ·
> **KMS** = Key Management Service · **CORS** = Cross-Origin Resource Sharing.

---

## 2. Authentication — who you are

### 2.1 Account lifecycle
Register → **verify email** (account `pending` → `active`) → sign in. A user cannot act until verified,
except the guest emergency path (§2.5). Backed by `users`, `email_verification_tokens`,
`password_reset_tokens`, `user_sessions` (see [`50-data-model.md`](50-data-model.md)).

### 2.2 Token model
| Token | Form | Lifetime | Purpose / rules |
|---|---|---|---|
| **Access token** | JWT, **RS256** (asymmetric) | **~60 min** | Sent as `Authorization: Bearer <jwt>` on every authenticated call; carries `sub` (user id) + `role`; verified on each request. |
| **Refresh token** | opaque, stored in `user_sessions` | **~7 days** | Exchanged at `POST /auth/refresh` for a new access token; **rotated on use**; **revocable** (logout deletes the session row). |
| **Email-verification token** | random, single-use | 24 h | Activates the account. |
| **Password-reset token** | random, single-use | 1 h | Authorizes one password reset; invalidates existing sessions. |
| **Guest tracking token** | random, scoped | life of the request | Read-only access to **one** guest-created incident (§2.5). |

> **Why RS256 (not HS256):** the app signs access tokens with a **private key**; anything can verify with
> the **public key** *without* holding a secret. That means when FFP splits modules into services behind
> APISIX, they verify the *same* tokens with no shared secret and no code change — consistent with the
> "evolve without rewrite" rule.

### 2.3 Password policy (NIST SP 800-63B-4–aligned)
- **Minimum length ≥ 8** (10+ encouraged); **allow all characters** (spaces, Unicode) — length beats forced
  composition.
- **Block known-breached / common passwords** (dictionary check) instead of rigid "1 upper + 1 symbol" rules.
- **No forced periodic rotation**; reset only on suspicion/compromise.
- Stored **only** as a **bcrypt** hash (cost 12) — never plaintext, never reversible.

> *Why gentler than the archived v3 rule:* IDRM's users are often stressed, on phones, with low digital
> literacy. NIST-style "long but simple" passwords are **more** secure in practice **and** less likely to
> lock out someone who needs help. (Stronger 2FA is available later via MFA → FFP.)

### 2.4 Brute-force protection
After **5 failed logins**, the account is locked for **15 minutes** (`failed_login_attempts`,
`locked_until`). Login and other sensitive endpoints are also rate-limited (§6). *(15 min, not 30 —
deliberately short so a fumbling user in an emergency isn't shut out for long.)*

### 2.5 Guest (emergency) access — life-safety
An unauthenticated person may `POST /incidents` (stricter rate limit) for life-safety. The response returns
a **guest tracking token** granting **read-only** access to **that one incident** and the ability to upload
its photos — nothing else. No browsing, no other data. `incidents.requester_id` is `NULL` for guests.

---

## 3. Authorization — the RBAC map (role → API operation)

**Model:** RBAC — a user's **role** grants a set of **permissions**; each API operation requires a
permission. Where a resource is *owned* (a citizen's own incident, a provider's own org), an **ownership
check** is applied on top of the role. ABAC (area/jurisdiction rules) is **→ FFP**.

**Legend:** ✓ = allowed · **own** = only their own records · **assigned** = only the incident they claimed ·
— = denied · *(guest)* = the narrow guest path.

### 3.1 Auth & users
| Operation | citizen | provider | coordinator | admin |
|---|:--:|:--:|:--:|:--:|
| `POST /auth/*` (register, login, refresh, forgot/reset) | public | public | public | public |
| `POST /auth/logout`, `/change-password` | ✓ | ✓ | ✓ | ✓ |
| `GET/PATCH /users/me` | own | own | own | own |
| `GET /users`, `GET /users/{id}` | — | — | ✓ | ✓ |
| `PATCH /users/{id}` (role/status) | — | — | — | ✓ |

### 3.2 Incidents (core) — including lifecycle transitions
| Operation | citizen | provider | coordinator | admin |
|---|:--:|:--:|:--:|:--:|
| `POST /incidents` (create) | ✓ | — *(conflict of interest)* | ✓ | ✓ + *(guest)* |
| `GET /incidents` (list, role-scoped) | own | claimable/nearby | ✓ all | ✓ all |
| `GET /incidents/{id}` | own | assigned | ✓ | ✓ |
| `PATCH /incidents/{id}` (edit pre-accept) | own | — | ✓ | ✓ |
| `GET /incidents/mine` | ✓ | — | — | — |
| `GET /incidents/assigned` | — | ✓ | — | — |
| `GET /incidents/nearby` | — | ✓ | ✓ | ✓ |
| `POST …/approve`, `…/reject`, `…/assign` | — | — | ✓ | ✓ |
| `POST …/accept` | — | ✓ | — | — |
| `POST …/start`, `…/complete` | — | assigned | — | — |
| `POST …/verify` | own | — | — | — |
| `POST …/cancel` | own | — | ✓ | ✓ |

### 3.3 Organizations, resources, geo
| Operation | citizen | provider | coordinator | admin |
|---|:--:|:--:|:--:|:--:|
| `POST /organizations` | — | ✓ | — | ✓ |
| `GET /organizations`, `GET /{id}` | ✓ (public fields) | ✓ | ✓ | ✓ |
| `GET /organizations/mine` | — | ✓ | — | — |
| `PATCH /organizations/{id}` | — | own | ✓ | ✓ |
| `POST /organizations/{id}/verify` | — | — | ✓ | ✓ |
| `PATCH …/capacity`, `…/availability` | — | own | — | ✓ |
| `GET /resources`; `POST/PATCH /resources` | ✓ (view) | own (write) | ✓ | ✓ |
| `GET /locations/*` (nearby, distance, geocode, map) | ✓ (role-scoped) | ✓ | ✓ | ✓ |

### 3.4 Alerts, notifications, reports, audit, files
| Operation | citizen | provider | coordinator | admin |
|---|:--:|:--:|:--:|:--:|
| `POST /alerts` (broadcast) | — | — | ✓ | ✓ |
| `GET /alerts` | ✓ | ✓ | ✓ | ✓ |
| `GET/POST/DELETE /notifications/*` | own | own | own | own |
| `GET /reports/*` (dashboard, metrics, export) | — | — | ✓ | ✓ |
| `GET /audit-logs` | — | — | ✓ | ✓ |
| `POST /files` (upload) | ✓ + *(guest, incident photos)* | ✓ | ✓ | ✓ |
| `GET /files/{id}` | own/linked | linked | ✓ | ✓ |
| `GET /health` | public | public | public | public |

> **Enforcement:** the role check runs at the API layer (a dependency on every protected route); the
> ownership/assignment check runs in the module's service layer against the DB. A failed role check →
> **`403 forbidden`**; an unauthenticated call to a protected route → **`401`**. *(The `Auditor` role and
> area/jurisdiction scoping from the archived 10-role model are **→ FFP**.)*

---

## 4. Data protection

| Control | MVP application |
|---|---|
| **In transit** | All traffic over **HTTPS / TLS 1.2+** (1.3 preferred). No plaintext HTTP in any environment beyond local dev. |
| **Passwords** | **bcrypt** (cost 12) hashes only. |
| **Input validation** | Every request body/param validated with **Pydantic** at the edge, before business logic — blocks malformed/injection input; SQLAlchemy uses **parameterised queries** (no string-built SQL). |
| **PII minimisation** | Collect only what's needed (name, phone, location). Citizen contact is **not** exposed publicly; it's shared with an assigned provider only as needed. |
| **File / object security** | The **MinIO** bucket is **private**; files are served via the backend as **time-limited pre-signed URLs**, never public links. Uploads are type/size/blur-validated and **EXIF/GPS-stripped** (media rules, [`40-api-specification.md`](40-api-specification.md) §5.7). |
| **Secrets** | DB, MinIO, and the **JWT signing keys** are read from **environment variables** (`pydantic-settings` / a git-ignored `.env`) — **never** committed to code. The setup script's placeholder credentials **must be changed** before any non-local use. |
| **Secure defaults** | Security headers (CSP, HSTS, X-Content-Type-Options), safe/HttpOnly cookies where used, CORS locked to known origins. |

*(Field-level PII encryption at rest / **AES-256** and a dedicated **secrets vault (Vault/KMS)** are
**→ FFP** — the MVP relies on transport encryption, hashing, disk/db-level protection, and env-var secrets.)*

---

## 5. Audit & accountability

- **Append-only** `audit_logs` (no update/delete endpoint by design — §3 shows only `GET`). Written by the
  system as a side-effect of sensitive operations.
- **Logged:** login/logout & auth failures, account lock, incident create/claim/every lifecycle transition,
  critical approve/reject, org verify/suspend, role/status changes, file uploads.
- **Each entry:** `actor_id`, `action` (e.g. `incident.accepted`), `resource_type`+`resource_id`,
  `ip_address`, `old_values`/`new_values` (JSONB), `created_at` (UTC).
- **Retention:** target **≥ 1 year** for the MVP; **7 years** is the compliance target (→ tune with policy).
- Feeds monitoring/alerting (see [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md)).

---

## 6. Rate limiting & abuse protection

- **Per-endpoint budgets** carried from the API contract (e.g. login 5/min, register 10/min, create
  incident 20/min, guest create 5/min); exceeding returns **`429`** + `Retry-After`.
- **Account lockout** (§2.4) on repeated auth failures.
- **Guest path** is the most tightly limited (life-safety, but abuse-resistant).
- *(Centralised, distributed rate limiting and a WAF arrive with the **APISIX** gateway → FFP; the MVP
  enforces limits in the app.)*

---

## 7. Threat model (MVP-scoped)

IDRM follows the authoritative model in [`../../docs/05-security.md`](../../docs/05-security.md) §6
(STRIDE + OWASP, trust boundaries). MVP-relevant highlights:

| OWASP (2021) | MVP mitigation |
|---|---|
| A01 Broken Access Control | The RBAC map (§3) + ownership checks; deny-by-default; tested per operation. |
| A02 Cryptographic Failures | TLS 1.2+, bcrypt, RS256 JWT, secrets in env (not code). |
| A03 Injection | Pydantic validation + SQLAlchemy parameterised queries. |
| A05 Misconfiguration | Change default creds; security headers; least-privilege DB/MinIO accounts. |
| A07 Auth Failures | Email verification, lockout, rate limiting, single-use tokens, refresh rotation. |
| A09 Logging Failures | Append-only audit of all sensitive actions. |

**Trust boundary:** untrusted internet/public → the FastAPI app (authN, validation, rate-limit) → trusted
PostgreSQL/MinIO. External SMS/email gateways sit outside and are called server-side only.

---

## 8. Compliance

- **DPDP Act, 2023 (India)** — data minimisation, purpose limitation, access control, and consent posture
  for personal/location data. (Biometric processing — FaceNet — is **explicitly deferred → FFP** precisely
  because of this.)
- **OWASP Top 10 / ASVS** — web-risk baseline (§7).
- **WCAG 2.2 AA** — security must never lock people out unfairly (accessible auth — a 2.2 criterion — clear errors).
- **NIST CSF 2.0** — the cybersecurity framework (Govern·Identify·Protect·Detect·Respond·Recover) IDRM organises
  its security posture around; identity follows **NIST SP 800-63-4 / 63B-4**.
- Aligns toward **ISO/IEC 27001** as the platform matures.
- Full standards map + owners: [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) §4.

---

## 9. Deferred to the FFP (recorded, not dropped)

| Deferred control | Why it waits |
|---|---|
| **OIDC / SSO**, **MFA / OTP** | The MVP uses email+password + JWT; stronger/second-factor auth arrives with organisational rollout. |
| **ABAC** (area/jurisdiction/ownership-as-policy) | MVP uses RBAC + simple ownership checks; policy-based context rules are FFP. |
| **Full 10-role hierarchy + `Auditor` role** | MVP has 4 roles; the richer hierarchy is FFP IAM. |
| **Per-request privacy levels** (Public/Protected/Private) | Deferred with the scope decision (doc 11 §3). |
| **Biometric face recognition (FaceNet)** | Biometric data of vulnerable people → consent + DPDP safeguards; FFP. |
| **APISIX gateway** (TLS termination, WAF, centralised rate-limit, zero-trust edge) | MVP's FastAPI app enforces auth/limits directly. |
| **Secrets vault / KMS**, field-level **AES-256** at rest | MVP uses env-var secrets + transport/hashing; a vault + at-rest field encryption are FFP. |

All recorded in the [FFP charter](../ffp/prompts/instructions_idrm_ffp_docs.md).

---

## 10. Traceability

- Every row of the §3 matrix corresponds to an operation in [`40-api-specification.md`](40-api-specification.md) /
  [`40-api-openapi.yaml`](40-api-openapi.yaml); auth/roles listed there match here.
- Backed by the `users`/`user_sessions`/`*_tokens`/`audit_logs` tables in [`50-data-model.md`](50-data-model.md).
- Access-control and audit behaviours are asserted by tests in [`70-quality-test-strategy.md`](70-quality-test-strategy.md)
  and are part of the Definition of Done ([`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) §7).

*Related:* [`10-requirements-prd.md`](10-requirements-prd.md) · [`20-architecture-system.md`](20-architecture-system.md) ·
[`21-architecture-decisions.md`](21-architecture-decisions.md) · [`25-module-elucidation.md`](25-module-elucidation.md) (USR/AUD modules) ·
[`26-conformance-pics.md`](26-conformance-pics.md) (USR/AUD conformance rows) · [`../../docs/05-security.md`](../../docs/05-security.md).
Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
