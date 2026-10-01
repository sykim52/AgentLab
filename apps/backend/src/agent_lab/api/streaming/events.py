"""Canonical SSE / run event contracts (OpenAPI source of truth)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RunEventType(StrEnum):
    RUN_STARTED = "run.started"
    RUN_COMPLETED = "run.completed"
    RUN_FAILED = "run.failed"
    RUN_CANCELLED = "run.cancelled"
    NODE_STARTED = "node.started"
    NODE_COMPLETED = "node.completed"
    NODE_FAILED = "node.failed"
    PLAN_CREATED = "plan.created"
    SKILL_SELECTED = "skill.selected"
    AGENT_SELECTED = "agent.selected"
    AGENT_DELEGATED = "agent.delegated"
    TOOL_STARTED = "tool.started"
    TOOL_COMPLETED = "tool.completed"
    TOOL_FAILED = "tool.failed"
    EVIDENCE_ADDED = "evidence.added"
    SECURITY_FLAGGED = "security.flagged"
    APPROVAL_REQUIRED = "approval.required"
    APPROVAL_RESOLVED = "approval.resolved"
    ANSWER_DELTA = "answer.delta"
    # Graph / ontology (P1)
    ONTOLOGY_LOADED = "ontology.loaded"
    GRAPH_SEARCH_STARTED = "graph.search.started"
    GRAPH_SEARCH_COMPLETED = "graph.search.completed"
    GRAPH_TRAVERSAL_STARTED = "graph.traversal.started"
    GRAPH_TRAVERSAL_COMPLETED = "graph.traversal.completed"
    GRAPH_QUERY_GENERATED = "graph.query.generated"
    GRAPH_QUERY_EXECUTED = "graph.query.executed"
    GRAPH_EVIDENCE_ADDED = "graph.evidence.added"


class RunEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid4()))
    run_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    type: RunEventType
    sequence: int
    data: dict[str, Any] = Field(default_factory=dict)


class RunStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CreateRunRequest(BaseModel):
    session_id: str | None = None
    application: str = "ontology"  # ontology | embedded | enterprise | automotive
    message: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CreateRunResponse(BaseModel):
    run_id: str
    session_id: str
    status: RunStatus
    events_url: str


class RunActionRequest(BaseModel):
    action: str  # approve | reject
    checkpoint_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
