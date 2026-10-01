"""Ontology validation before KG persistence."""

from __future__ import annotations

from pydantic import BaseModel, Field

from agent_lab.tracks.ontology_rag.ontology.models import GraphEntity, GraphRelation
from agent_lab.tracks.ontology_rag.ontology.schema import is_allowed_triple


class ValidationIssue(BaseModel):
    code: str
    message: str
    subject_id: str | None = None


class GraphBuildReport(BaseModel):
    extracted_entities: int = 0
    accepted_entities: int = 0
    merged_entities: int = 0
    rejected_entities: int = 0
    extracted_relations: int = 0
    accepted_relations: int = 0
    rejected_relations: int = 0
    validation_errors: list[ValidationIssue] = Field(default_factory=list)


def validate_entity(entity: GraphEntity) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not entity.canonical_id.strip():
        issues.append(
            ValidationIssue(
                code="missing_canonical_id",
                message="Entity canonical_id is required",
                subject_id=entity.canonical_id or None,
            )
        )
    if entity.valid_from and entity.valid_to and entity.valid_to < entity.valid_from:
        issues.append(
            ValidationIssue(
                code="invalid_temporal_range",
                message="valid_to precedes valid_from",
                subject_id=entity.canonical_id,
            )
        )
    return issues


def validate_relation(relation: GraphRelation) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if not is_allowed_triple(
        relation.source_type, relation.relation_type, relation.target_type
    ):
        issues.append(
            ValidationIssue(
                code="illegal_triple",
                message=(
                    f"{relation.source_type.value} -[{relation.relation_type.value}]-> "
                    f"{relation.target_type.value} is not in ontology schema"
                ),
                subject_id=relation.canonical_id,
            )
        )
    if not relation.source_document_id and not relation.source_chunk_id:
        issues.append(
            ValidationIssue(
                code="missing_provenance",
                message="Relation requires source_document_id or source_chunk_id",
                subject_id=relation.canonical_id,
            )
        )
    if relation.valid_from and relation.valid_to and relation.valid_to < relation.valid_from:
        issues.append(
            ValidationIssue(
                code="invalid_temporal_range",
                message="valid_to precedes valid_from",
                subject_id=relation.canonical_id,
            )
        )
    return issues
