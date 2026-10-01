from __future__ import annotations

from agent_lab.tracks.ontology_rag.ontology.models import (
    EntityType,
    GraphEntity,
    GraphRelation,
    RelationType,
)
from agent_lab.tracks.ontology_rag.ontology.schema import is_allowed_triple
from agent_lab.tracks.ontology_rag.ontology.validation import validate_relation


def test_allowed_enterprise_triple():
    assert is_allowed_triple(
        EntityType.INCIDENT, RelationType.AFFECTS, EntityType.SYSTEM
    )
    assert is_allowed_triple(
        EntityType.SYSTEM, RelationType.USES, EntityType.TECHNOLOGY
    )


def test_rejects_illegal_triple():
    assert not is_allowed_triple(
        EntityType.DOCUMENT, RelationType.HAS_ROLE, EntityType.INCIDENT
    )


def test_validate_relation_requires_provenance_and_schema():
    bad = GraphRelation(
        canonical_id="r1",
        relation_type=RelationType.HAS_ROLE,
        source_id="doc-1",
        target_id="inc-1",
        source_type=EntityType.DOCUMENT,
        target_type=EntityType.INCIDENT,
    )
    issues = validate_relation(bad)
    codes = {i.code for i in issues}
    assert "illegal_triple" in codes
    assert "missing_provenance" in codes

    good = GraphRelation(
        canonical_id="r2",
        relation_type=RelationType.AFFECTS,
        source_id="inc-1",
        target_id="sys-1",
        source_type=EntityType.INCIDENT,
        target_type=EntityType.SYSTEM,
        source_document_id="doc-incident-note",
    )
    assert validate_relation(good) == []


def test_graph_entity_model():
    e = GraphEntity(
        canonical_id="sys-ai-platform",
        entity_type=EntityType.SYSTEM,
        name="AI Platform",
        aliases=["ai-platform"],
    )
    assert e.entity_type == EntityType.SYSTEM
