import { FormEvent, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchGraph, fetchOntology } from "../api/runs";
import { useAgentRun } from "../hooks/useAgentRun";

export function KnowledgePage() {
  const ontology = useQuery({ queryKey: ["ontology"], queryFn: fetchOntology });
  const graph = useQuery({ queryKey: ["graph"], queryFn: () => fetchGraph() });
  const { messages, timeline, evidence, status, runId, submit } = useAgentRun();
  const [text, setText] = useState("Which systems does the AI Platform depend on?");
  const [filter, setFilter] = useState("");

  const nodes = useMemo(() => {
    const all = graph.data?.nodes ?? [];
    const q = filter.trim().toLowerCase();
    if (!q) return all.slice(0, 40);
    return all
      .filter((n) => {
        const hay = `${n.id} ${n.name} ${(n.labels || []).join(" ")}`.toLowerCase();
        return hay.includes(q);
      })
      .slice(0, 40);
  }, [graph.data, filter]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    await submit(text.trim(), "ontology");
  }

  return (
    <div className="grid-2">
      <section className="panel">
        <h2>Ontology Agent</h2>
        <p className="muted">
          Schema + seeded in-memory KG · status:{" "}
          <span className="badge">{ontology.data?.status ?? "loading"}</span>
          {ontology.data && (
            <>
              {" "}
              · {ontology.data.node_count} nodes / {ontology.data.edge_count} edges
            </>
          )}
        </p>
        <p className="muted">
          Run: {runId ?? "—"} · agent: <span className="badge">{status}</span>
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
            Ask graph
          </button>
        </form>
        <div className="sources">
          <h3>Graph evidence</h3>
          {evidence.length === 0 && <p className="muted">No citations yet.</p>}
          {evidence.map((ev, i) => (
            <div key={i} className="bubble">
              [{i + 1}] {JSON.stringify(ev)}
            </div>
          ))}
        </div>
        <aside style={{ marginTop: "1rem" }}>
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
      </section>
      <aside className="panel">
        <h2>Graph Explorer</h2>
        <input
          placeholder="Filter nodes…"
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          style={{ width: "100%", marginBottom: "0.75rem" }}
        />
        {graph.isError && <p>Failed to load graph.</p>}
        <ul className="timeline">
          {nodes.map((n) => (
            <li key={n.id}>
              <strong>{n.name}</strong>
              <div className="muted">
                {n.id} · {(n.labels || []).join(", ")}
              </div>
            </li>
          ))}
        </ul>
        <h3>Sample allowed triples</h3>
        <ul className="timeline">
          {(ontology.data?.allowed_triples ?? []).slice(0, 8).map((t, i) => (
            <li key={i}>{`${t.source} -[ ${t.relation} ]-> ${t.target}`}</li>
          ))}
        </ul>
      </aside>
    </div>
  );
}
