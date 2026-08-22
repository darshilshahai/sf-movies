from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SF Movies API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"
    frontend_url: str = "http://localhost:5173"
    cors_origins: str = "http://localhost:5173"
    datasf_base_url: str = "https://data.sfgov.org/resource/yitu-d5am.json"
    datasf_app_token: str | None = None
    datasf_timeout_seconds: float = 10.0

    @property
    def allowed_origins(self) -> list[str]:
        """Returns a list of allowed CORS origin URLs split from cors_origins or frontend_url."""
        origins = set()
        if self.cors_origins:
            origins.update(o.strip() for o in self.cors_origins.split(",") if o.strip())
        if self.frontend_url:
            origins.add(self.frontend_url.strip())
        return list(origins)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Returns a cached singleton instance of application settings."""
    return Settings()
