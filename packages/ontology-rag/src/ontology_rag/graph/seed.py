"""Seed synthetic enterprise + ADAS ontology graph for demos/tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_lab.tracks.ontology_rag.graph.store import GraphStore


def seed_graph(store: GraphStore) -> GraphStore:
    """Populate an empty GraphStore with interview-friendly fixtures."""

    def node(nid: str, etype: str, name: str, **props: object) -> None:
        store.upsert_node(
            nid,
            [etype],
            {"name": name, "entity_type": etype, **props},
        )

    def edge(src: str, rel: str, tgt: str, **props: object) -> None:
        store.upsert_edge(src, rel, tgt, props or None)

    # --- Enterprise / ontology demo ---
    node("org-acme", "Organization", "Acme Labs", description="Synthetic demo organization")
    node("dept-hr", "Department", "Human Resources")
    node("dept-sec", "Department", "Security")
    node("dept-platform", "Department", "Platform Engineering")
    node("person-alex", "Person", "Alex Kim", aliases=["alex"])
    node("role-engineer", "Role", "Staff Engineer")
    node("sys-ai-platform", "System", "AI Platform", aliases=["ai-platform", "platform"])
    node("svc-identity", "Service", "Identity Service", aliases=["identity"])
    node("tech-langgraph", "Technology", "LangGraph", aliases=["langgraph"])
    node("tech-neo4j", "Technology", "Neo4j", aliases=["neo4j", "graph database"])
    node("pol-pto", "Policy", "PTO Policy", aliases=["pto", "leave", "vacation"])
    node("pol-aup", "Policy", "Acceptable Use Policy", aliases=["security", "aup"])
    node(
        "doc-pto",
        "Document",
        "Employee Handbook — Leave",
        description="Employees receive 20 days PTO; manager approval required.",
        aliases=["pto policy", "leave policy"],
    )
    node(
        "inc-1001",
        "Incident",
        "INC-1001 Auth latency",
        description="Elevated auth latency on Identity Service",
        aliases=["outage", "incident"],
    )

    edge("dept-hr", "OWNS", "sys-ai-platform")  # illustrative ownership link
    edge("dept-platform", "OWNS", "sys-ai-platform")
    edge("sys-ai-platform", "OWNED_BY", "dept-platform")
    edge("sys-ai-platform", "USES", "tech-langgraph")
    edge("sys-ai-platform", "USES", "tech-neo4j")
    edge("sys-ai-platform", "DEPENDS_ON", "svc-identity")
    edge("pol-pto", "GOVERNS", "sys-ai-platform")
    edge("pol-aup", "GOVERNS", "sys-ai-platform")
    edge("person-alex", "BELONGS_TO", "dept-platform")
    edge("person-alex", "HAS_ROLE", "role-engineer")
    edge("inc-1001", "AFFECTS", "sys-ai-platform")
    edge("inc-1001", "AFFECTS", "svc-identity")
    edge("doc-pto", "MENTIONS", "pol-pto")  # soft link for search demos

    # --- Embedded / ADAS demo subgraph (same registry, separate IDs) ---
    node("veh-demo-1", "Vehicle", "Demo Vehicle A")
    node("ecu-adas", "ECU", "ADAS Domain Controller", aliases=["adas ecu"])
    node(
        "sw-perception",
        "SoftwareComponent",
        "Perception Stack",
        aliases=["perception", "perception module"],
    )
    node("sensor-lidar", "Sensor", "Front LiDAR", aliases=["lidar"])
    node("sensor-cam", "Sensor", "Front Camera", aliases=["camera"])
    node(
        "fc-perception-timeout",
        "FailureCode",
        "PERCEPTION_TIMEOUT",
        aliases=["perception_timeout"],
        description="Frame deadline missed in perception pipeline",
    )
    node(
        "fc-sensor-sync",
        "FailureCode",
        "SENSOR_SYNC_LOST",
        aliases=["sensor_sync_lost"],
        description="Camera-LiDAR temporal skew exceeded budget",
    )
    node(
        "tc-sil-perception",
        "TestCase",
        "SIL-Perception-Timeout-01",
        description="Software-in-the-loop replay for perception stall",
    )

    edge("veh-demo-1", "CONTAINS", "ecu-adas")
    edge("ecu-adas", "RUNS", "sw-perception")
    edge("sw-perception", "RUNS_ON", "ecu-adas")
    edge("fc-perception-timeout", "AFFECTS", "sw-perception")
    edge("fc-sensor-sync", "AFFECTS", "sw-perception")
    edge("sw-perception", "TESTED_BY", "tc-sil-perception")

    return store
