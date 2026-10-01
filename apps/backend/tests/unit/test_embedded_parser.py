from __future__ import annotations

from agent_lab.tracks.embedded_adas.logs.parser import parse_log_text


def test_parse_sample_fixture():
    from pathlib import Path

    text = Path("fixtures/embedded_adas/sample_perception_timeout.log").read_text(
        encoding="utf-8"
    )
    events, malformed = parse_log_text(text)
    assert len(events) >= 3
    assert malformed >= 1
    assert any(e.code == "PERCEPTION_TIMEOUT" for e in events)
