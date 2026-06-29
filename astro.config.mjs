// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

const BASE = "/agentic-compliance-platform";

// The articles use root-absolute internal links (e.g. /ai/agent-security/) that were authored
// for a root deployment. Under a GitHub Pages base path, Astro does NOT rebase markdown body
// links automatically, so this rehype plugin prefixes internal root-absolute <a href>s with the
// base at build time — leaving external, anchor, and already-based links untouched.
function rehypeRebaseInternalLinks() {
  /** @param {any} tree */
  return (tree) => {
    /** @param {any} node */
    const walk = (node) => {
      if (
        node.type === "element" &&
        node.tagName === "a" &&
        node.properties &&
        typeof node.properties.href === "string"
      ) {
        const href = node.properties.href;
        if (
          href.startsWith("/") &&
          !href.startsWith("//") &&
          href !== BASE &&
          !href.startsWith(BASE + "/")
        ) {
          node.properties.href = BASE + href;
        }
      }
      if (Array.isArray(node.children)) node.children.forEach(walk);
    };
    walk(tree);
  };
}

// Engineering portfolio, deployed to GitHub Pages as a project site.
export default defineConfig({
  site: "https://ermiasmikael.github.io",
  base: BASE,
  markdown: {
    rehypePlugins: [rehypeRebaseInternalLinks],
  },
  integrations: [
    starlight({
      title: "Infopole Engineering",
      description:
        "How the DPS denied-party-screening platform is built — architecture, applied AI, and AI agent security.",
      customCss: ["./src/styles/custom.css"],
      // Default to light when the visitor has no stored preference (toggle still works).
      components: {
        ThemeProvider: "./src/components/ThemeProvider.astro",
      },
      sidebar: [
        {
          label: "Start here",
          items: [{ label: "Welcome", link: "/" }],
        },
        {
          label: "Architecture",
          autogenerate: { directory: "architecture" },
        },
        {
          label: "Applied AI",
          autogenerate: { directory: "ai" },
        },
        {
          label: "Machine learning",
          autogenerate: { directory: "ml" },
        },
        {
          label: "Decisions",
          autogenerate: { directory: "decisions" },
        },
        {
          label: "Code",
          autogenerate: { directory: "code" },
        },
      ],
    }),
  ],
});
