"""Graph retrieval helpers for Track A MCP-style tools."""

from __future__ import annotations

from typing import Any

from agent_lab.tracks.ontology_rag.graph.store import get_graph_store


def graph_search(query: str, *, limit: int = 8) -> list[dict[str, Any]]:
    return get_graph_store().search(query, limit=limit)


def graph_neighbors(node_id: str, *, depth: int = 1, limit: int = 24) -> dict[str, Any]:
    return get_graph_store().neighbors(node_id, depth=depth, limit=limit)
