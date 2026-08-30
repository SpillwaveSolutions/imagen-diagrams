# imagen-diagrams

Illustration renderer for Mermaid and PlantUML. Not the diagram author.

design-doc-mermaid writes Mermaid. plantuml writes leftover UML and Salt. This skill turns `.mmd` and `.puml` into a themed PNG. Optional SVG follows a passing judge.

Hosts: Claude Code, Codex, Grok Build, Cursor, SKILZ / Agent Plugins 1.0.

## Built-in themes

- **claude-clay**: cream paper, clay, soft yellow, muted lavender, sage, ink arrows.
- **manning-print**: white paper, black ink, four greys. Print-safe.
- **agent-control**: white canvas, deep navy cards and arrows, an orange tool boundary, green repository target.
- **arctic-fox**: white paper, deep navy ink, royal-blue emphasis, silver-grey surfaces.
- **towards-ai**: warm paper, near-black ink, royal-blue emphasis. Towards AI brand palette.

Add a theme as YAML under `skills/imagen-diagrams/themes/` or `.imagen-diagrams/themes/`. Extract a theme from a URL or an image.

## Backend (auto)

1. `imagen` CLI if it is on PATH. Brace policy: double `{` and `}`.
2. Else `grok` CLI. Brace policy: no rewrite.
3. Else `codex` CLI. Brace policy: no rewrite.
4. Else fail closed. The prompt sidecar is still written.

Pin a backend in `.imagen-diagrams/config.yaml` if you do not want auto.

## Install

```text
skilz install SpillwaveSolutions/imagen-diagrams
```

Claude Code / Grok Build from the documentation marketplace:

```text
/plugin marketplace add SpillwaveSolutions/spillwave-documentation-marketplace
/plugin install imagen-diagrams@spillwave-documentation
```

Claude Code `/plugin` also loads this tree. Grok Build loads Claude plugins with zero extra config.

## Commands

- `/imagen-render` source to PNG
- `/imagen-theme` extract or list themes
- `/imagen-svg` translate a passing PNG
- `/imagen-judge` score a PNG against source inventory

Scripts live in `skills/imagen-diagrams/scripts/`. Course repos can call `tools/imagen-worker.sh` as a drop-in shim.

## Publication contract

When the user asks for article, deck, website, glossary, or publication figures, follow `skills/imagen-diagrams/references/publication-contract.md`.

Hard writing rule: zero em dash characters. STE100 voice. One term per concept. Never publish source syntax as the figure.

## Status

v0.1.0 scaffold. Published at [SpillwaveSolutions/imagen-diagrams](https://github.com/SpillwaveSolutions/imagen-diagrams). Listed in [spillwave-documentation-marketplace](https://github.com/SpillwaveSolutions/spillwave-documentation-marketplace). Judge and theme extract are first-pass. Manning greys can be tightened from the book palette.
