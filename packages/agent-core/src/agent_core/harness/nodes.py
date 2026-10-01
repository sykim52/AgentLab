"""Harness node implementations."""

from __future__ import annotations

import uuid
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage

from agent_lab.config import get_settings
from agent_lab.core.guardrails.injection import (
    scan_retrieved_for_injection,
    scan_text_for_injection,
)
from agent_lab.core.guardrails.policy import policy_for
from agent_lab.core.harness.state import AgentState
from agent_lab.core.models.stub import stub_answer, stub_plan, stub_select_skill
from agent_lab.integrations.mcp.envelope import ToolStatus
from agent_lab.integrations.mcp.tools import invoke_tool


def _cid(state: AgentState) -> str:
    return state.get("request_id") or str(uuid.uuid4())


def _app(state: AgentState) -> str:
    ctx = state.get("app_context") or {}
    return str(ctx.get("app") or "enterprise")


def input_guard(state: AgentState) -> dict[str, Any]:
    msg = state.get("user_message") or ""
    result = scan_text_for_injection(msg)
    if result.blocked:
        return {
            "security_flags": list(state.get("security_flags") or []) + result.flags,
            "outcome": "denied",
            "failure_reason": result.reason,
            "final_answer": (
                "Request blocked by input guard (prompt-injection heuristic). "
                "No tools were called."
            ),
            "messages": [AIMessage(content="Blocked by input_guard.")],
        }
    return {
        "iteration": int(state.get("iteration") or 0),
        "retry_count": int(state.get("retry_count") or 0),
        "needs_replan": False,
        "messages": [HumanMessage(content=msg)],
    }


def planner(state: AgentState) -> dict[str, Any]:
    if state.get("outcome") == "denied":
        return {}
    plan = stub_plan(state.get("user_message") or "", app=_app(state))
    return {
        "plan": plan,
        "needs_replan": False,
        "messages": [AIMessage(content=f"Plan: {' → '.join(plan)}")],
    }


def skill_selector(state: AgentState) -> dict[str, Any]:
    if state.get("outcome") == "denied":
        return {}
    skill = stub_select_skill(state.get("user_message") or "", app=_app(state))
    agent = {
        "ontology-graph": "ontology",
        "embedded-diagnostics": "embedded",
    }.get(skill, "knowledge")
    return {
        "selected_skill": skill,
        "selected_agent": agent,
        "messages": [AIMessage(content=f"Selected skill: {skill}")],
    }


def _pick_ontology_tool(state: AgentState) -> tuple[str, dict[str, Any]]:
    user_message = state.get("user_message") or ""
    already = {c.get("name") for c in (state.get("tool_calls") or [])}
    if "graph_search" not in already:
        return "graph_search", {"query": user_message}
    if "graph_neighbors" not in already:
        for tr in reversed(state.get("tool_results") or []):
            if tr.get("tool") == "graph_search" and tr.get("status") == ToolStatus.OK.value:
                items = tr.get("items") or []
                if items:
                    return "graph_neighbors", {"node_id": items[0]["id"], "depth": 1}
        return "graph_neighbors", {"node_id": "sys-ai-platform", "depth": 1}
    return "graph_search", {"query": user_message}


def _pick_embedded_tool(state: AgentState) -> tuple[str, dict[str, Any]]:
    user_message = state.get("user_message") or ""
    already = {c.get("name") for c in (state.get("tool_calls") or [])}
    if "parse_logs" not in already:
        return "parse_logs", {"query": user_message, "use_fixture": True}
    if "lookup_known_issue" not in already:
        codes: list[str] = []
        for tr in reversed(state.get("tool_results") or []):
            if tr.get("tool") == "parse_logs" and tr.get("status") == ToolStatus.OK.value:
                for item in tr.get("items") or []:
                    code = item.get("code")
                    if code and code not in codes:
                        codes.append(str(code))
                break
        return "lookup_known_issue", {"codes": codes or ["PERCEPTION_TIMEOUT"]}
    return "parse_logs", {"query": user_message, "use_fixture": True}


def _pick_enterprise_tool(state: AgentState) -> tuple[str, dict[str, Any]]:
    user_message = state.get("user_message") or ""
    plan = state.get("plan") or []
    already = {c.get("name") for c in (state.get("tool_calls") or [])}
    tool_name = "search_documents"
    args: dict[str, Any] = {"query": user_message}

    if any("query_structured" in p for p in plan) and "query_structured_data" not in already:
        tool_name = "query_structured_data"
        args = {"entity": "departments"}
    elif "search_documents" in already and "read_document" not in already:
        for tr in reversed(state.get("tool_results") or []):
            if tr.get("tool") == "search_documents" and tr.get("status") == ToolStatus.OK.value:
                items = tr.get("items") or []
                if items:
                    tool_name = "read_document"
                    args = {"document_id": items[0]["id"]}
                    break
    return tool_name, args


def tool_executor(state: AgentState) -> dict[str, Any]:
    if state.get("outcome") == "denied":
        return {}
    settings = get_settings()
    skill = state.get("selected_skill")
    policy = policy_for(skill)
    correlation_id = _cid(state)
    app = _app(state)

    if app == "ontology" or skill == "ontology-graph":
        tool_name, args = _pick_ontology_tool(state)
    elif app in {"embedded", "automotive"} or skill == "embedded-diagnostics":
        tool_name, args = _pick_embedded_tool(state)
    else:
        tool_name, args = _pick_enterprise_tool(state)

    envelope = invoke_tool(
        tool_name,
        args,
        correlation_id=correlation_id,
        allowed_tools=policy.allowed_tools,
    )

    call_rec = {"name": tool_name, "args": args, "correlation_id": correlation_id}
    result_rec = {
        "tool": tool_name,
        "status": envelope.status.value,
        "items": envelope.items,
        "message": envelope.message,
        "provenance": envelope.provenance,
    }

    updates: dict[str, Any] = {
        "tool_calls": list(state.get("tool_calls") or []) + [call_rec],
        "tool_results": list(state.get("tool_results") or []) + [result_rec],
        "iteration": int(state.get("iteration") or 0) + 1,
        "last_tool_error": None,
        "messages": [
            AIMessage(
                content=f"Tool {tool_name} → {envelope.status.value} "
                f"({len(envelope.items)} items)"
            )
        ],
    }

    if envelope.status == ToolStatus.DENIED:
        updates["security_flags"] = list(state.get("security_flags") or []) + [
            f"tool_denied:{tool_name}"
        ]
        updates["outcome"] = "denied"
        updates["failure_reason"] = envelope.message
        updates["final_answer"] = f"Denied: {envelope.message}"
        return updates

    if envelope.status in {
        ToolStatus.ERROR,
        ToolStatus.TIMEOUT,
        ToolStatus.UNAVAILABLE,
    }:
        retry = int(state.get("retry_count") or 0) + 1
        updates["retry_count"] = retry
        updates["last_tool_error"] = envelope.message or envelope.status.value
        if retry > settings.agent_lab_max_tool_retries:
            updates["needs_replan"] = True
            updates["retry_count"] = 0
        return updates

    if envelope.status == ToolStatus.OK:
        if tool_name in {"read_document", "query_structured_data", "graph_search", "graph_neighbors"}:
            updates["evidence"] = list(state.get("evidence") or []) + list(envelope.items)
        elif tool_name == "parse_logs":
            updates["evidence"] = list(state.get("evidence") or []) + list(envelope.items)
        elif tool_name == "lookup_known_issue":
            updates["evidence"] = list(state.get("evidence") or []) + list(envelope.items)

    return updates


def verifier(state: AgentState) -> dict[str, Any]:
    if state.get("outcome") in {"denied", "aborted"}:
        return {}
    settings = get_settings()
    iteration = int(state.get("iteration") or 0)
    if iteration >= settings.agent_lab_max_iterations:
        return {
            "outcome": "aborted",
            "failure_reason": "max_iterations_exceeded",
            "final_answer": (
                "Stopped: max iterations reached without a verified answer "
                f"(limit={settings.agent_lab_max_iterations})."
            ),
        }

    bodies = [
        str(e.get("body") or e.get("snippet") or e.get("description") or e.get("message") or "")
        for e in (state.get("evidence") or [])
    ]
    inj = scan_retrieved_for_injection(bodies)
    if inj.blocked:
        return {
            "security_flags": list(state.get("security_flags") or []) + inj.flags,
            "outcome": "denied",
            "failure_reason": inj.reason,
            "final_answer": (
                "Blocked: retrieved content contained injection-like instructions. "
                "Evidence was not used for the answer."
            ),
            "evidence": [],
        }

    results = state.get("tool_results") or []
    ok = any(r.get("status") == ToolStatus.OK.value for r in results)
    if not ok and state.get("last_tool_error"):
        return {"needs_replan": True}

    names = {c.get("name") for c in (state.get("tool_calls") or [])}
    app = _app(state)

    # Track A: search then neighbors
    if app == "ontology" or state.get("selected_skill") == "ontology-graph":
        if "graph_search" in names and "graph_neighbors" not in names:
            search_ok = any(
                r.get("tool") == "graph_search" and r.get("status") == ToolStatus.OK.value
                for r in results
            )
            if search_ok:
                return {}
        if ok and (state.get("evidence") or []):
            return {"needs_replan": False}
        if not ok and not (state.get("evidence") or []):
            return {
                "needs_replan": True,
                "messages": [AIMessage(content="Verifier: insufficient graph evidence → re-plan")],
            }
        return {"needs_replan": False}

    # Track B: parse then lookup
    if app in {"embedded", "automotive"} or state.get("selected_skill") == "embedded-diagnostics":
        if "parse_logs" in names and "lookup_known_issue" not in names:
            parse_ok = any(
                r.get("tool") == "parse_logs" and r.get("status") == ToolStatus.OK.value
                for r in results
            )
            if parse_ok:
                return {}
        if ok and (state.get("evidence") or []):
            return {"needs_replan": False}
        if not ok and not (state.get("evidence") or []):
            return {
                "needs_replan": True,
                "messages": [AIMessage(content="Verifier: insufficient log evidence → re-plan")],
            }
        return {"needs_replan": False}

    # Enterprise: search then read
    if "search_documents" in names and "read_document" not in names:
        search_ok = any(
            r.get("tool") == "search_documents" and r.get("status") == ToolStatus.OK.value
            for r in results
        )
        if search_ok:
            return {}

    if not ok and not (state.get("evidence") or []):
        return {
            "needs_replan": True,
            "messages": [AIMessage(content="Verifier: insufficient evidence → re-plan")],
        }

    return {"needs_replan": False}


def security_check(state: AgentState) -> dict[str, Any]:
    if state.get("outcome") in {"denied", "aborted"}:
        return {}
    if state.get("approval_required"):
        return {
            "outcome": "needs_approval",
            "final_answer": "Action requires human approval (HITL interrupt stub).",
        }
    return {}


def response_builder(state: AgentState) -> dict[str, Any]:
    if state.get("final_answer"):
        return {
            "outcome": state.get("outcome") or "ok",
            "messages": [AIMessage(content=state["final_answer"])],
        }
    answer = stub_answer(
        user_message=state.get("user_message") or "",
        evidence=list(state.get("evidence") or []),
        tool_results=list(state.get("tool_results") or []),
    )
    return {
        "final_answer": answer,
        "outcome": "ok",
        "messages": [AIMessage(content=answer)],
    }
