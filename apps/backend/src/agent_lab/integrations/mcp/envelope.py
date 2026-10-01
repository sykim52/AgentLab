"""MCP-style tool result envelope (local + MCP transport share the same shape)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class ToolStatus(StrEnum):
    OK = "ok"
    NO_RESULTS = "no_results"
    DENIED = "denied"
    INVALID_INPUT = "invalid_input"
    TIMEOUT = "timeout"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


class ToolEnvelope(BaseModel):
    schema_version: str = "1.0"
    dataset_version: str = "mock-v1"
    status: ToolStatus
    items: list[dict[str, Any]] = Field(default_factory=list)
    truncation: bool = False
    correlation_id: str | None = None
    message: str | None = None
    provenance: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
