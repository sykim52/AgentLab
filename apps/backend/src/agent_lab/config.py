"""Runtime settings (env / .env). Secrets never belong in code."""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    agent_lab_model_provider: str = "stub"
    agent_lab_max_iterations: int = 6
    agent_lab_max_tool_retries: int = 2

    otel_sdk_disabled: bool = True
    otel_tracing_enabled: bool = False
    langsmith_tracing: bool = False
    langsmith_api_key: str | None = None
    langsmith_project: str = "agent-lab"
    langsmith_endpoint: str | None = None

    agent_lab_api_host: str = "127.0.0.1"
    agent_lab_api_port: int = 8080


@lru_cache
def get_settings() -> Settings:
    return Settings()
