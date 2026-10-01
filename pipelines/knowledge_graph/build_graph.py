"""Offline KG build entrypoint — Planned: fixture → validate → Neo4j upsert."""

from __future__ import annotations

import json


def main() -> None:
    print(
        json.dumps(
            {
                "status": "planned",
                "steps": [
                    "extract_entities",
                    "extract_relations",
                    "validate_ontology",
                    "resolve_entities",
                    "build_graph (Neo4j)",
                ],
                "note": "Not invoked on the online request path (apps/backend).",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
