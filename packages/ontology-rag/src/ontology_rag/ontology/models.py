"""Enterprise ontology types — LLM must not invent types outside this schema."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class EntityType(StrEnum):
    ORGANIZATION = "Organization"
    DEPARTMENT = "Department"
    PERSON = "Person"
    ROLE = "Role"
    SKILL = "Skill"
    DOCUMENT = "Document"
    POLICY = "Policy"
    SYSTEM = "System"
    SERVICE = "Service"
    INCIDENT = "Incident"
    PROJECT = "Project"
    TECHNOLOGY = "Technology"
    DATASET = "Dataset"
    CHUNK = "Chunk"
    # Automotive (same registry; domain-scoped in fixtures)
    VEHICLE = "Vehicle"
    ECU = "ECU"
    SOFTWARE_COMPONENT = "SoftwareComponent"
    SENSOR = "Sensor"
    MODEL = "Model"
    FAILURE_CODE = "FailureCode"
    TEST_CASE = "TestCase"
    LOG_EVENT = "LogEvent"


class RelationType(StrEnum):
    BELONGS_TO = "BELONGS_TO"
    HAS_ROLE = "HAS_ROLE"
    HAS_SKILL = "HAS_SKILL"
    OWNS = "OWNS"
    USES = "USES"
    DEPENDS_ON = "DEPENDS_ON"
    MENTIONS = "MENTIONS"
    GOVERNS = "GOVERNS"
    RELATED_TO = "RELATED_TO"
    AFFECTS = "AFFECTS"
    RESOLVED_BY = "RESOLVED_BY"
    PARTICIPATES_IN = "PARTICIPATES_IN"
    HAS_CHUNK = "HAS_CHUNK"
    CONTAINS = "CONTAINS"
    RUNS = "RUNS"
    EMITS = "EMITS"
    TRIGGERS = "TRIGGERS"
    TESTED_BY = "TESTED_BY"
    OWNED_BY = "OWNED_BY"
    RUNS_ON = "RUNS_ON"


class GraphEntity(BaseModel):
    canonical_id: str
    entity_type: EntityType
    name: str
    aliases: list[str] = Field(default_factory=list)
    description: str | None = None
    source_id: str | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    confidence: float = 1.0
    created_at: datetime | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    provenance_document_ids: list[str] = Field(default_factory=list)
    provenance_chunk_ids: list[str] = Field(default_factory=list)


class GraphRelation(BaseModel):
    canonical_id: str
    relation_type: RelationType
    source_id: str
    target_id: str
    source_type: EntityType
    target_type: EntityType
    confidence: float = 1.0
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source_document_id: str | None = None
    source_chunk_id: str | None = None
    extraction_run_id: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
