"""Application settings, read from the environment (never hard-coded).

All configuration and secrets come from environment variables (a git-ignored ``.env`` in
development), loaded once into a cached ``Settings`` object. See roadmap §11 and doc 80.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings sourced from the environment / ``.env``."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str = "postgresql+asyncpg://idrm_user:CHANGE_ME@127.0.0.1:5432/idrm_db"

    # Object storage (MinIO / S3)
    s3_endpoint: str = "http://127.0.0.1:9000"
    s3_bucket: str = "idrm-uploads"
    s3_access_key: str = "CHANGE_ME"
    s3_secret_key: str = "CHANGE_ME"

    # Media / upload rules (server re-checks; never trust the client — doc 22, PICS-FIL-002/003)
    file_max_bytes: int = 10 * 1024 * 1024  # 10 MB hard limit (413 file_too_large)
    lite_photo_max_bytes: int = 512 * 1024  # emergency "lite" path (~500 KB, PICS-FIL-004)
    image_max_dimension: int = 1920  # longest edge; larger images are downscaled
    image_min_width: int = 640
    image_min_height: int = 480
    image_blur_min_variance: float = 5.0  # edge-variance floor; below = rejected as too blurry

    # Auth (RS256 keypair)
    jwt_private_key_path: str = "/etc/idrm/jwt_private.pem"
    jwt_public_key_path: str = "/etc/idrm/jwt_public.pem"
    access_token_ttl_min: int = 60
    refresh_token_ttl_days: int = 7

    # App
    app_env: str = "development"
    allowed_origins: str = "http://127.0.0.1:8000"
    default_language: str = "en"
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> list[str]:
        """The allow-list of front-end origins (comma-separated in the env var)."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide cached settings instance."""
    return Settings()
