import type { Meta, StoryObj } from "@storybook/react";
import LedgerPage from "./page";

/**
 * `/ledger` — polls `GET /tasks` every 3s and renders the task table with
 * state-based coloring. In Storybook there is no backend running, so `listTasks()`
 * rejects and the page renders its empty table (the component swallows fetch
 * errors via `.catch(() => {})`, matching production behavior when the API is
 * unreachable).
 */
const meta: Meta<typeof LedgerPage> = {
  title: "App/LedgerPage",
  component: LedgerPage,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "Task ledger view. Real data comes from `frontend/lib/api.ts#listTasks()` " +
          "against the FastAPI `/tasks` endpoint (`backend/src/atlas/api/main.py`).",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof LedgerPage>;

export const Empty: Story = {};
