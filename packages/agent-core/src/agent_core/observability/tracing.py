"""Fail-open observability helpers."""

from __future__ import annotations

from agent_lab.config import get_settings


def tracing_status() -> dict[str, bool | str]:
    s = get_settings()
    return {
        "otel_enabled": bool(s.otel_tracing_enabled) and not s.otel_sdk_disabled,
        "langsmith_enabled": bool(s.langsmith_tracing) and bool(s.langsmith_api_key),
        "langsmith_project": s.langsmith_project,
        "note": "fail-open: telemetry must never break answers/scoring",
    }


def maybe_export_run_metadata(meta: dict) -> None:
    """Placeholder — never raises into the request path."""
    try:
        status = tracing_status()
        if not status["otel_enabled"] and not status["langsmith_enabled"]:
            return
        # Future: OTel span / LangSmith run export
        _ = meta
    except Exception:
        return
