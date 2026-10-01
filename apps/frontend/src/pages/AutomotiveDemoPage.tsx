import { FormEvent, useState } from "react";
import { parseEmbeddedLogs } from "../api/runs";
import { useAgentRun } from "../hooks/useAgentRun";

const SAMPLE_HINT =
  "Diagnose the perception timeout in the sample ADAS log (software-only SIL).";

export function AutomotiveDemoPage() {
  const { messages, timeline, evidence, status, runId, submit } = useAgentRun();
  const [text, setText] = useState(SAMPLE_HINT);
  const [logText, setLogText] = useState("");
  const [parseResult, setParseResult] = useState<string>("");
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    await submit(text.trim(), "embedded");
  }

  async function onParseFixture() {
    setBusy(true);
    try {
      const data = await parseEmbeddedLogs({ use_fixture: true });
      setParseResult(
        `Parsed ${data.event_count} events (malformed=${data.malformed}). ` +
          `Hypotheses: ${data.report.hypotheses.length}. ` +
          `Suspected: ${(data.report.suspected_components || []).join(", ") || "n/a"}`,
      );
      setLogText(
        (data.events || [])
          .map(
            (e) =>
              `${e.timestamp}|${e.component}|${e.severity}|${e.code}|${e.message}`,
          )
          .join("\n"),
      );
    } catch (err) {
      setParseResult(String(err));
    } finally {
      setBusy(false);
    }
  }

  async function onParseCustom() {
    if (!logText.trim()) return;
    setBusy(true);
    try {
      const data = await parseEmbeddedLogs({ log_text: logText });
      setParseResult(
        `Parsed ${data.event_count} events. Confidence=${data.report.confidence}. ` +
          `Next: ${(data.report.next_actions || []).slice(0, 2).join("; ") || "n/a"}`,
      );
    } catch (err) {
      setParseResult(String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid-2">
      <section className="panel">
        <h2>Embedded / ADAS Diagnostics</h2>
        <p className="badge">Synthetic demonstration data — Actual HIL: Not implemented</p>
        <p className="muted">
          Run: {runId ?? "—"} · status: <span className="badge">{status}</span>
        </p>
        <div className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`bubble ${m.role}`}>
              <strong>{m.role}</strong>
              <div>{m.text}</div>
            </div>
          ))}
        </div>
        <form className="composer" onSubmit={onSubmit}>
          <input value={text} onChange={(e) => setText(e.target.value)} />
          <button className="primary" type="submit">
            Triage
          </button>
        </form>
        <div className="sources">
          <h3>Evidence</h3>
          {evidence.length === 0 && <p className="muted">No citations yet.</p>}
          {evidence.map((ev, i) => (
            <div key={i} className="bubble">
              [{i + 1}] {JSON.stringify(ev)}
            </div>
          ))}
        </div>
      </section>
      <aside className="panel">
        <h2>Log parser</h2>
        <p className="muted">Wire format: ISO8601|COMPONENT|SEVERITY|CODE|message</p>
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
          <button type="button" className="primary" disabled={busy} onClick={onParseFixture}>
            Load sample fixture
          </button>
          <button type="button" disabled={busy || !logText.trim()} onClick={onParseCustom}>
            Parse textarea
          </button>
        </div>
        <textarea
          value={logText}
          onChange={(e) => setLogText(e.target.value)}
          rows={10}
          style={{ width: "100%", fontFamily: "ui-monospace, monospace", fontSize: "0.8rem" }}
          placeholder="Paste synthetic logs here…"
        />
        {parseResult && <p className="muted">{parseResult}</p>}
        <h3>Agent activity</h3>
        <ul className="timeline">
          {timeline.length === 0 && <li className="muted">Waiting for events…</li>}
          {timeline.map((ev) => (
            <li key={ev.event_id}>
              <strong>{ev.type}</strong>
              <div className="muted">seq {ev.sequence}</div>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
