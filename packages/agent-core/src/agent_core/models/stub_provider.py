"""Deterministic stub ChatModelProvider for tests / offline demos."""

from __future__ import annotations

from typing import Any

from agent_lab.core.models.registry import ModelFamily
from agent_lab.core.models.stub import stub_answer


class StubChatProvider:
    family = ModelFamily.STUB

    async def invoke(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
        user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user = str(m.get("content") or "")
                break
        return stub_answer(user_message=user, evidence=[], tool_results=[])

    async def stream(self, messages: list[dict[str, Any]], **kwargs: Any):
        text = await self.invoke(messages, **kwargs)
        yield text

    async def structured_output(
        self, messages: list[dict[str, Any]], schema: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]:
        _ = schema
        return {"answer": await self.invoke(messages, **kwargs)}

    async def tool_call(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], **kwargs: Any
    ) -> dict[str, Any]:
        _ = tools
        return {"name": "search_documents", "args": {"query": "demo"}}
