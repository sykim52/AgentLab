from __future__ import annotations

from fastapi.testclient import TestClient

from agent_lab.api.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_run_enterprise():
    r = client.post("/v1/run", json={"message": "PTO leave policy", "app": "enterprise"})
    assert r.status_code == 200
    body = r.json()
    assert body["outcome"] == "ok"
    assert body["final_answer"]
    assert body["tool_calls"]
