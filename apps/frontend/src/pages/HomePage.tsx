import { Link } from "react-router-dom";

export function HomePage() {
  return (
    <div className="panel">
      <h1>agent-lab</h1>
      <p className="muted">
        Full-stack AI engineering lab: <strong>two independent E2E tracks</strong> on one Common AI
        Core (LangGraph). Synthetic / software-only — not production ADAS or HIL.
      </p>
      <ul>
        <li>
          <Link to="/ontology">Ontology Agent</Link> (Track A) — ontology → KG → GraphRAG → agent →
          Graph Explorer
        </li>
        <li>
          <Link to="/embedded">Embedded / ADAS AI</Link> (Track B) — C++ logs → agent triage →
          SIL-style validation
        </li>
        <li>
          <Link to="/evaluations">Evaluation</Link>
        </li>
        <li>
          <Link to="/benchmarks">Benchmarks</Link> — Llama / Mistral / Qwen · Python vs C++ (measured
          only)
        </li>
      </ul>
    </div>
  );
}
