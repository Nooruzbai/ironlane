"""
Typed environment configuration, validated by pydantic-settings.

Values are read from environment variables first, then from the `.env` file in the
repository root. Invalid values (e.g. DEBUG=maybe) fail loudly at startup instead of
silently falling back to a default.
"""

from pathlib import Path
from typing import Annotated

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = False
    # In Docker this points at a mounted volume so submissions survive redeploys
    database_path: Path = REPO_ROOT / "source" / "db.sqlite3"
    # Required, with no fallback: put SECRET_KEY in `.env` locally and in GitHub secrets
    secret_key: SecretStr

    # Comma-separated in the environment: ALLOWED_HOSTS=example.com,www.example.com
    allowed_hosts: Annotated[list[str], NoDecode] = Field(
        default=["it-cons.com", "www.it-cons.com", "localhost", "127.0.0.1"]
    )

    # Set ENABLE_HTTPS=False only while running without a TLS certificate,
    # otherwise Django redirects to https:// and nothing is reachable.
    enable_https: bool = True
    prepend_www: bool = True

    email_host: str = "smtp.gmail.com"
    email_port: int = 465
    email_use_ssl: bool = True
    email_host_user: str = ""
    email_password: SecretStr = SecretStr("")
    default_from_email: str = "azat.usubakunov@gmail.com"
    # Where quote requests and driver applications are delivered
    inbox_email: str = "azat.usubakunov@gmail.com"

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def _split_csv(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return value

    @field_validator("secret_key")
    @classmethod
    def _secret_key_not_blank(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value().strip():
            raise ValueError("SECRET_KEY must not be empty")
        return value


config = AppSettings()
