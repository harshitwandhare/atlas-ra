import type { Preview } from "@storybook/react";
import React from "react";
import "../app/globals.css";

const preview: Preview = {
  parameters: {
    layout: "padded",
    backgrounds: {
      default: "atlas-dark",
      values: [{ name: "atlas-dark", value: "#09090b" }],
    },
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
  decorators: [
    (Story) =>
      // The app renders on a dark zinc background (see app/globals.css); Storybook's
      // canvas doesn't pick up the <body> class from layout.tsx, so replicate it here.
      React.createElement(
        "div",
        { className: "bg-zinc-950 text-zinc-100 min-h-screen p-6" },
        React.createElement(Story)
      ),
  ],
};

export default preview;
