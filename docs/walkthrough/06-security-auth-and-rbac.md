# Chapter 6 — Security, Auth & RBAC

*Who is the caller, and what are they allowed to do?*

**By the end of this chapter you will be able to:** explain how passwords are stored, how
RS256 tokens prove identity, how the dependency guards enforce roles (and allow guests),
and how the login lifecycle resists abuse.

Files: [`core/security.py`](../../code/app/core/security.py),
[`core/dependencies.py`](../../code/app/core/dependencies.py),
[`core/rate_limit.py`](../../code/app/core/rate_limit.py),
[`modules/users/deps.py`](../../code/app/modules/users/deps.py),
[`modules/users/service.py`](../../code/app/modules/users/service.py).

---

## Passwords are hashed, never stored

Passwords are stored only as **bcrypt** hashes (cost 12) — the plaintext is never kept.[1]

```python
# app/core/security.py
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)
def hash_password(plain: str) -> str:  return _pwd.hash(plain)
def verify_password(plain: str, hashed: str) -> bool:  return _pwd.verify(plain, hashed)
```

🧠 **Nuance:** bcrypt is a **deliberately slow**, salted hash. Slowness is a *feature* —
it makes mass password-guessing expensive. "cost 12" sets that work factor.[2]

> **Footnotes**
>
> - **[1]** A ***hash*** is a one-way fingerprint: you can check a guess against it, but you cannot reverse it to the password. If the database leaks, attackers get hashes, not passwords.
> - **[2]** ***Salt*** = random data mixed in so identical passwords produce different hashes (defeating precomputed "rainbow table" attacks); bcrypt salts automatically. The ***work factor*** (rounds) is tunable upward as hardware gets faster — NIST-aligned policy favours length + slow hashing over forced composition rules.

---

## Identity: RS256 JSON Web Tokens

After login, the client holds a signed **JWT access token**. IDRM uses **RS256** —
*asymmetric* signing: the private key signs, and anyone with the **public** key can
verify.[1]

```python
# app/core/security.py (trimmed)
def create_access_token(subject: str, role: str) -> str:
    payload = {"sub": subject, "role": role, "iat": now, "exp": now + timedelta(minutes=ttl)}
    return jwt.encode(payload, _read_key(private_key_path), algorithm="RS256")

def decode_token(token: str) -> dict:              # verifies signature + expiry
    return jwt.decode(token, _read_key(public_key_path), algorithms=["RS256"])
```

The token carries just `sub` (user id) and `role`, plus issue/expiry times.[2]

> **Footnotes**
>
> - **[1]** ***Asymmetric*** (public/private) signing means a future microservice can *verify* tokens with the public key without holding the secret that can *mint* them. A single shared secret (HS256) would have to be copied to every verifier — a bigger blast radius if leaked. This is why RS256 was chosen (ADR-008).
> - **[2]** A ***JWT*** is a signed, self-describing token: its ***claims*** (`sub`, `role`, `exp`) are readable and tamper-evident. The server trusts a valid signature, so it needn't look the session up on every call — access tokens are short-lived (~60 min) to bound the risk if one leaks.

---

## The guards: three dependencies every router reuses

`core/dependencies.py` turns a token into claims and enforces roles — as FastAPI
dependencies routers simply declare.

```python
# app/core/dependencies.py (trimmed)
async def get_current_claims(creds = Depends(_bearer)) -> dict:      # 401 if missing/invalid
    if creds is None: raise AppError(401, "unauthorized", "Authentication required.")
    return decode_token(creds.credentials)

async def get_optional_claims(creds = Depends(_bearer)) -> dict | None:  # guest-allowed
    if creds is None: return None                    # absence = guest…
    return decode_token(creds.credentials)           # …but a present-but-bad token still 401s

def require_role(*roles):                            # RBAC gate
    def _guard(claims = Depends(get_current_claims)):
        if roles and claims.get("role") not in roles:
            raise AppError(403, "forbidden", "You do not have permission to do this.")
        return claims
    return _guard
```

🧠 **Nuance:** the **guest path** is `get_optional_claims` — *no* token means guest (an
emergency can be raised without an account); an *invalid* token still fails.[1]

> **Footnotes**
>
> - **[1]** ***RBAC*** (Role-Based Access Control) grants by role — citizen, provider, coordinator, admin. `require_role("coordinator","admin")` is a one-line, declarative gate on an endpoint. Distinguishing "no token" (guest, allowed) from "bad token" (rejected) is a subtle but important correctness point — Chapter 7 uses it for guest incident creation.

---

## From claims to the full user (kept out of `core`)

Some endpoints need the whole `User` row, not just claims. That loader lives in the
**users** module, not in `core` — so `core` never imports a module (no circular
dependency).[1]

```python
# app/modules/users/deps.py (trimmed)
async def get_current_user(claims = Depends(get_current_claims), db = Depends(get_db)) -> User:
    user = await UserRepository(db).get_by_id(uuid.UUID(claims["sub"]))
    if user is None: raise AppError(401, "unauthorized", "Account not found.")
    return user
```

> **Footnotes**
>
> - **[1]** A deliberate layering choice: `core` holds primitives everything depends on, so it must depend on *nothing* module-specific. Putting `get_current_user` in `users/deps.py` keeps the dependency graph acyclic — the same discipline as Design Law #3.

---

## The login lifecycle — and the one deliberate `commit`

Login enforces a **5-failure / 15-minute lockout** and gives a **generic** error so it
never reveals whether an email exists.[1] Watch the explicit `commit` on the failure path:

```python
# app/modules/users/service.py (trimmed)
if not verify_password(password, user.password_hash):
    user.failed_login_attempts += 1
    if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
        user.locked_until = _now() + timedelta(minutes=LOCKOUT_MINUTES)
    await self.repo.commit()     # persist the attempt NOW…
    raise AppError(401, "invalid_credentials", "Incorrect email or password.")   # …the 401 must not roll it back
```

⚠️ **Pitfall:** without that `commit`, the `401`'s rollback (the Unit of Work, Ch 5)
would erase the counter and the lockout could never accumulate. This is the *one* place a
service commits mid-request — and the comment says exactly why.[2]

> **Footnotes**
>
> - **[1]** ***Account enumeration*** is leaking which emails are registered via different error messages/timings. Returning the same `invalid_credentials` for "no such user" and "wrong password" closes that leak. The rest of the flow — email verification, **rotating** refresh tokens, single-use password-reset tokens — lives in the same service.
> - **[2]** This is the documented exception to "repositories/services never commit." It's safe because it commits *only* the counter increment and then deliberately fails the request; nothing else is pending. Recognising when a rule needs a principled exception — and documenting it — is part of engineering maturity.

---

## Rate limiting: a per-endpoint abuse guard

Sensitive endpoints declare a budget; exceeding it returns **`429` with `Retry-After`**.
It's keyed by (endpoint, client IP), in-process.

```python
# app/core/rate_limit.py (trimmed)
def rate_limit(name, limit, window_seconds=60):
    def _dependency(request: Request) -> None:
        ... # count recent hits for (name, client_ip) in the window
        if len(recent) >= limit:
            raise AppError(429, "rate_limit_exceeded", "Too many requests…",
                           headers={"Retry-After": str(retry_after)})
    return _dependency
```

Login is 5/min, register 10/min, guest incident-create a stricter 5/min, and so on.[1]

> **Footnotes**
>
> - **[1]** **Honest scope note:** this limiter is deliberately **in-process and single-box** — perfect for the MVP's one server. Distributed rate limiting and a WAF arrive with the **APISIX** gateway in the FFP. What would change the decision: running more than one app instance (then the counters must move to a shared store). Note the `AppError` carries a `Retry-After` **header** — that's why the error envelope supports headers (Ch 4).

---

## Recap & what's next

- Passwords → **bcrypt (cost 12)**; identity → **RS256 JWTs** (`sub` + `role`), verifiable
  with the public key alone.
- Three guards — `get_current_claims`, `get_optional_claims` (**guest**), `require_role`
  (**RBAC**) — plus `get_current_user` in the users module.
- Login resists abuse (**lockout**, generic errors) with one carefully-justified `commit`;
  per-endpoint **rate limiting** returns `429 + Retry-After`.

🛠️ **Try it:** call `GET /api/v1/users` (staff-only) with a citizen's token → `403`
`forbidden`. Now call it with no token → `401` `unauthorized`. Two different guards, two
different codes.

**Next:** [Chapter 7 — The Incident Lifecycle](07-the-incident-lifecycle.md), the domain's
beating heart.
