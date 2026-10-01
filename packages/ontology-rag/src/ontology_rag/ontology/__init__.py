"""Track A ontology package — schema artifacts (not prompt-only text)."""

from agent_lab.tracks.ontology_rag.ontology.models import (
    EntityType,
    GraphEntity,
    GraphRelation,
    RelationType,
)
from agent_lab.tracks.ontology_rag.ontology.schema import is_allowed_triple
from agent_lab.tracks.ontology_rag.ontology.validation import validate_relation

__all__ = [
    "EntityType",
    "RelationType",
    "GraphEntity",
    "GraphRelation",
    "is_allowed_triple",
    "validate_relation",
]
