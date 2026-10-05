"""
core/config.py — Application settings (the single place we read configuration).

We use **pydantic-settings**: it loads values from environment variables and the
project's root `.env` file, validates their types, and exposes them as a typed
object. The rest of the code imports the ready-made singleton:

    from core.config import settings
    settings.DATABASE_URL   # -> str

Why this matters (rookie note): nothing else in the codebase should touch
`os.environ` directly. One typed `settings` object = no scattered config, no
guessing whether a value is a string or an int.
"""
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# The .env file lives at the REPO ROOT, but we run uvicorn from this backend
# folder. Resolve the root path from THIS file's location so it works no matter
# which directory you launch from:
#   config.py -> core -> app-python -> backend -> src -> <repo root>
_ENV_FILE = Path(__file__).resolve().parents[4] / ".env"


class Settings(BaseSettings):
    # env_file = where to read; extra="ignore" = don't crash on unknown keys.
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "IDRM API"
    API_V1_PREFIX: str = "/api/v1"

    # --- Database (async SQLAlchemy URL — note the +asyncpg driver) ---
    DATABASE_URL: str = (
        "postgresql+asyncpg://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db"
    )

    # --- Redis (cache, sessions, rate limiting, pub/sub) ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- JWT auth (canonical: 15-min access + 7-day refresh) ---
    JWT_SECRET_KEY: str = "dev-only-secret-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    # Stored as a comma-separated string in .env; use `cors_origins_list` to get
    # a real list. (We avoid a list-typed field here because pydantic-settings
    # would try to JSON-parse it from the env value and choke on a plain string.)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:5174,exp://127.0.0.1:19000"

    @property
    def cors_origins_list(self) -> list[str]:
        """The CORS origins as a clean list (splits the comma-separated string)."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache  # build the Settings object once and reuse it (fast + consistent)
def get_settings() -> Settings:
    return Settings()


# Import this anywhere: `from core.config import settings`
settings = get_settings()
