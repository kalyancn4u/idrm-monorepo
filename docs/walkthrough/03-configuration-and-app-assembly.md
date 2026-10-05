# Chapter 3 — Configuration & App Assembly

*Where every setting lives, and how the application is wired together at startup.*

**By the end of this chapter you will be able to:** explain why all settings live in one
typed object, override any of them from the environment, and trace how `main.py` assembles
the app and stamps every request with a correlation id.

Files: [`app/core/config.py`](../../services/monolith/app/core/config.py),
[`app/main.py`](../../services/monolith/app/main.py).

---

## One place for every setting

Configuration is **centralized** in a single typed `Settings` object, read from the
**environment** (a git-ignored `.env` in development).[1] Nothing is hard-coded and no
secret is committed.

```python
# app/core/config.py (trimmed)
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = "postgresql+asyncpg://idrm_user:CHANGE_ME@127.0.0.1:5432/idrm_db"
    s3_endpoint: str = "http://127.0.0.1:9000"
    access_token_ttl_min: int = 60
    log_level: str = "INFO"
```

Each field has a **type** and a safe default; the type is enforced at load time.[2]

> **Footnotes**
>
> - **[1]** This is the ***12-factor*** "config in the environment" principle: the same built artifact runs in dev, staging, and prod, differing only by environment variables. It also keeps secrets out of the code and out of git.
> - **[2]** ***Pydantic Settings*** coerces and validates: `access_token_ttl_min` will only ever be an `int`. A malformed value fails loudly at startup, not mysteriously at runtime. `extra="ignore"` means unknown env vars are harmless.

---

## Overriding settings, and one derived value

Any field is overridden by an environment variable of the same name (upper-cased). A
small `@property` turns the comma-separated `ALLOWED_ORIGINS` string into a list:

```python
# app/core/config.py (trimmed)
@property
def cors_origins(self) -> list[str]:
    return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]
```

```bash
# any shell — override without touching code
export DATABASE_URL="postgresql+asyncpg://idrm_user:realpass@db:5432/idrm_db"
export LOG_LEVEL=DEBUG
```

🧠 **Nuance:** the template file [`services/monolith/.env.example`](../../services/monolith/.env.example) documents
every variable; you copy it to `.env` and fill in real values. The `CHANGE_ME`
placeholders are intentional trip-wires.[1]

> **Footnotes**
>
> - **[1]** Committing `.env.example` (safe) but never `.env` (real) is the standard pattern: it documents the contract without leaking secrets. IDRM's `.gitignore` enforces that real `.env` variants stay untracked.

---

## Loaded once, cached forever

`get_settings()` is wrapped in `@lru_cache`, so the environment is read **once** and the
same object is reused everywhere.[1]

```python
# app/core/config.py
@lru_cache
def get_settings() -> Settings:
    return Settings()
```

⚠️ **Pitfall:** because settings are cached at first import, **tests must set env vars
*before* importing the app** — which is exactly what `tests/conftest.py` does (Ch 11).[2]

> **Footnotes**
>
> - **[1]** ***`lru_cache`*** memoizes a function's result. With no arguments, the first call builds `Settings`; every later call returns the cached instance — cheap and consistent. This is a lightweight ***singleton***.
> - **[2]** This is a real gotcha of cached config: set-then-import, not import-then-set. `conftest.py` writes a test `DATABASE_URL` and generates an ephemeral keypair *above* its `from app.main import app` line.

---

## Assembling the app

`main.py` is the composition root: it configures logging, creates the FastAPI app, adds
CORS, registers the error handlers, and mounts every module's router.

```python
# app/main.py (trimmed)
settings = get_settings()
configure_logging(settings.log_level)                 # JSON logs (Ch 4)
app = FastAPI(title="IDRM MVP API", version="0.1.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, ...)
register_exception_handlers(app)                      # the one error envelope (Ch 4)
```

This file *wires*; it contains no business logic.[1]

> **Footnotes**
>
> - **[1]** A ***composition root*** is the single place where the pieces are assembled. Keeping assembly in one file (and logic out of it) means you can read the app's whole shape — middleware, error handling, routes — in one screen.

---

## The request-context middleware — one id ties a request together

Every request passes through one middleware that assigns an **`X-Request-Id`**, records
the client IP, logs start and end with the latency, and echoes the id back in the
response header.[1]

```python
# app/main.py (trimmed)
@app.middleware("http")
async def request_context(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or f"req_{uuid.uuid4().hex[:12]}"
    request_id_ctx.set(rid)                           # a contextvar (Ch 4)
    client_ip_ctx.set(request.client.host if request.client else None)
    logger.info("request.start", extra={"extra_fields": {"method": request.method, "path": request.url.path}})
    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    return response
```

🧠 **Nuance:** the id is stored in a **contextvar**, so *every* log line emitted while
handling that request carries it automatically — no need to thread it through calls.[2]

> **Footnotes**
>
> - **[1]** ***Correlation id*** = one identifier shared by every log line of a single request. When something goes wrong, you filter logs by `request_id` and see the whole story. Echoing it back lets a client (or a proxy) report the exact id to support.
> - **[2]** A ***contextvar*** (`contextvars.ContextVar`) is per-task, async-safe storage — the async equivalent of thread-local. Set once in middleware, read anywhere downstream, isolated between concurrent requests. Chapter 4 shows the logging side.

---

## Health and the ten routers

Finally, `main.py` exposes a health probe and mounts all ten module routers under
`/api/v1`:

```python
# app/main.py (trimmed)
@app.get("/api/v1/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok"}

app.include_router(users_router,     prefix="/api/v1",           tags=["users"])
app.include_router(incidents_router, prefix="/api/v1/incidents", tags=["incidents"])
# … organizations, resources, locations, alerts, notifications, reports, files, audit, administration
```

That list of `include_router(...)` lines **is** the ten modules — the map from Chapter 1
made concrete.[1]

> **Footnotes**
>
> - **[1]** A ***health endpoint*** is a tiny, dependency-free URL that a load balancer or `systemd` pings to ask "are you alive?". Keeping it trivial (no DB call) means it answers even when downstream systems are degraded — the right behaviour for a *liveness* check.

---

## Recap & what's next

- All settings live in one **typed, env-driven, cached** `Settings` object; override via
  environment variables; never commit real secrets.
- `main.py` is the **composition root**: logging, CORS, error handlers, the request-id
  middleware, health, and the ten routers.
- A **contextvar** carries the request id (and client IP) to everything downstream.

🛠️ **Try it:** run the app (Ch 1's "before you start") and `curl -i` any endpoint — look
for the `X-Request-Id` header in the response. That id will also appear on every log line
for that call.

**Next:** [Chapter 4 — Observability & Errors](04-observability-and-errors.md), where those
log lines become structured JSON and every failure becomes one predictable shape.
