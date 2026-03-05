from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Invoice Generator API"
    environment: str = "development"
    debug: bool = True

    database_url: str = "postgresql+psycopg2://invoice:invoice@postgres:5432/invoice_db"
    backend_base_url: str = "http://localhost:8000"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    media_root: str = "media"
    logos_dir: str = "media/logos"
    exports_dir: str = "media/exports"

    telegram_bot_token: str | None = None
    telegram_allowed_user_ids: list[int] = Field(default_factory=list)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
