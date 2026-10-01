"""Per-skill tool permission policies."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillPolicy:
    name: str
    description: str
    use_when: str
    allowed_tools: frozenset[str]


SKILL_POLICIES: dict[str, SkillPolicy] = {
    "enterprise-search": SkillPolicy(
        name="enterprise-search",
        description="Search and read synthetic enterprise documents with citations.",
        use_when="policy, notice, or HR/security document questions",
        allowed_tools=frozenset({"search_documents", "read_document", "query_structured_data"}),
    ),
    "incident-triage": SkillPolicy(
        name="incident-triage",
        description="Lightweight incident framing (stub skill metadata).",
        use_when="ops incident / outage style questions",
        allowed_tools=frozenset({"search_documents", "read_document"}),
    ),
    "ontology-graph": SkillPolicy(
        name="ontology-graph",
        description="Search the seeded property graph and traverse neighbors.",
        use_when="Track A ontology / GraphRAG questions",
        allowed_tools=frozenset({"graph_search", "graph_neighbors"}),
    ),
    "embedded-diagnostics": SkillPolicy(
        name="embedded-diagnostics",
        description="Parse synthetic ADAS logs and look up known issues.",
        use_when="Track B embedded / ADAS diagnostic questions",
        allowed_tools=frozenset({"parse_logs", "lookup_known_issue"}),
    ),
}


def policy_for(skill: str | None) -> SkillPolicy:
    if skill and skill in SKILL_POLICIES:
        return SKILL_POLICIES[skill]
    return SKILL_POLICIES["enterprise-search"]
