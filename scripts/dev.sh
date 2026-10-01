#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
source .venv/bin/activate
uvicorn agent_lab.api.main:app --reload --host 127.0.0.1 --port 8080
