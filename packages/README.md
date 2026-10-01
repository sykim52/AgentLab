# Shared packages

- `agent-core` — LangGraph harness, ModelRegistry, guardrails, eval, observability  
- `ontology-rag` — ontology schema + graph retrieval (Track A)  
- `embedded-adas` — diagnostics domain + log bridge (Track B)  

Installed via root `pyproject.toml` `pythonpath` / editable install.  
`apps/backend/src/agent_lab/core` and `tracks/*` are **compat symlinks** into these packages.
