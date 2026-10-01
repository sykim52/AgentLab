"""LangGraph AgentState — interview-defendable shared state."""

from __future__ import annotations

from typing import Annotated, Any, Literal, NotRequired, TypedDict

from langgraph.graph.message import add_messages

Outcome = Literal["ok", "denied", "error", "needs_approval", "aborted"]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    request_id: str
    thread_id: str
    user_message: str
    plan: list[str]
    selected_skill: str | None
    selected_agent: str | None
    tool_calls: list[dict[str, Any]]
    tool_results: list[dict[str, Any]]
    evidence: list[dict[str, Any]]
    security_flags: list[str]
    retry_count: int
    iteration: int
    approval_required: bool
    failure_reason: str | None
    final_answer: str | None
    outcome: Outcome | None
    app_context: dict[str, Any]
    # Internal control flags for routing
    needs_replan: NotRequired[bool]
    last_tool_error: NotRequired[str | None]
