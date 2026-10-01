# AgentLab

Laboratory for **agentic AI systems** and applied ML experiments.

Two independent demos share one core (LangGraph harness, model registry, tool envelopes, guardrails, eval hooks, FastAPI, React):

| Track | What it demos | UI |
|-------|----------------|-----|
| Ontology agent | Ontology schema → graph tools → agent answers | `/ontology` |
| Embedded diagnostics | C++/Python log parse → diagnostic agent (software-only) | `/embedded` |

Not a production product. The embedded track is a **software simulation** only — no hardware-in-the-loop, no production vehicle claims.

## Quick start

```bash
git clone https://github.com/sykim52/AgentLab.git
cd AgentLab

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q

# API
uvicorn agent_lab.api.main:app --reload --host 127.0.0.1 --port 8080

# Frontend (separate terminal)
cd apps/frontend && npm install && npm run dev
```

Optional C++ log parser (Track B):

```bash
cmake -S embedded/cpp -B embedded/cpp/build
cmake --build embedded/cpp/build
ctest --test-dir embedded/cpp/build --output-on-failure
```

Copy `.env.example` to `.env` for local flags (tracing off by default). Never commit `.env`.

## Layout

```text
apps/backend/              FastAPI + SSE run API
apps/frontend/             React / Vite demos
packages/agent-core/       Harness, registry, guardrails, eval
packages/ontology-rag/     Ontology + graph retrieval (Track A)
packages/embedded-adas/    Diagnostics domain + log bridge (Track B)
embedded/cpp/              C++17 LogParser
pipelines/                 Offline builders (e.g. knowledge graph)
training/                  Open-model configs + LoRA/QLoRA entrypoints
evals/                     Smoke / regression fixtures
infra/                     Local compose stubs
```

## Training note

Configs under `training/` support a simple lifecycle: benchmark a few open models → pick one → LoRA/QLoRA → register adapter for demos. **Weights and adapters are not committed.**

## Claim boundaries

**In scope:** synthetic data demos · software-only diagnostic pipelines · SIL-style scenarios · local agent experiments.

**Out of scope:** production ADAS · HIL racks · OEM ECU deployment · proprietary third-party IP.

## License

MIT — see `LICENSE` when present; otherwise treat source as MIT-licensed.
