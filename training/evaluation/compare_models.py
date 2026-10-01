"""Compare Llama / Mistral / Qwen base configs — Stage-1 selection helper (Planned: real evals)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = {
    "llama": ROOT / "configs" / "llama" / "base.yaml",
    "mistral": ROOT / "configs" / "mistral" / "base.yaml",
    "qwen": ROOT / "configs" / "qwen" / "base.yaml",
}


def list_candidates() -> dict[str, str]:
    return {k: str(v) for k, v in CONFIGS.items() if v.exists()}


def main() -> None:
    candidates = list_candidates()
    report = {
        "stage": "base_benchmark_planned",
        "rule": "Benchmark all three families; fine-tune only the selected one.",
        "candidates": candidates,
        "next": [
            "Fill docs/benchmarks/models/ with measured metrics",
            "Write ADR selecting one family",
            "Enable finetuning in that family's YAML and run train_qlora.py",
            "Register adapter path in ModelRegistry for apps/backend demo",
        ],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
