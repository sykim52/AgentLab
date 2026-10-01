"""Local mock tools with MCP envelope semantics (same names as future MCP server)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_lab.integrations.mcp.envelope import ToolEnvelope, ToolStatus
from agent_lab.integrations.mcp.fixtures import DOCUMENTS

ALLOWED_TOOLS = frozenset(
    {
        "search_documents",
        "read_document",
        "query_structured_data",
        "graph_search",
        "graph_neighbors",
        "parse_logs",
        "lookup_known_issue",
    }
)

DANGEROUS_TOOLS = frozenset({"admin_export", "delete_document"})

_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "for",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "with",
        "me",
        "my",
        "please",
        "summary",
        "summarize",
        "about",
        "tell",
    }
)

# tools.py → mcp → integrations → agent_lab → src → backend → apps → repo root
_FIXTURE_LOG = (
    Path(__file__).resolve().parents[6]
    / "fixtures"
    / "embedded_adas"
    / "sample_perception_timeout.log"
)


def _query_tokens(query: str) -> list[str]:
    raw = (query or "").lower()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in raw)
    return [t for t in cleaned.split() if len(t) > 2 and t not in _STOPWORDS]


def search_documents(
    *,
    query: str,
    correlation_id: str | None = None,
    limit: int = 5,
) -> ToolEnvelope:
    tokens = _query_tokens(query)
    if not tokens:
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="query is required",
        )
    scored: list[tuple[int, dict[str, Any]]] = []
    for doc in DOCUMENTS:
        hay = f"{doc['title']} {doc['body']} {' '.join(doc['tags'])}".lower()
        hay_tokens = set(
            "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in hay).split()
        )
        score = sum(1 for tok in tokens if tok in hay_tokens)
        if doc.get("department") == "External":
            score -= 1
        if score > 0:
            scored.append(
                (
                    score,
                    {
                        "id": doc["id"],
                        "title": doc["title"],
                        "department": doc["department"],
                        "snippet": doc["body"][:160],
                    },
                )
            )
    scored.sort(key=lambda x: x[0], reverse=True)
    hits = [item for _, item in scored[:limit]]
    if not hits:
        return ToolEnvelope(
            status=ToolStatus.NO_RESULTS,
            correlation_id=correlation_id,
            message="no matching documents",
            provenance={"source": "mock_fixtures"},
        )
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=hits,
        truncation=len(scored) > limit,
        correlation_id=correlation_id,
        provenance={"source": "mock_fixtures", "tool": "search_documents"},
    )


def read_document(
    *,
    document_id: str,
    correlation_id: str | None = None,
    allowed_ids: set[str] | None = None,
) -> ToolEnvelope:
    doc_id = (document_id or "").strip()
    if not doc_id:
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="document_id is required",
        )
    if allowed_ids is not None and doc_id not in allowed_ids:
        return ToolEnvelope(
            status=ToolStatus.DENIED,
            correlation_id=correlation_id,
            message="document not in caller allowlist",
            provenance={"document_id": doc_id},
        )
    for doc in DOCUMENTS:
        if doc["id"] == doc_id:
            return ToolEnvelope(
                status=ToolStatus.OK,
                items=[dict(doc)],
                correlation_id=correlation_id,
                provenance={"source": "mock_fixtures", "tool": "read_document"},
            )
    return ToolEnvelope(
        status=ToolStatus.NO_RESULTS,
        correlation_id=correlation_id,
        message="document not found",
    )


def query_structured_data(
    *,
    entity: str,
    correlation_id: str | None = None,
) -> ToolEnvelope:
    table = {
        "departments": [
            {"id": "hr", "name": "Human Resources"},
            {"id": "sec", "name": "Security"},
            {"id": "fac", "name": "Facilities"},
        ]
    }
    key = (entity or "").strip().lower()
    if key not in table:
        return ToolEnvelope(
            status=ToolStatus.NO_RESULTS,
            correlation_id=correlation_id,
            message=f"unknown entity '{entity}'",
        )
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=table[key],
        correlation_id=correlation_id,
        provenance={"source": "mock_fixtures", "tool": "query_structured_data"},
    )


def graph_search_tool(
    *,
    query: str,
    correlation_id: str | None = None,
    limit: int = 8,
) -> ToolEnvelope:
    from agent_lab.tracks.ontology_rag.retrieval.graph_tools import graph_search

    q = (query or "").strip()
    if not q:
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="query is required",
        )
    hits = graph_search(q, limit=limit)
    if not hits:
        return ToolEnvelope(
            status=ToolStatus.NO_RESULTS,
            correlation_id=correlation_id,
            message="no matching graph nodes",
            provenance={"source": "in_memory_graph"},
        )
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=hits,
        correlation_id=correlation_id,
        provenance={"source": "in_memory_graph", "tool": "graph_search"},
    )


def graph_neighbors_tool(
    *,
    node_id: str,
    correlation_id: str | None = None,
    depth: int = 1,
) -> ToolEnvelope:
    from agent_lab.tracks.ontology_rag.retrieval.graph_tools import graph_neighbors

    nid = (node_id or "").strip()
    if not nid:
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="node_id is required",
        )
    result = graph_neighbors(nid, depth=depth)
    if not result.get("nodes"):
        return ToolEnvelope(
            status=ToolStatus.NO_RESULTS,
            correlation_id=correlation_id,
            message=result.get("message") or "no neighbors",
            provenance={"source": "in_memory_graph", "node_id": nid},
        )
    items = [
        {
            "id": result["node_id"],
            "title": f"Neighborhood of {result['node_id']}",
            "body": (
                f"nodes={len(result['nodes'])} edges={len(result['edges'])}; "
                + ", ".join(
                    f"{e['source']}-[{e['type']}]->{e['target']}" for e in result["edges"][:8]
                )
            ),
            "nodes": result["nodes"],
            "edges": result["edges"],
        }
    ]
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=items,
        correlation_id=correlation_id,
        provenance={"source": "in_memory_graph", "tool": "graph_neighbors"},
    )


def _resolve_log_text(args: dict[str, Any]) -> str:
    if args.get("log_text"):
        return str(args["log_text"])
    if args.get("use_fixture") or args.get("query"):
        # Prefer embedded sample when user asks about perception / timeout / logs
        q = str(args.get("query") or "").lower()
        if args.get("use_fixture") or any(
            k in q for k in ("perception", "timeout", "sensor", "log", "diagnos", "adas")
        ):
            if _FIXTURE_LOG.is_file():
                return _FIXTURE_LOG.read_text(encoding="utf-8")
    # Inline log lines in the query itself
    query = str(args.get("query") or "")
    if "|" in query:
        return query
    if _FIXTURE_LOG.is_file():
        return _FIXTURE_LOG.read_text(encoding="utf-8")
    return ""


def parse_logs_tool(
    *,
    args: dict[str, Any],
    correlation_id: str | None = None,
) -> ToolEnvelope:
    from agent_lab.tracks.embedded_adas.logs.parser import parse_log_text

    text = _resolve_log_text(args)
    if not text.strip():
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="log_text is empty",
        )
    events, malformed = parse_log_text(text)
    if not events:
        return ToolEnvelope(
            status=ToolStatus.NO_RESULTS,
            correlation_id=correlation_id,
            message=f"no valid events (malformed={malformed})",
            provenance={"source": "log_parser"},
        )
    items = [
        {
            "id": f"evt-{i}",
            "title": f"{e.code or e.component} @ {e.timestamp}",
            "body": e.message,
            "timestamp": e.timestamp,
            "component": e.component,
            "severity": e.severity.value,
            "code": e.code,
            "message": e.message,
        }
        for i, e in enumerate(events)
    ]
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=items,
        correlation_id=correlation_id,
        provenance={
            "source": "log_parser",
            "tool": "parse_logs",
            "malformed": malformed,
            "event_count": len(events),
        },
    )


def lookup_known_issue_tool(
    *,
    code: str | None = None,
    codes: list[str] | None = None,
    correlation_id: str | None = None,
) -> ToolEnvelope:
    from agent_lab.tracks.embedded_adas.diagnostics.engine import diagnose_events
    from agent_lab.tracks.embedded_adas.domain.models import LogEvent, Severity
    from agent_lab.tracks.embedded_adas.simulation.known_issues import lookup_known_issue

    code_list = list(codes or [])
    if code:
        code_list.append(code)
    code_list = [c.strip().upper() for c in code_list if c and c.strip()]
    if not code_list:
        return ToolEnvelope(
            status=ToolStatus.INVALID_INPUT,
            correlation_id=correlation_id,
            message="code or codes required",
        )

    # Prefer full diagnose path when multiple codes
    fake_events = [
        LogEvent(
            timestamp="",
            component="UNKNOWN",
            severity=Severity.ERROR,
            code=c,
            message=c,
        )
        for c in code_list
    ]
    report = diagnose_events(fake_events)
    items: list[dict[str, Any]] = [report.model_dump()]
    for c in code_list:
        issue = lookup_known_issue(c)
        if issue:
            items.append({"id": c, "title": issue["title"], "body": issue["summary"], **issue})
    return ToolEnvelope(
        status=ToolStatus.OK,
        items=items,
        correlation_id=correlation_id,
        provenance={"source": "known_issues", "tool": "lookup_known_issue"},
    )


def invoke_tool(
    name: str,
    args: dict[str, Any],
    *,
    correlation_id: str | None = None,
    allowed_tools: frozenset[str] | None = None,
) -> ToolEnvelope:
    allow = allowed_tools if allowed_tools is not None else ALLOWED_TOOLS
    if name in DANGEROUS_TOOLS:
        return ToolEnvelope(
            status=ToolStatus.DENIED,
            correlation_id=correlation_id,
            message=f"tool '{name}' requires HITL approval",
        )
    if name not in allow:
        return ToolEnvelope(
            status=ToolStatus.DENIED,
            correlation_id=correlation_id,
            message=f"tool '{name}' not permitted",
        )
    if name == "search_documents":
        return search_documents(
            query=str(args.get("query", "")),
            correlation_id=correlation_id,
            limit=int(args.get("limit", 5)),
        )
    if name == "read_document":
        return read_document(
            document_id=str(args.get("document_id", "")),
            correlation_id=correlation_id,
        )
    if name == "query_structured_data":
        return query_structured_data(
            entity=str(args.get("entity", "")),
            correlation_id=correlation_id,
        )
    if name == "graph_search":
        return graph_search_tool(
            query=str(args.get("query", "")),
            correlation_id=correlation_id,
            limit=int(args.get("limit", 8)),
        )
    if name == "graph_neighbors":
        return graph_neighbors_tool(
            node_id=str(args.get("node_id", "")),
            correlation_id=correlation_id,
            depth=int(args.get("depth", 1)),
        )
    if name == "parse_logs":
        return parse_logs_tool(args=args, correlation_id=correlation_id)
    if name == "lookup_known_issue":
        codes = args.get("codes")
        code_list = [str(c) for c in codes] if isinstance(codes, list) else None
        return lookup_known_issue_tool(
            code=str(args.get("code", "")) or None,
            codes=code_list,
            correlation_id=correlation_id,
        )
    return ToolEnvelope(
        status=ToolStatus.ERROR,
        correlation_id=correlation_id,
        message=f"unknown tool '{name}'",
    )
