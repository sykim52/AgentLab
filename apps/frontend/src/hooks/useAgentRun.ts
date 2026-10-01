import { useCallback, useRef, useState } from "react";
import { createRun, RunEvent, subscribeRunEvents } from "../api/runs";

type Msg = { role: "user" | "assistant"; text: string };

export function useAgentRun() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [timeline, setTimeline] = useState<RunEvent[]>([]);
  const [evidence, setEvidence] = useState<Record<string, unknown>[]>([]);
  const [status, setStatus] = useState<string>("idle");
  const [runId, setRunId] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  const submit = useCallback(async (message: string, application = "enterprise") => {
    esRef.current?.close();
    setMessages((m) => [...m, { role: "user", text: message }]);
    setTimeline([]);
    setEvidence([]);
    setStatus("queued");
    const created = await createRun(message, application);
    setRunId(created.run_id);
    setStatus(created.status);

    const es = subscribeRunEvents(created.run_id, (event) => {
      setTimeline((t) => [...t, event]);
      if (event.type === "evidence.added") {
        setEvidence((e) => [...e, event.data]);
      }
      if (event.type === "answer.delta") {
        const text = String(event.data.text ?? "");
        setMessages((m) => {
          const last = m[m.length - 1];
          if (last?.role === "assistant") {
            return [...m.slice(0, -1), { role: "assistant", text }];
          }
          return [...m, { role: "assistant", text }];
        });
      }
      if (event.type === "run.completed" || event.type === "run.failed") {
        setStatus(event.type === "run.completed" ? "completed" : "failed");
        es.close();
      }
    });
    esRef.current = es;
  }, []);

  return { messages, timeline, evidence, status, runId, submit };
}
