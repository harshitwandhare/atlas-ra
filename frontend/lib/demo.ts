/**
 * Sample dataset for the hosted preview.
 *
 * The dashboard talks to a local ATLAS backend. On the public deployment there
 * is no backend to reach, so the typed client falls back to this data and the
 * UI flags itself as a preview (see `demoMode` below). A local run with
 * `atlas serve` up never touches any of this — real data wins whenever the API
 * answers.
 *
 * The runs below mirror the shape of real ones: goals routed to a team, skills
 * matched from procedural memory, critic review before done.
 */

import type { AgentEvent, Approval, Skill, Task } from "./api";

const MINUTE = 60_000;

/** Fixed clock so server and client render identical timestamps. */
const BASE = Date.UTC(2026, 7, 14, 16, 30, 0);
const at = (minutesAgo: number) => new Date(BASE - minutesAgo * MINUTE).toISOString();

export const DEMO_TASKS: Task[] = [
  {
    id: "t_9f2c1a",
    goal: "Summarize how to fit Wan 2.2 5B in a 10GB VRAM budget",
    team: "research",
    state: "done",
    result:
      "Load the 5B checkpoint in fp8 and offload the text encoder to CPU between steps. " +
      "At head resolution 720x480 with 24 frames this peaks around 9.1GB. Drop to 16 frames " +
      "if the sampler reports an allocator retry.",
    created_at: at(48),
    updated_at: at(44),
  },
  {
    id: "t_4b8e07",
    goal: "Install StreamDiffusion and run a smoke test",
    team: "systems",
    state: "done",
    result:
      "Rebuilt the venv against torch 2.4.1+cu121, installed xformers before the StreamDiffusion " +
      "wheel to avoid the resolver downgrade. Smoke test held 4.74 FPS at 512x512.",
    created_at: at(36),
    updated_at: at(31),
  },
  {
    id: "t_1d55c3",
    goal: "Draft a TouchDesigner OSC bridge checklist",
    team: "research",
    state: "review",
    result: null,
    created_at: at(12),
    updated_at: at(11),
  },
  {
    id: "t_7ac420",
    goal: "Archive last week's LoRA training runs and free the scratch disk",
    team: "ops",
    state: "blocked",
    result: null,
    created_at: at(9),
    updated_at: at(8),
  },
  {
    id: "t_2e6f9b",
    goal: "Compare native TrainLoraNode against the custom trainer node",
    team: "research",
    state: "running",
    result: null,
    created_at: at(3),
    updated_at: at(1),
  },
];

export const DEMO_SKILLS: Skill[] = [
  {
    name: "touchdesigner-pipeline",
    version: "1.2.0",
    triggers: ["touchdesigner", "osc", "ndi"],
    body:
      "# TouchDesigner bridge\n\n" +
      "1. Start the StreamDiffusion backend in `td` mode before opening the .toe.\n" +
      "2. Bind OSC in on 7000, out on 7001 — the demo project assumes those ports.\n" +
      "3. Prefer the NDI bridge over PNG spout when the target is above 512x512;\n" +
      "   PNG round-trips through disk and costs about 40% of the frame budget.\n" +
      "4. If frames stall, check that the venv on PATH is the rebuilt one.",
  },
  {
    name: "wan22-vram-budget",
    version: "1.1.0",
    triggers: ["wan 2.2", "vram", "i2v"],
    body:
      "# Wan 2.2 within 10GB\n\n" +
      "- fp8 checkpoint, text encoder offloaded to CPU between sampler steps.\n" +
      "- 720x480 / 24 frames peaks near 9.1GB; 16 frames is the safe fallback.\n" +
      "- An allocator retry in the log means the next run should drop frame count\n" +
      "  before it drops resolution — quality falls off faster with resolution.",
  },
  {
    name: "venv-rebuild-order",
    version: "1.0.1",
    triggers: ["install", "torch", "xformers", "smoke test"],
    body:
      "# Install order matters\n\n" +
      "Install torch first, pinned to the CUDA build you actually want, then\n" +
      "xformers, then the project wheel. Installing the project first lets the\n" +
      "resolver pull a CPU torch and the failure surfaces much later as a\n" +
      "device-mismatch error that reads like a code bug.",
  },
];

export const DEMO_APPROVALS: Approval[] = [
  {
    id: "a_3c71fe",
    tool_name: "delete_path",
    args: { path: "D:/scratch/lora_runs/2026-08-05", recursive: true },
    state: "pending",
    created_at: at(8),
  },
  {
    id: "a_88b204",
    tool_name: "send_email",
    args: {
      to: "lab-team@example.edu",
      subject: "Weekly render benchmarks",
      body: "Attaching this week's throughput numbers for the StreamDiffusion box.",
    },
    state: "pending",
    created_at: at(6),
  },
  {
    id: "a_5d1099",
    tool_name: "run_powershell",
    args: { script: "Get-ChildItem D:/scratch -Recurse | Measure-Object -Property Length -Sum" },
    state: "approved",
    created_at: at(21),
  },
];

/** One full lifecycle, newest first — matches what the live bus would push. */
export const DEMO_EVENTS: AgentEvent[] = [
  { type: "state_change", task_id: "t_2e6f9b", agent: "orchestrator", payload: { state: "running" }, ts: at(1) },
  {
    type: "message_delta",
    task_id: "t_2e6f9b",
    agent: "research",
    payload: { text: "Native TrainLoraNode covers rank and alpha but not per-block LR..." },
    ts: at(2),
  },
  { type: "skill_matched", task_id: "t_2e6f9b", agent: "memory", payload: { text: "wan22-vram-budget v1.1.0" }, ts: at(3) },
  { type: "task_created", task_id: "t_2e6f9b", agent: "orchestrator", payload: { text: "Compare native TrainLoraNode against the custom trainer node" }, ts: at(3) },
  { type: "approval_requested", task_id: "t_7ac420", agent: "ops", payload: { tool: "delete_path" }, ts: at(8) },
  { type: "state_change", task_id: "t_1d55c3", agent: "orchestrator", payload: { state: "review" }, ts: at(11) },
  { type: "critic_review", task_id: "t_4b8e07", agent: "critic", payload: { text: "approve — smoke test output present" }, ts: at(31) },
  { type: "state_change", task_id: "t_4b8e07", agent: "orchestrator", payload: { state: "done" }, ts: at(31) },
];
