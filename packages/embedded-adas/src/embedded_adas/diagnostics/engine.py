"""Build a DiagnosticReport from parsed log events + known issues."""

from __future__ import annotations

from agent_lab.tracks.embedded_adas.domain.models import (
    DiagnosticHypothesis,
    DiagnosticReport,
    HypothesisStatus,
    LogEvent,
)
from agent_lab.tracks.embedded_adas.simulation.known_issues import lookup_known_issue


def diagnose_events(events: list[LogEvent]) -> DiagnosticReport:
    codes = [e.code for e in events if e.code]
    unique_codes = list(dict.fromkeys(codes))
    hypotheses: list[DiagnosticHypothesis] = []
    suspected: list[str] = []
    recommended: list[str] = []
    next_actions: list[str] = []
    evidence: list[dict] = []

    for i, event in enumerate(events):
        evidence.append(
            {
                "id": f"log-{i}",
                "timestamp": event.timestamp,
                "component": event.component,
                "severity": event.severity.value,
                "code": event.code,
                "message": event.message,
            }
        )

    for code in unique_codes:
        issue = lookup_known_issue(code)
        if not issue:
            hypotheses.append(
                DiagnosticHypothesis(
                    id=f"hyp-unknown-{code or 'empty'}",
                    summary=f"Unrecognized code {code or '(empty)'} — no catalogue match",
                    suspected_components=[],
                    supporting_logs=[code],
                    confidence=0.2,
                    validation_status=HypothesisStatus.UNSUPPORTED,
                )
            )
            continue
        for c in issue["suspected_components"]:
            if c not in suspected:
                suspected.append(c)
        for t in issue["recommended_tests"]:
            if t not in recommended:
                recommended.append(t)
        for a in issue["next_actions"]:
            if a not in next_actions:
                next_actions.append(a)
        supporting = [e.message for e in events if e.code == code][:3]
        hypotheses.append(
            DiagnosticHypothesis(
                id=f"hyp-{code.lower()}",
                summary=issue["summary"],
                suspected_components=list(issue["suspected_components"]),
                evidence_ids=[f"log-{i}" for i, e in enumerate(events) if e.code == code],
                supporting_logs=supporting,
                confidence=0.78 if len(supporting) > 1 else 0.62,
                validation_status=HypothesisStatus.PARTIALLY_SUPPORTED,
            )
        )

    conf = 0.0
    if hypotheses:
        conf = sum(h.confidence for h in hypotheses) / len(hypotheses)

    uncertainties: list[str] = []
    if not unique_codes:
        uncertainties.append("No failure codes found in parsed events")
    if any(h.validation_status == HypothesisStatus.UNSUPPORTED for h in hypotheses):
        uncertainties.append("Some codes lack catalogue entries")

    return DiagnosticReport(
        suspected_components=suspected,
        hypotheses=hypotheses,
        evidence=evidence,
        confidence=round(conf, 3),
        recommended_tests=recommended,
        uncertainties=uncertainties,
        next_actions=next_actions,
    )
