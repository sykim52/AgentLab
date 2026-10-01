"""In-memory SSE event broker for agent runs (local demos)."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator
from typing import Any

from agent_lab.api.streaming.events import RunEvent, RunEventType, RunStatus


class RunBroker:
    """Stores run status + ordered events; fans out to SSE subscribers."""

    def __init__(self) -> None:
        self._events: dict[str, list[RunEvent]] = defaultdict(list)
        self._status: dict[str, RunStatus] = {}
        self._queues: dict[str, list[asyncio.Queue[RunEvent | None]]] = defaultdict(list)
        self._results: dict[str, dict[str, Any]] = {}
        self._seq: dict[str, int] = defaultdict(int)
        self._lock = asyncio.Lock()

    async def create(self, run_id: str) -> None:
        async with self._lock:
            self._status[run_id] = RunStatus.QUEUED
            self._events[run_id] = []
            self._seq[run_id] = 0

    async def set_status(self, run_id: str, status: RunStatus) -> None:
        async with self._lock:
            self._status[run_id] = status

    def get_status(self, run_id: str) -> RunStatus | None:
        return self._status.get(run_id)

    def get_result(self, run_id: str) -> dict[str, Any] | None:
        return self._results.get(run_id)

    async def publish(
        self,
        run_id: str,
        event_type: RunEventType,
        data: dict[str, Any] | None = None,
    ) -> RunEvent:
        async with self._lock:
            self._seq[run_id] += 1
            event = RunEvent(
                run_id=run_id,
                type=event_type,
                sequence=self._seq[run_id],
                data=data or {},
            )
            self._events[run_id].append(event)
            queues = list(self._queues.get(run_id, []))
        for q in queues:
            await q.put(event)
        return event

    async def complete(self, run_id: str, result: dict[str, Any], *, failed: bool = False) -> None:
        self._results[run_id] = result
        await self.set_status(
            run_id, RunStatus.FAILED if failed else RunStatus.COMPLETED
        )
        await self.publish(
            run_id,
            RunEventType.RUN_FAILED if failed else RunEventType.RUN_COMPLETED,
            {
                "outcome": result.get("outcome"),
                "final_answer": result.get("final_answer"),
                "failure_reason": result.get("failure_reason"),
            },
        )
        async with self._lock:
            queues = list(self._queues.get(run_id, []))
            self._queues[run_id] = []
        for q in queues:
            await q.put(None)

    async def subscribe(self, run_id: str, *, after_sequence: int = 0) -> AsyncIterator[RunEvent]:
        q: asyncio.Queue[RunEvent | None] = asyncio.Queue()
        async with self._lock:
            history = [e for e in self._events.get(run_id, []) if e.sequence > after_sequence]
            self._queues[run_id].append(q)
            status = self._status.get(run_id)
        for e in history:
            yield e
        if status in {RunStatus.COMPLETED, RunStatus.FAILED, RunStatus.CANCELLED}:
            return
        while True:
            item = await q.get()
            if item is None:
                break
            yield item


broker = RunBroker()
