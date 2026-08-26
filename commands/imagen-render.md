---
description: Render Mermaid or PlantUML as a themed slide or article PNG.
---

Run `skills/imagen-diagrams/scripts/render.py` on the given source.

1. Inventory nodes and edges. If Salt, stop and send the user to the plantuml JAR.
2. Resolve theme (claude-clay, manning-print, YAML, or extract).
3. Apply editorial simplify for slide or article density.
4. Build the six-block layout-hints prompt.
5. Apply the brace policy for the chosen backend (auto: imagen, then grok, then codex).
6. Call the image worker. Write `<stem>_imagen.png` and a sidecar.
7. Judge. Retry with feedback if it fails.

Never publish source syntax as the figure.
