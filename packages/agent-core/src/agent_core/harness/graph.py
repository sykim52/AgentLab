"""Compile the LangGraph Agent Harness."""

from __future__ import annotations

from typing import Any, Literal

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent_lab.config import get_settings
from agent_lab.core.harness import nodes
from agent_lab.core.harness.state import AgentState


def _after_guard(state: AgentState) -> Literal["planner", "response_builder"]:
    if state.get("outcome") == "denied":
        return "response_builder"
    return "planner"


def _after_verifier(
    state: AgentState,
) -> Literal["tool_executor", "planner", "security_check", "response_builder"]:
    if state.get("outcome") in {"denied", "aborted"}:
        return "response_builder"
    settings = get_settings()
    if int(state.get("iteration") or 0) >= settings.agent_lab_max_iterations:
        return "response_builder"
    if state.get("needs_replan"):
        return "planner"
    names = {c.get("name") for c in (state.get("tool_calls") or [])}
    # Enterprise: search → read
    if "search_documents" in names and "read_document" not in names:
        for r in state.get("tool_results") or []:
            if r.get("tool") == "search_documents" and r.get("status") == "ok":
                return "tool_executor"
    # Track A: graph_search → graph_neighbors
    if "graph_search" in names and "graph_neighbors" not in names:
        for r in state.get("tool_results") or []:
            if r.get("tool") == "graph_search" and r.get("status") == "ok":
                return "tool_executor"
    # Track B: parse_logs → lookup_known_issue
    if "parse_logs" in names and "lookup_known_issue" not in names:
        for r in state.get("tool_results") or []:
            if r.get("tool") == "parse_logs" and r.get("status") == "ok":
                return "tool_executor"
    if state.get("last_tool_error") and int(state.get("retry_count") or 0) > 0:
        return "tool_executor"
    return "security_check"


def build_harness(*, checkpointer: Any | None = None):
    """Build and compile the enterprise-capable harness graph."""
    g: StateGraph = StateGraph(AgentState)
    g.add_node("input_guard", nodes.input_guard)
    g.add_node("planner", nodes.planner)
    g.add_node("skill_selector", nodes.skill_selector)
    g.add_node("tool_executor", nodes.tool_executor)
    g.add_node("verifier", nodes.verifier)
    g.add_node("security_check", nodes.security_check)
    g.add_node("response_builder", nodes.response_builder)

    g.add_edge(START, "input_guard")
    g.add_conditional_edges(
        "input_guard",
        _after_guard,
        {"planner": "planner", "response_builder": "response_builder"},
    )
    g.add_edge("planner", "skill_selector")
    g.add_edge("skill_selector", "tool_executor")
    g.add_edge("tool_executor", "verifier")
    g.add_conditional_edges(
        "verifier",
        _after_verifier,
        {
            "tool_executor": "tool_executor",
            "planner": "planner",
            "security_check": "security_check",
            "response_builder": "response_builder",
        },
    )
    g.add_edge("security_check", "response_builder")
    g.add_edge("response_builder", END)

    saver = checkpointer if checkpointer is not None else MemorySaver()
    return g.compile(checkpointer=saver)


def initial_state(
    *,
    user_message: str,
    request_id: str,
    thread_id: str,
    app: str = "enterprise",
) -> AgentState:
    return AgentState(
        messages=[],
        request_id=request_id,
        thread_id=thread_id,
        user_message=user_message,
        plan=[],
        selected_skill=None,
        selected_agent=None,
        tool_calls=[],
        tool_results=[],
        evidence=[],
        security_flags=[],
        retry_count=0,
        iteration=0,
        approval_required=False,
        failure_reason=None,
        final_answer=None,
        outcome=None,
        app_context={"app": app},
        needs_replan=False,
        last_tool_error=None,
    )


def run_harness(
    user_message: str,
    *,
    app: str = "enterprise",
    request_id: str | None = None,
    thread_id: str | None = None,
    graph=None,
) -> AgentState:
    import uuid

    rid = request_id or str(uuid.uuid4())
    tid = thread_id or rid
    compiled = graph or build_harness()
    state = initial_state(
        user_message=user_message,
        request_id=rid,
        thread_id=tid,
        app=app,
    )
    result = compiled.invoke(
        state,
        config={"configurable": {"thread_id": tid}},
    )
    return result  # type: ignore[return-value]
