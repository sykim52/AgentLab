from __future__ import annotations

from agent_lab.core.harness.graph import run_harness
from agent_lab.tracks.embedded_adas.diagnostics.engine import diagnose_events
from agent_lab.tracks.embedded_adas.logs.parser import parse_log_text
from agent_lab.tracks.ontology_rag.graph.store import get_graph_store


def test_graph_seed_and_search():
    store = get_graph_store(refresh=True)
    assert store.snapshot()["node_count"] >= 10
    hits = store.search("LangGraph")
    assert any(h["id"] == "tech-langgraph" for h in hits)
    nb = store.neighbors("sys-ai-platform", depth=1)
    assert len(nb["edges"]) >= 1


def test_ontology_harness_path():
    result = run_harness(
        "Which technologies does the AI Platform use?",
        app="ontology",
    )
    assert result["outcome"] == "ok"
    assert result["selected_skill"] == "ontology-graph"
    names = [c["name"] for c in result["tool_calls"]]
    assert "graph_search" in names
    assert "graph_neighbors" in names
    assert result["evidence"]
    assert result["final_answer"]


def test_embedded_harness_path():
    result = run_harness(
        "Diagnose the perception timeout in the sample log",
        app="embedded",
    )
    assert result["outcome"] == "ok"
    assert result["selected_skill"] == "embedded-diagnostics"
    names = [c["name"] for c in result["tool_calls"]]
    assert "parse_logs" in names
    assert "lookup_known_issue" in names
    assert result["final_answer"]
    assert "software-only" in (result["final_answer"] or "").lower() or "Perception" in (
        result["final_answer"] or ""
    )


def test_diagnose_events_from_fixture():
    from pathlib import Path

    text = Path("fixtures/embedded_adas/sample_perception_timeout.log").read_text(
        encoding="utf-8"
    )
    events, malformed = parse_log_text(text)
    assert malformed >= 1
    report = diagnose_events(events)
    assert report.hypotheses
    assert "Perception Stack" in report.suspected_components
