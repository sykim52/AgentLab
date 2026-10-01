"""FastAPI entry — sync /v1/run (compat) + async /api/v1/runs + SSE."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent_lab import __version__
from agent_lab.api.routes.runs import router as runs_router
from agent_lab.core.harness.graph import run_harness
from agent_lab.core.observability.tracing import maybe_export_run_metadata, tracing_status

app = FastAPI(
    title="agent-lab",
    version=__version__,
    description="LangGraph agent harness demo API (synthetic fixtures).",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(runs_router)


class RunRequest(BaseModel):
    message: str = Field(..., min_length=1)
    app: Literal["enterprise", "automotive", "ontology", "embedded"] = "ontology"
    thread_id: str | None = None


class RunResponse(BaseModel):
    request_id: str
    thread_id: str
    outcome: str | None
    final_answer: str | None
    selected_skill: str | None
    plan: list[str]
    tool_calls: list[dict[str, Any]]
    evidence_count: int
    security_flags: list[str]
    failure_reason: str | None
    tracing: dict[str, Any]


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "version": __version__, "tracing": tracing_status()}


@app.post("/v1/run", response_model=RunResponse)
def run_agent(body: RunRequest) -> RunResponse:
    request_id = str(uuid.uuid4())
    thread_id = body.thread_id or request_id
    result = run_harness(
        body.message,
        app=body.app,
        request_id=request_id,
        thread_id=thread_id,
    )
    maybe_export_run_metadata(
        {
            "request_id": request_id,
            "outcome": result.get("outcome"),
            "app": body.app,
        }
    )
    return RunResponse(
        request_id=request_id,
        thread_id=thread_id,
        outcome=result.get("outcome"),
        final_answer=result.get("final_answer"),
        selected_skill=result.get("selected_skill"),
        plan=list(result.get("plan") or []),
        tool_calls=list(result.get("tool_calls") or []),
        evidence_count=len(result.get("evidence") or []),
        security_flags=list(result.get("security_flags") or []),
        failure_reason=result.get("failure_reason"),
        tracing=tracing_status(),
    )


def run() -> None:
    import uvicorn

    from agent_lab.config import get_settings

    s = get_settings()
    uvicorn.run(
        "agent_lab.api.main:app",
        host=s.agent_lab_api_host,
        port=s.agent_lab_api_port,
        reload=False,
    )
