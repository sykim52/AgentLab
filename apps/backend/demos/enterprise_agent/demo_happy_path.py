#!/usr/bin/env python3
"""Enterprise happy-path demo (synthetic fixtures — not production search)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # agent-lab-dev
sys.path.insert(0, str(ROOT / "apps" / "backend" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "agent-core" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "ontology-rag" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "embedded-adas" / "src"))

from agent_lab.core.evaluation.scorecard import score_run  # noqa: E402
from agent_lab.core.harness.graph import run_harness  # noqa: E402


def main() -> int:
    query = "What is the PTO policy summary?"
    result = run_harness(query, app="enterprise")
    card = score_run(
        case_id="enterprise-pto-happy",
        result=result,
        expect_outcome="ok",
        expect_tool="search_documents",
    )
    print("=== agent-lab enterprise demo ===")
    print(f"outcome: {result.get('outcome')}")
    print(f"skill:   {result.get('selected_skill')}")
    print(f"plan:    {result.get('plan')}")
    print(f"tools:   {[c.get('name') for c in (result.get('tool_calls') or [])]}")
    print(f"answer:\n{result.get('final_answer')}\n")
    print("scorecard:", json.dumps(card.to_dict(), indent=2))
    return 0 if card.task_success and card.tool_correct else 1


if __name__ == "__main__":
    raise SystemExit(main())
