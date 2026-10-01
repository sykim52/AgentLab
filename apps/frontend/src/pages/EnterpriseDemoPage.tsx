import { FormEvent, useState } from "react";
import { useAgentRun } from "../hooks/useAgentRun";

export function EnterpriseDemoPage() {
  const { messages, timeline, evidence, status, runId, submit } = useAgentRun();
  const [text, setText] = useState("What is the PTO policy summary?");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    await submit(text.trim(), "enterprise");
  }

  return (
    <div className="grid-2">
      <section className="panel">
        <h2>Enterprise Agent</h2>
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
            Send
          </button>
        </form>
        <div className="sources">
          <h3>Sources</h3>
          {evidence.length === 0 && <p className="muted">No citations yet.</p>}
          {evidence.map((ev, i) => (
            <div key={i} className="bubble">
              [{i + 1}] {JSON.stringify(ev)}
            </div>
          ))}
        </div>
      </section>
      <aside className="panel">
        <h2>Agent Activity</h2>
        <ul className="timeline">
          {timeline.length === 0 && <li className="muted">Waiting for events…</li>}
          {timeline.map((ev) => (
            <li key={ev.event_id}>
              <strong>{ev.type}</strong>
              <div className="muted">seq {ev.sequence}</div>
              <pre style={{ margin: 0, whiteSpace: "pre-wrap", fontSize: "0.8rem" }}>
                {JSON.stringify(ev.data, null, 0)}
              </pre>
            </li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
