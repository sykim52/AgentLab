"""Guardrails: injection heuristics + tool allowlist helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.I),
    re.compile(r"disregard\s+(your\s+)?system\s+prompt", re.I),
    re.compile(r"exfiltrate", re.I),
    re.compile(r"call\s+admin[_ ]?tools?", re.I),
    re.compile(r"you\s+must\s+override", re.I),
]


@dataclass(frozen=True)
class GuardResult:
    blocked: bool
    flags: list[str]
    reason: str | None = None


def scan_text_for_injection(text: str) -> GuardResult:
    flags: list[str] = []
    for pat in INJECTION_PATTERNS:
        if pat.search(text or ""):
            flags.append(f"injection:{pat.pattern}")
    if flags:
        return GuardResult(blocked=True, flags=flags, reason="prompt_injection_heuristic")
    return GuardResult(blocked=False, flags=[])


def scan_retrieved_for_injection(chunks: list[str]) -> GuardResult:
    """Indirect injection via retrieved documents."""
    flags: list[str] = []
    for i, chunk in enumerate(chunks):
        r = scan_text_for_injection(chunk)
        if r.blocked:
            flags.extend(f"retrieved[{i}]:{f}" for f in r.flags)
    if flags:
        return GuardResult(
            blocked=True,
            flags=flags,
            reason="indirect_injection_in_retrieved_content",
        )
    return GuardResult(blocked=False, flags=[])
