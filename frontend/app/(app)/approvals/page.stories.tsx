import type { Meta, StoryObj } from "@storybook/react";
import ApprovalsPage from "./page";

/**
 * `/approvals` — the human-in-the-loop gate for `Risk.DESTRUCTIVE` tool calls
 * and outbound email (`backend/src/atlas/executors/approvals.py#ApprovalQueue`).
 * Polls `GET /approvals` every 2.5s; Approve/Deny buttons call
 * `POST /approvals/{id}`. Rendered here without a backend, so it shows the
 * "No pending approvals" empty state.
 */
const meta: Meta<typeof ApprovalsPage> = {
  title: "App/ApprovalsPage",
  component: ApprovalsPage,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "Nothing marked `destructive` in `atlas.executors.registry.Risk` " +
          "executes without a human decision made on this page.",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof ApprovalsPage>;

export const Empty: Story = {};
