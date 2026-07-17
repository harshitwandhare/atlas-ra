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

export const submitGoal = (goal: string) =>
  fetch(`${API}/goals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ goal }),
  }).then((r) => r.json() as Promise<{ task_id: string }>);

export const listTasks = () => fetch(`${API}/tasks`).then((r) => r.json() as Promise<Task[]>);
export const listSkills = () => fetch(`${API}/skills`).then((r) => r.json() as Promise<Skill[]>);
