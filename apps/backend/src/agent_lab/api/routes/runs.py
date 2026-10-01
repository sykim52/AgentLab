"""Run resource API: POST create → GET SSE events (async agent execution)."""

from __future__ import annotations

import asyncio
import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from agent_lab.api.streaming.broker import broker
from agent_lab.api.streaming.events import (
    CreateRunRequest,
    CreateRunResponse,
    RunEventType,
    RunStatus,
)
from agent_lab.core.harness.graph import run_harness
from agent_lab.core.observability.tracing import maybe_export_run_metadata

router = APIRouter(prefix="/api/v1", tags=["runs"])


async def _execute_run(run_id: str, message: str, application: str) -> None:
    await broker.set_status(run_id, RunStatus.RUNNING)
    await broker.publish(run_id, RunEventType.RUN_STARTED, {"application": application})
    try:
        # Harness is sync today — run in thread to keep event loop free for SSE.
        result = await asyncio.to_thread(
            run_harness,
            message,
            app=application,
            request_id=run_id,
            thread_id=run_id,
        )
        await broker.publish(
            run_id,
            RunEventType.PLAN_CREATED,
            {"plan": list(result.get("plan") or [])},
        )
        if result.get("selected_skill"):
            await broker.publish(
                run_id,
                RunEventType.SKILL_SELECTED,
                {"skill": result.get("selected_skill")},
            )
        for call in result.get("tool_calls") or []:
            await broker.publish(
                run_id,
                RunEventType.TOOL_COMPLETED,
                {"tool": call.get("name"), "arguments": call.get("arguments")},
            )
        for ev in result.get("evidence") or []:
            await broker.publish(run_id, RunEventType.EVIDENCE_ADDED, ev)
        for flag in result.get("security_flags") or []:
            await broker.publish(run_id, RunEventType.SECURITY_FLAGGED, {"flag": flag})
        if result.get("final_answer"):
            await broker.publish(
                run_id,
                RunEventType.ANSWER_DELTA,
                {"text": result.get("final_answer")},
            )
        failed = result.get("outcome") not in {"ok", "denied"}
        # denied is a completed guarded run, not transport failure
        if result.get("outcome") == "denied":
            failed = False
        await broker.complete(run_id, dict(result), failed=failed)
        maybe_export_run_metadata(
            {"run_id": run_id, "outcome": result.get("outcome"), "app": application}
        )
    except Exception as exc:  # noqa: BLE001 — surface as run.failed
        await broker.complete(
            run_id,
            {"outcome": "error", "failure_reason": str(exc), "final_answer": None},
            failed=True,
        )


@router.post("/runs", response_model=CreateRunResponse, status_code=202)
async def create_run(body: CreateRunRequest) -> CreateRunResponse:
    run_id = str(uuid.uuid4())
    session_id = body.session_id or str(uuid.uuid4())
    await broker.create(run_id)
    asyncio.create_task(_execute_run(run_id, body.message, body.application))
    return CreateRunResponse(
        run_id=run_id,
        session_id=session_id,
        status=RunStatus.QUEUED,
        events_url=f"/api/v1/runs/{run_id}/events",
    )


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict[str, Any]:
    status = broker.get_status(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="run not found")
    return {
        "run_id": run_id,
        "status": status,
        "result": broker.get_result(run_id),
    }


@router.get("/runs/{run_id}/events")
async def stream_run_events(run_id: str, last_event_id: int = 0) -> StreamingResponse:
    if broker.get_status(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")

    async def gen():
        async for event in broker.subscribe(run_id, after_sequence=last_event_id):
            payload = event.model_dump(mode="json")
            data = json.dumps(payload)
            yield (
                f"id: {event.sequence}\nevent: {event.type.value}\ndata: {data}\n\n"
            )

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/ontology")
def get_ontology() -> dict[str, Any]:
    from agent_lab.tracks.ontology_rag.graph.store import get_graph_store
    from agent_lab.tracks.ontology_rag.ontology.models import EntityType, RelationType
    from agent_lab.tracks.ontology_rag.ontology.schema import ALLOWED_TRIPLES

    snap = get_graph_store().snapshot()
    return {
        "entity_types": [e.value for e in EntityType],
        "relation_types": [r.value for r in RelationType],
        "allowed_triples": [
            {
                "source": s.value,
                "relation": rel.value,
                "target": t.value,
            }
            for s, rel, t in sorted(
                ALLOWED_TRIPLES,
                key=lambda x: (x[0].value, x[1].value, x[2].value),
            )
        ],
        "status": "seeded_graph",
        "note": "In-memory seeded property graph (Neo4j driver optional follow-up)",
        "node_count": snap["node_count"],
        "edge_count": snap["edge_count"],
    }


@router.get("/graph")
def get_graph(q: str | None = None, node_id: str | None = None) -> dict[str, Any]:
    from agent_lab.tracks.ontology_rag.graph.store import get_graph_store

    store = get_graph_store()
    if node_id:
        return {"mode": "neighbors", **store.neighbors(node_id, depth=1)}
    if q:
        return {"mode": "search", "query": q, "nodes": store.search(q)}
    snap = store.snapshot()
    return {"mode": "snapshot", **snap}


@router.post("/embedded/parse")
def parse_embedded_logs(body: dict[str, Any]) -> dict[str, Any]:
    from pathlib import Path

    from agent_lab.tracks.embedded_adas.diagnostics.engine import diagnose_events
    from agent_lab.tracks.embedded_adas.logs.parser import parse_log_text

    text = str(body.get("log_text") or "")
    use_fixture = bool(body.get("use_fixture"))
    if use_fixture and not text.strip():
        # runs.py → routes → api → agent_lab → src → backend → apps → repo root
        fixture = (
            Path(__file__).resolve().parents[6]
            / "fixtures"
            / "embedded_adas"
            / "sample_perception_timeout.log"
        )
        text = fixture.read_text(encoding="utf-8") if fixture.is_file() else ""
    events, malformed = parse_log_text(text)
    report = diagnose_events(events)
    return {
        "event_count": len(events),
        "malformed": malformed,
        "events": [e.model_dump() for e in events],
        "report": report.model_dump(),
    }
