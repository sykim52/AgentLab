"""Stub chat model — deterministic, no API key (tests + local demo)."""

from __future__ import annotations


def stub_plan(user_message: str, *, app: str = "enterprise") -> list[str]:
    msg = user_message.lower()
    app_l = (app or "enterprise").lower()

    if app_l in {"ontology"}:
        return [
            "graph_search for matching entities",
            "graph_neighbors for top hit",
            "answer from graph evidence",
        ]
    if app_l in {"embedded", "automotive"}:
        return [
            "parse_logs for failure codes",
            "lookup_known_issue for matched codes",
            "compose diagnostic report",
        ]

    if "pto" in msg or "leave" in msg or "vacation" in msg:
        return [
            "search_documents for PTO policy",
            "read top document",
            "summarize with citations",
        ]
    if "security" in msg or "acceptable use" in msg:
        return [
            "search_documents for security policy",
            "read top document",
            "summarize with citations",
        ]
    if "department" in msg:
        return [
            "query_structured_data departments",
            "answer from structured rows",
        ]
    return [
        "search_documents for user query",
        "read top document if found",
        "answer with evidence or say insufficient",
    ]


def stub_select_skill(user_message: str, *, app: str = "enterprise") -> str:
    msg = user_message.lower()
    app_l = (app or "enterprise").lower()
    if app_l == "ontology":
        return "ontology-graph"
    if app_l in {"embedded", "automotive"}:
        return "embedded-diagnostics"
    if "incident" in msg or "outage" in msg:
        return "incident-triage"
    return "enterprise-search"


def stub_answer(*, user_message: str, evidence: list[dict], tool_results: list[dict]) -> str:
    if not evidence and not tool_results:
        return (
            "I could not find supporting evidence in the mock corpus. "
            "Please refine the query. (stub model)"
        )

    # Track B diagnostic report in evidence
    for e in evidence:
        if "hypotheses" in e and "suspected_components" in e:
            hyps = e.get("hypotheses") or []
            lines = [
                "Diagnostic report (software-only simulation — not production HIL):",
                f"Suspected: {', '.join(e.get('suspected_components') or []) or 'n/a'}",
                f"Confidence: {e.get('confidence', 0)}",
            ]
            for h in hyps[:3]:
                lines.append(f"- {h.get('summary')} (status={h.get('validation_status')})")
            actions = e.get("next_actions") or []
            if actions:
                lines.append("Next: " + "; ".join(actions[:3]))
            lines.append(f"(Query: {user_message!r})")
            return "\n".join(lines)

    cites = []
    for e in evidence:
        doc_id = e.get("id") or e.get("document_id") or e.get("name")
        title = e.get("title") or e.get("name") or ""
        if doc_id:
            cites.append(f"[{doc_id}] {title}".strip())
    body_bits = []
    for e in evidence:
        if e.get("body"):
            body_bits.append(str(e["body"])[:240])
        elif e.get("snippet"):
            body_bits.append(str(e["snippet"]))
        elif e.get("description"):
            body_bits.append(str(e["description"])[:240])
        elif e.get("message"):
            body_bits.append(str(e["message"])[:240])
    summary = " ".join(body_bits) if body_bits else "See cited evidence."
    cite_line = "; ".join(cites) if cites else "(no citations)"
    return (
        f"Based on mock fixtures (not production search):\n{summary}\n\n"
        f"Evidence: {cite_line}\n"
        f"(Query: {user_message!r})"
    )
