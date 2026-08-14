import type { Meta, StoryObj } from "@storybook/react";
import SkillsPage from "./page";

/**
 * `/skills` — renders `GET /skills` (parsed `skills/*.md` playbooks, see
 * `backend/src/atlas/memory/procedural.py#SkillStore`) as cards. Without a
 * running backend the fetch rejects and the page renders zero cards — the
 * grid layout and empty state are still exercised here.
 */
const meta: Meta<typeof SkillsPage> = {
  title: "App/SkillsPage",
  component: SkillsPage,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component:
          "Procedural memory browser. Each card is one `Skill` " +
          "(name, semver version, trigger keywords, markdown body).",
      },
    },
  },
};

export default meta;
type Story = StoryObj<typeof SkillsPage>;

export const Empty: Story = {};
