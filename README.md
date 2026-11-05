# imagen-diagrams (Spillwave portable edition)

Turn Mermaid and PlantUML into themed slide and article figures.

Built from [SpillwaveSolutions/imagen-diagrams](https://github.com/SpillwaveSolutions/imagen-diagrams) v0.3.0 and repackaged for Claude Desktop, Cowork, and claude.ai.

## What changed from upstream

- Shares the image-gen engine: `imagen` CLI, `gemini-api` REST, `grok-img` CLI, `xai-api` REST, `codex`, with real failover. The upstream grok and codex argv did not match those CLIs.
- Diagrams default to Nano Banana Pro for label accuracy.
- Reads `.imagen-diagrams/config.yaml` (theme, backend, model, aspect, output_dir).
- `to_svg.py` is now a working SVG gate: well-formed XML, no raster or script, size budget, label coverage, and a PNG preview via rsvg-convert or headless Chrome.
- Code-drawn SVG path: when no image API is reachable (for example a claude.ai cloud session), Claude draws the themed figure as SVG and gates it, so you still get a figure.
- `render.py --feedback` for judge-driven retries.

## Themes

`claude-clay` (screen default), `manning-print` (print default), `agent-control`, `arctic-fox`, `towards-ai`.

## Keys

Same as image-gen: `GEMINI_API_KEY` and/or `XAI_API_KEY` in env or `~/.config/spillwave/image-keys.env`.

MIT License.
