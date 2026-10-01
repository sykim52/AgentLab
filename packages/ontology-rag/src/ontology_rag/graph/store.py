"""In-memory property graph used by Track A tools and Graph Explorer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphStore:
    nodes: dict[str, dict[str, Any]] = field(default_factory=dict)
    edges: list[dict[str, Any]] = field(default_factory=list)

    def upsert_node(self, node_id: str, labels: list[str], props: dict[str, Any]) -> None:
        self.nodes[node_id] = {"id": node_id, "labels": labels, "props": dict(props)}

    def upsert_edge(
        self,
        source_id: str,
        rel_type: str,
        target_id: str,
        props: dict[str, Any] | None = None,
    ) -> None:
        self.edges.append(
            {
                "source": source_id,
                "type": rel_type,
                "target": target_id,
                "props": props or {},
            }
        )

    def search(self, query: str, *, limit: int = 8) -> list[dict[str, Any]]:
        tokens = _tokens(query)
        if not tokens:
            return []
        scored: list[tuple[int, dict[str, Any]]] = []
        for node in self.nodes.values():
            hay = _node_haystack(node)
            score = sum(1 for tok in tokens if tok in hay)
            if score > 0:
                scored.append((score, _public_node(node)))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        return [item for _, item in scored[:limit]]

    def neighbors(self, node_id: str, *, depth: int = 1, limit: int = 24) -> dict[str, Any]:
        if node_id not in self.nodes:
            return {"node_id": node_id, "nodes": [], "edges": [], "message": "node not found"}
        frontier = {node_id}
        seen_nodes = {node_id}
        seen_edges: list[dict[str, Any]] = []
        for _ in range(max(1, depth)):
            nxt: set[str] = set()
            for edge in self.edges:
                src, tgt = edge["source"], edge["target"]
                if src in frontier or tgt in frontier:
                    if edge not in seen_edges:
                        seen_edges.append(edge)
                    if src not in seen_nodes:
                        seen_nodes.add(src)
                        nxt.add(src)
                    if tgt not in seen_nodes:
                        seen_nodes.add(tgt)
                        nxt.add(tgt)
            frontier = nxt
            if not frontier:
                break
        nodes = [_public_node(self.nodes[nid]) for nid in seen_nodes if nid in self.nodes]
        edges = seen_edges[:limit]
        return {
            "node_id": node_id,
            "nodes": nodes[: limit + 1],
            "edges": edges,
            "message": "ok",
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "nodes": [_public_node(n) for n in self.nodes.values()],
            "edges": list(self.edges),
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
        }


_STOPWORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "what",
        "which",
        "who",
        "for",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "with",
        "me",
        "please",
        "about",
        "tell",
        "show",
        "find",
        "related",
        "connected",
    }
)


def _tokens(query: str) -> list[str]:
    raw = (query or "").lower()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in raw)
    return [t for t in cleaned.split() if len(t) > 1 and t not in _STOPWORDS]


def _node_haystack(node: dict[str, Any]) -> str:
    props = node.get("props") or {}
    parts = [
        node.get("id", ""),
        " ".join(node.get("labels") or []),
        str(props.get("name", "")),
        " ".join(props.get("aliases") or []),
        str(props.get("description", "")),
        " ".join(str(v) for v in props.values() if isinstance(v, str)),
    ]
    return " ".join(parts).lower()


def _public_node(node: dict[str, Any]) -> dict[str, Any]:
    props = dict(node.get("props") or {})
    return {
        "id": node["id"],
        "labels": list(node.get("labels") or []),
        "name": props.get("name") or node["id"],
        "description": props.get("description"),
        "props": props,
    }


_DEFAULT: GraphStore | None = None


def get_graph_store(*, refresh: bool = False) -> GraphStore:
    global _DEFAULT
    if _DEFAULT is None or refresh:
        from agent_lab.tracks.ontology_rag.graph.seed import seed_graph

        store = GraphStore()
        seed_graph(store)
        _DEFAULT = store
    return _DEFAULT
