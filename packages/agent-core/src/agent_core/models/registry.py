"""Model provider abstraction — open-model first (no OpenAI-centric default)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol


class ModelFamily(StrEnum):
    LLAMA = "llama"
    MISTRAL = "mistral"
    QWEN = "qwen"
    STUB = "stub"
    OTHER = "other"


class ModelPurpose(StrEnum):
    CHAT = "chat"
    TOOL = "tool"
    STRUCTURED = "structured"
    LOG_REASONING = "log_reasoning"
    GRAPH_QUERY = "graph_query"
    DIAGNOSTIC = "diagnostic"


class ChatModelProvider(Protocol):
    family: ModelFamily

    async def invoke(self, messages: list[dict[str, Any]], **kwargs: Any) -> str: ...

    async def stream(self, messages: list[dict[str, Any]], **kwargs: Any): ...

    async def structured_output(
        self, messages: list[dict[str, Any]], schema: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]: ...

    async def tool_call(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], **kwargs: Any
    ) -> dict[str, Any]: ...


_REGISTRY: dict[tuple[ModelFamily, ModelPurpose, str], ChatModelProvider] = {}


def register_model(
    family: ModelFamily,
    purpose: ModelPurpose,
    provider: ChatModelProvider,
    profile: str = "default",
) -> None:
    _REGISTRY[(family, purpose, profile)] = provider


def get_model(
    family: ModelFamily,
    purpose: ModelPurpose = ModelPurpose.CHAT,
    profile: str = "default",
) -> ChatModelProvider:
    key = (family, purpose, profile)
    if key in _REGISTRY:
        return _REGISTRY[key]
    # Fallback to stub for local/tests until open-model adapters land.
    from agent_lab.core.models.stub_provider import StubChatProvider

    return StubChatProvider()
