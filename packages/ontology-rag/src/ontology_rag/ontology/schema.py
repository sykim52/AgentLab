"""Allowed (source_type, relation, target_type) triples for ontology validation."""

from __future__ import annotations

from agent_lab.tracks.ontology_rag.ontology.models import EntityType, RelationType

# Minimal enterprise + automotive matrix — extend as fixtures grow.
ALLOWED_TRIPLES: frozenset[tuple[EntityType, RelationType, EntityType]] = frozenset(
    {
        (EntityType.DEPARTMENT, RelationType.OWNS, EntityType.SYSTEM),
        (EntityType.SYSTEM, RelationType.OWNED_BY, EntityType.DEPARTMENT),
        (EntityType.SYSTEM, RelationType.USES, EntityType.TECHNOLOGY),
        (EntityType.SYSTEM, RelationType.DEPENDS_ON, EntityType.SERVICE),
        (EntityType.INCIDENT, RelationType.AFFECTS, EntityType.SYSTEM),
        (EntityType.INCIDENT, RelationType.RESOLVED_BY, EntityType.TECHNOLOGY),
        (EntityType.DOCUMENT, RelationType.HAS_CHUNK, EntityType.CHUNK),
        (EntityType.CHUNK, RelationType.MENTIONS, EntityType.TECHNOLOGY),
        (EntityType.CHUNK, RelationType.MENTIONS, EntityType.SYSTEM),
        (EntityType.POLICY, RelationType.GOVERNS, EntityType.SYSTEM),
        (EntityType.PERSON, RelationType.BELONGS_TO, EntityType.DEPARTMENT),
        (EntityType.PERSON, RelationType.HAS_ROLE, EntityType.ROLE),
        (EntityType.LOG_EVENT, RelationType.EMITS, EntityType.FAILURE_CODE),
        (EntityType.FAILURE_CODE, RelationType.AFFECTS, EntityType.SOFTWARE_COMPONENT),
        (EntityType.SOFTWARE_COMPONENT, RelationType.RUNS_ON, EntityType.ECU),
        (EntityType.SOFTWARE_COMPONENT, RelationType.TESTED_BY, EntityType.TEST_CASE),
        (EntityType.VEHICLE, RelationType.CONTAINS, EntityType.ECU),
        (EntityType.ECU, RelationType.RUNS, EntityType.SOFTWARE_COMPONENT),
    }
)


def is_allowed_triple(
    source_type: EntityType,
    relation: RelationType,
    target_type: EntityType,
) -> bool:
    return (source_type, relation, target_type) in ALLOWED_TRIPLES
