---
name: imagen-diagrams
description: >
  Convert Mermaid and PlantUML into slide and article figures. Themes,
  layout-hints prompts, fidelity judge, optional SVG. Triggers: mermaid,
  plantuml, puml, slidedeck, slide diagram, article figure, imagen, theme,
  SVG translation, publication, glossary, STE100.
---

# imagen-diagrams

Illustration renderer. Not the diagram author.

- design-doc-mermaid authors Mermaid.
- plantuml authors leftover UML and Salt.
- This skill turns `.mmd` / `.puml` into a themed PNG (optional SVG).

## When to fire

Use this skill when the user wants a slide or article figure from diagram source, a theme extract, an SVG translation, or a publication figure pass.

Do not use this skill for Salt wireframes. Send those to the plantuml JAR.

## Persona

When the publication contract is active, act as product designer, technical writer, information architect, visual storyteller, technical illustrator, presentation designer, and full-stack web builder. Transform available research. Do not invent a new product.

## Research first

Before article, deck, or website work, inspect existing research. Determine thesis, findings, evidence, mechanisms, actors, interfaces, flows, boundaries, failure paths, tradeoffs, limitations, and uncertainties. Do not invent evidence.

## Inputs

- Source: `.mmd`, `.mermaid`, fenced mermaid, `.puml`, `.plantuml`, fenced plantuml
- Theme: `claude-clay`, `manning-print`, `agent-control`, `arctic-fox`, `towards-ai`, a YAML file, or a URL/image to extract
- Density: slide (default 16:9) or article (4:3)
- Backend: auto unless config pins one

## Outputs

- `<stem>_imagen.png`
- optional `<stem>_imagen.svg`
- sidecar with hash, theme, alt text, judge score

Never publish source syntax as the figure.

## Backend (auto)

1. `imagen` CLI if on PATH. Brace policy: `imagen-cli-vars` (double braces).
2. Else `grok` CLI. Brace policy: `grok-imagine` (no rewrite).
3. Else `codex` CLI. Brace policy: `grok-imagine` (no rewrite).
4. Else fail closed. Write the prompt sidecar and report that no image backend is installed.

Project `.imagen-diagrams/config.yaml` `backend:` can pin `imagen`, `grok`, or `codex`. Use `imagen-scan` to rewrite `{token}` to `(token)` for binaries that still scan inner braces.

## Theme resolution

1. Explicit `--theme` or "use theme X"
2. Figure sidecar
3. Project config
4. Built-in: `claude-clay` for screen, `manning-print` for print

## Scripts

From `skills/imagen-diagrams/scripts/`:

- `render.py` build prompt and call the image worker
- `extract_theme.py` URL or image to YAML
- `judge.py` score PNG against inventory
- `to_svg.py` translate a passing PNG
- `inventory.py` parse nodes and edges
- `prompt_builder.py` six-block layout-hints prompt

Compatibility shim: `tools/imagen-worker.sh` calls `render.py`.

Course-repo path: if `articles/<topic>/diagrams/` exists, write `improved_articles/<topic>/diagrams/<stem>_imagen.png` unless `output_dir` is set.

## Publication

If the user asks for article, deck, website, glossary, or publication figures, follow `references/publication-contract.md`. Write STE100. Zero em dash characters. One term per concept. Browse https://spillwave.com/guides/ for visual principles. Do not copy assets.

## Accuracy

Label accuracy has priority over decoration. If generated labels fail after retries, rebuild as a code-drawn SVG that still obeys the theme. That fallback is not a mermaid-cli export.

Read `references/` before inventing prompt text. Do not bake a palette into this file.
