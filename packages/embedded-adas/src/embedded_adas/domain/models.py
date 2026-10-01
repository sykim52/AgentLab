"""Track B shared domain contracts (Python side)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"


class LogEvent(BaseModel):
    timestamp: str
    component: str
    severity: Severity
    code: str = ""
    message: str = ""


class FailureCode(BaseModel):
    code: str
    description: str = ""
    component: str | None = None


class HypothesisStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class DiagnosticHypothesis(BaseModel):
    id: str
    summary: str
    suspected_components: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)
    supporting_logs: list[str] = Field(default_factory=list)
    conflicting_evidence: list[str] = Field(default_factory=list)
    confidence: float = 0.0
    validation_status: HypothesisStatus = HypothesisStatus.UNSUPPORTED


class DiagnosticReport(BaseModel):
    suspected_components: list[str] = Field(default_factory=list)
    hypotheses: list[DiagnosticHypothesis] = Field(default_factory=list)
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = 0.0
    recommended_tests: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    claim_boundary: str = (
        "software-only embedded/ADAS simulation — not production HIL/OEM experience"
    )
