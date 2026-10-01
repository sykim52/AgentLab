export type RunEvent = {
  event_id: string;
  run_id: string;
  timestamp: string;
  type: string;
  sequence: number;
  data: Record<string, unknown>;
};

export async function createRun(message: string, application = "enterprise") {
  const res = await fetch("/api/v1/runs", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message, application }),
  });
  if (!res.ok) {
    throw new Error(`createRun failed: ${res.status}`);
  }
  return res.json() as Promise<{
    run_id: string;
    session_id: string;
    status: string;
    events_url: string;
  }>;
}

export function subscribeRunEvents(
  runId: string,
  onEvent: (event: RunEvent) => void,
  onError?: (err: Event) => void,
): EventSource {
  const es = new EventSource(`/api/v1/runs/${runId}/events`);
  const types = [
    "run.started",
    "run.completed",
    "run.failed",
    "plan.created",
    "skill.selected",
    "tool.completed",
    "evidence.added",
    "security.flagged",
    "answer.delta",
  ];
  for (const t of types) {
    es.addEventListener(t, (ev) => {
      const msg = ev as MessageEvent;
      onEvent(JSON.parse(msg.data) as RunEvent);
    });
  }
  es.onerror = (e) => onError?.(e);
  return es;
}

export async function fetchOntology() {
  const res = await fetch("/api/v1/ontology");
  if (!res.ok) throw new Error(`ontology ${res.status}`);
  return res.json() as Promise<{
    entity_types: string[];
    relation_types: string[];
    allowed_triples: { source: string; relation: string; target: string }[];
    status: string;
    note: string;
    node_count?: number;
    edge_count?: number;
  }>;
}

export async function fetchGraph(params?: { q?: string; node_id?: string }) {
  const qs = new URLSearchParams();
  if (params?.q) qs.set("q", params.q);
  if (params?.node_id) qs.set("node_id", params.node_id);
  const suffix = qs.toString() ? `?${qs}` : "";
  const res = await fetch(`/api/v1/graph${suffix}`);
  if (!res.ok) throw new Error(`graph ${res.status}`);
  return res.json() as Promise<{
    mode: string;
    nodes?: {
      id: string;
      name: string;
      labels: string[];
      description?: string;
      props?: Record<string, unknown>;
    }[];
    edges?: { source: string; type: string; target: string }[];
    node_count?: number;
    edge_count?: number;
  }>;
}

export async function parseEmbeddedLogs(body: {
  log_text?: string;
  use_fixture?: boolean;
}) {
  const res = await fetch("/api/v1/embedded/parse", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`embedded/parse ${res.status}`);
  return res.json() as Promise<{
    event_count: number;
    malformed: number;
    events: {
      timestamp: string;
      component: string;
      severity: string;
      code: string;
      message: string;
    }[];
    report: {
      suspected_components: string[];
      hypotheses: Record<string, unknown>[];
      confidence: number;
      next_actions: string[];
      recommended_tests: string[];
    };
  }>;
}
