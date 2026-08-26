---
description: List built-in themes or extract a theme from a URL or image.
---

Run `skills/imagen-diagrams/scripts/extract_theme.py`.

- No args: list built-in themes and project themes.
- `--url`: fetch the page, sample colors, write YAML plus a swatch.
- `--image`: map the image onto the theme schema (model-assisted is allowed). The file must validate before use.

Enforce contrast at least 4.5:1. Invalid YAML never reaches the worker.
