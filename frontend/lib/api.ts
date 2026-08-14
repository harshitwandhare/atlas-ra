export const API = process.env.NEXT_PUBLIC_ATLAS_API ?? "http://localhost:8000";
export const WS = API.replace(/^http/, "ws") + "/ws";

export interface Task {
  id: string;
  goal: string;
  team: string;
  state: string;
  result: string | null;
  created_at: string;
  updated_at: string;
}

export interface AgentEvent {
  type: string;
  task_id: string;
  agent: string;
  payload: Record<string, unknown>;
  ts: string;
}

export interface Skill {
  name: string;
  version: string;
  triggers: string[];
  body: string;
}

export interface Approval {
  id: string;
  tool_name: string;
  args: Record<string, unknown>;
  state: string;
  created_at: string;
}

/* ------------------------------------------------------------------ *
 * Demo mode
 *
 * The dashboard expects a local backend. When it cannot be reached — the
 * public deployment, or a local run with `atlas serve` down — the client
 * serves sample data and flips this flag so the UI can say so. Any
 * successful call clears it again.
 * ------------------------------------------------------------------ */

let demo = false;
const listeners = new Set<(v: boolean) => void>();

const setDemo = (v: boolean) => {
  if (demo === v) return;
  demo = v;
  listeners.forEach((fn) => fn(v));
};

export const isDemo = () => demo;

/** For non-fetch transports (the WebSocket) to report they cannot connect. */
export const markDemo = (v: boolean) => setDemo(v);

export function subscribeDemo(fn: (v: boolean) => void): () => void {
  listeners.add(fn);
  return () => {
    listeners.delete(fn);
  };
}

/** Run a request, falling back to sample data if the backend is unreachable. */
async function withFallback<T>(request: () => Promise<Response>, fallback: T): Promise<T> {
  try {
    const res = await request();
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = (await res.json()) as T;
    setDemo(false);
    return data;
  } catch {
    setDemo(true);
    return fallback;
  }
}

export const submitGoal = (goal: string) =>
  withFallback<{ task_id: string; demo?: boolean }>(
    () =>
      fetch(`${API}/goals`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ goal }),
      }),
    { task_id: "t_preview", demo: true },
  );

export const listTasks = async (state?: string) => {
  const { DEMO_TASKS } = await import("./demo");
  const url = state ? `${API}/tasks?state=${encodeURIComponent(state)}` : `${API}/tasks`;
  const tasks = await withFallback<Task[]>(() => fetch(url), DEMO_TASKS);
  // The live API filters server-side; the fallback has to do it here.
  return isDemo() && state ? tasks.filter((t) => t.state === state) : tasks;
};

export const listSkills = async () => {
  const { DEMO_SKILLS } = await import("./demo");
  return withFallback<Skill[]>(() => fetch(`${API}/skills`), DEMO_SKILLS);
};

export const listApprovals = async () => {
  const { DEMO_APPROVALS } = await import("./demo");
  return withFallback<Approval[]>(() => fetch(`${API}/approvals`), DEMO_APPROVALS);
};

export const decideApproval = (id: string, approved: boolean) =>
  withFallback<unknown>(
    () =>
      fetch(`${API}/approvals/${id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ approved }),
      }),
    null,
  );
