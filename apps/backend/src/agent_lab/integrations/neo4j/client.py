"""Neo4j client — Track A. Stub wraps the in-memory GraphStore until a live driver is wired."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agent_lab.tracks.ontology_rag.graph.store import GraphStore, get_graph_store


@dataclass
class Neo4jConfig:
    """Local Neo4j connection settings — never commit real passwords.

    Defaults are empty; load from env (NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD).
    """

    uri: str = "bolt://127.0.0.1:7687"
    user: str = "neo4j"
    password: str = ""
    database: str = "neo4j"

    @classmethod
    def from_env(cls) -> Neo4jConfig:
        import os

        return cls(
            uri=os.getenv("NEO4J_URI", "bolt://127.0.0.1:7687"),
            user=os.getenv("NEO4J_USER", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
        )


class Neo4jClientStub:
    """In-memory stand-in so Track A works without a live Neo4j process."""

    def __init__(self, store: GraphStore | None = None) -> None:
        self._store = store or get_graph_store()

    @property
    def nodes(self) -> dict[str, dict[str, Any]]:
        return self._store.nodes

    @property
    def edges(self) -> list[dict[str, Any]]:
        return self._store.edges

    def upsert_node(self, node_id: str, labels: list[str], props: dict[str, Any]) -> None:
        self._store.upsert_node(node_id, labels, props)

    def upsert_edge(
        self, source_id: str, rel_type: str, target_id: str, props: dict[str, Any] | None = None
    ) -> None:
        self._store.upsert_edge(source_id, rel_type, target_id, props)

    def search(self, query: str, *, limit: int = 8) -> list[dict[str, Any]]:
        return self._store.search(query, limit=limit)

    def neighbors(self, node_id: str, *, depth: int = 1) -> dict[str, Any]:
        return self._store.neighbors(node_id, depth=depth)

    def cypher_stub(self, _query: str) -> list[dict[str, Any]]:
        snap = self._store.snapshot()
        return [
            {
                "note": "stub — connect neo4j driver for real Cypher",
                "node_count": snap["node_count"],
                "edge_count": snap["edge_count"],
            }
        ]
