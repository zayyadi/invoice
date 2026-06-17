from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Invoice Generator API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg2://invoice:invoice@postgres:5432/invoice_db"
    backend_base_url: str = "http://localhost:8000"
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )
    cors_origin_regex: str | None = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

    media_root: str = "media"
    logos_dir: str = "media/logos"
    exports_dir: str = "media/exports"

    telegram_bot_token: str | None = None
    telegram_allowed_user_ids: list[int] = Field(default_factory=list)

    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from_email: str | None = None

    # JWT Settings
    secret_key: str = Field(default="your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug_flag(cls, value):
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "prod", "production", "false", "0", "off", "no"}:
                return False
            if normalized in {"debug", "dev", "development", "true", "1", "on", "yes"}:
                return True
        return value


settings = Settings()
