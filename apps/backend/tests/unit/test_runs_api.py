from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from agent_lab.api.main import app


@pytest.mark.asyncio
async def test_create_run_and_sse_completes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/api/v1/runs",
            json={"message": "What is the PTO policy summary?", "application": "enterprise"},
        )
        assert resp.status_code == 202
        body = resp.json()
        run_id = body["run_id"]
        assert body["events_url"].endswith(f"/runs/{run_id}/events")

        # Poll get_run until completed (SSE in ASGI test client is awkward for long streams)
        for _ in range(50):
            st = await client.get(f"/api/v1/runs/{run_id}")
            assert st.status_code == 200
            payload = st.json()
            if payload["status"] in {"completed", "failed"}:
                break
            import asyncio

            await asyncio.sleep(0.05)
        assert payload["status"] == "completed"
        assert payload["result"]["outcome"] in {"ok", "denied"}
        assert payload["result"].get("final_answer")


@pytest.mark.asyncio
async def test_ontology_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/ontology")
        assert resp.status_code == 200
        data = resp.json()
        assert "Department" in data["entity_types"]
        assert "AFFECTS" in data["relation_types"]
        assert data["status"] == "seeded_graph"
        assert data["node_count"] > 0
        assert any(t["relation"] == "AFFECTS" for t in data["allowed_triples"])


@pytest.mark.asyncio
async def test_graph_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/graph")
        assert resp.status_code == 200
        data = resp.json()
        assert data["mode"] == "snapshot"
        assert data["node_count"] > 0

        search = await client.get("/api/v1/graph", params={"q": "LangGraph"})
        assert search.status_code == 200
        assert search.json()["nodes"]


@pytest.mark.asyncio
async def test_embedded_parse_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/api/v1/embedded/parse", json={"use_fixture": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data["event_count"] >= 3
        assert data["report"]["hypotheses"]
