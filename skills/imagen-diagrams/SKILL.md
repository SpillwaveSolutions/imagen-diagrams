---
name: imagen-diagrams
description: Turn Mermaid or PlantUML source into a themed slide or article figure (PNG, optional SVG) with a layout-hints image prompt, a fidelity judge, and a code-drawn SVG fallback. Use for "make this mermaid a slide figure", "render this plantuml for my article", "themed diagram", "article figure", "slide diagram", "publication figures", "extract a theme from this site", "translate to SVG", "claude-clay", "manning-print". Not for Salt wireframes (use plantuml) or for illustrations with no diagram source (use image-gen).
---

# imagen-diagrams

Illustration renderer. Not the diagram author.

- A Mermaid or PlantUML author writes the source.
- The `plantuml` skill renders exact UML and Salt wireframes.
- This skill turns `.mmd` / `.puml` into a themed, editorially simplified figure.

## Paths

Scripts live in `scripts/`, themes in `themes/`, contracts in `references/`, all inside this skill's base directory (shown as "Base directory for this skill" when the skill loads). Set it first in every command:

```bash
SKILL="<base directory for this skill>"
```

Write figures next to the source, into `output_dir` from project config, or into the user's connected folder. Hand finished figures to the user with the file-sending tool.

## Inputs

- Source: `.mmd`, `.mermaid`, fenced mermaid, `.puml`, `.plantuml`, fenced plantuml. Save a fenced block to a file first.
- Theme: `claude-clay`, `manning-print`, `agent-control`, `arctic-fox`, `towards-ai`, a YAML file, or a URL/image to extract.
- Density: `slide` (16:9, fewer nodes, bigger labels) or `article` (4:3).
- Backend: auto unless the user or project config pins one.

## Theme resolution

1. Explicit `--theme` or "use theme X"
2. Figure sidecar
3. Project config (`.imagen-diagrams/config.yaml` or `.imagen-diagrams.yaml`, nearest parent folder)
4. Built-in: `claude-clay` for screen, `manning-print` for print

List or extract themes:

```bash
python3 "$SKILL/scripts/extract_theme.py"            # list
python3 "$SKILL/scripts/extract_theme.py" --url URL  # extract to YAML
```

## Render

```bash
python3 "$SKILL/scripts/check_setup.py" --no-network   # what can run here
python3 "$SKILL/scripts/render.py" --source diagrams/flow.mmd \
  --topic "agent control loop" --theme claude-clay --density slide
```

Backend order (auto): `imagen` CLI, `gemini-api` (REST, key only), `grok-img` CLI, `xai-api` (REST, key only), `codex`. Failures fall through. Diagrams default to Nano Banana Pro because labels must be exact. Exit codes: 0 ok, 2 no backend, 3 Salt, 4 worker wrote nothing, 5 network blocked.

Keys and setup: load the `image-gen-setup` skill when it is installed, or tell the user to put `GEMINI_API_KEY=...` in `~/.config/spillwave/image-keys.env`. Never ask for a key in chat.

On exit 2 or 5, do not stop. Take the code-drawn SVG path below and tell the user in one sentence that the figure was drawn as SVG because no image backend was reachable.

## Judge (every PNG)

1. Mechanical: `python3 "$SKILL/scripts/judge.py" --source SRC --png PNG --sidecar PNG_judge.json`
2. Vision: open the PNG with the file-reading tool. Check every source label appears spelled exactly, edges connect the right nodes (count within 10 percent), no source syntax is visible, text is legible at the target density, and colors follow the theme.
3. On a miss, rerun render with `--feedback "<concrete misses>"`. Cap at 2 retries.
4. If labels still fail, take the code-drawn SVG path. Label accuracy beats decoration.

## Code-drawn SVG path

Use when no backend runs, when labels keep failing, or when the user asks for SVG. When a passing PNG exists, it is the visual spec and the source is the structure of record.

1. Read the theme YAML from `themes/` for palette, type, label size, and contrast floors.
2. Write a raw SVG by hand: every node from the inventory, every edge with arrowheads, theme colors, text as real `<text>` elements, no raster embeds, no scripts, no animation. Apply the same editorial simplification the prompt would.
3. Gate it and render a PNG preview:

   ```bash
   python3 "$SKILL/scripts/to_svg.py" --svg fig_imagen.svg --source SRC \
     --png-out fig_imagen.png --strict-labels
   ```

4. Open the PNG preview and run the vision check above. Fix and regate until it passes.

This is not a mermaid-cli export. It is a designed figure.

## Outputs

- `<stem>_imagen.png`
- optional `<stem>_imagen.svg`
- `<stem>_imagen.json` sidecar with hash, theme, inventory, backend, model
- `<stem>_imagen.prompt.txt`

Never publish source syntax as the figure.

## Course-repo path

If `articles/<topic>/diagrams/` exists, write `improved_articles/<topic>/diagrams/<stem>_imagen.png` unless `output_dir` is set.

## Persona

When the publication contract is active, act as product designer, technical writer, information architect, visual storyteller, technical illustrator, presentation designer, and full-stack web builder. Transform available research. Do not invent a new product.

## Research first

Before article, deck, or website work, inspect existing research. Determine thesis, findings, evidence, mechanisms, actors, interfaces, flows, boundaries, failure paths, tradeoffs, limitations, and uncertainties. Do not invent evidence.

## Publication

If the user asks for article, deck, website, glossary, or publication figures, follow `references/publication-contract.md`. Write STE100 (`references/ste100.md`). Zero em dash characters. One term per concept. Use https://spillwave.com/guides/ for visual principles. Do not copy assets.

Read `references/prompt-contract.md` and `references/quality-gates.md` before inventing prompt text. Do not bake a palette into this file.
