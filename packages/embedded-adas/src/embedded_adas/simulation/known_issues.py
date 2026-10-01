"""Synthetic known-issue catalogue for Track B diagnostics (software-only)."""

from __future__ import annotations

from typing import Any

KNOWN_ISSUES: dict[str, dict[str, Any]] = {
    "PERCEPTION_TIMEOUT": {
        "code": "PERCEPTION_TIMEOUT",
        "title": "Perception frame deadline miss",
        "suspected_components": ["Perception Stack", "Front Camera", "Front LiDAR"],
        "summary": (
            "Perception module missed the frame deadline. Often co-occurs with "
            "camera-LiDAR sync skew in synthetic SIL scenarios."
        ),
        "recommended_tests": [
            "SIL-Perception-Timeout-01",
            "Replay sensor bag with injected 20ms skew",
        ],
        "next_actions": [
            "Inspect SENSOR_SYNC_LOST proximity in the same window",
            "Check perception thread budget vs frame rate",
        ],
        "claim_boundary": "software-only embedded/ADAS simulation — not production HIL",
    },
    "SENSOR_SYNC_LOST": {
        "code": "SENSOR_SYNC_LOST",
        "title": "Camera-LiDAR temporal skew",
        "suspected_components": ["Front Camera", "Front LiDAR", "Perception Stack"],
        "summary": (
            "Sensor fusion reported camera-LiDAR skew beyond the sync budget. "
            "May precipitate perception timeouts downstream."
        ),
        "recommended_tests": [
            "Sensor sync unit check",
            "SIL replay with controlled clock offset",
        ],
        "next_actions": [
            "Correlate with PERCEPTION_TIMEOUT events",
            "Verify timestamp domains on camera vs LiDAR feeds",
        ],
        "claim_boundary": "software-only embedded/ADAS simulation — not production HIL",
    },
}


def lookup_known_issue(code: str) -> dict[str, Any] | None:
    key = (code or "").strip().upper()
    if not key:
        return None
    return KNOWN_ISSUES.get(key)
