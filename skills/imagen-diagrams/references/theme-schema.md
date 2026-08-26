# Theme schema

One YAML file per theme. Built-ins and extracted themes share the schema. See `themes/claude-clay.yaml`.

Required keys: id, name, version, aspect_default, style, palette, roles, negatives, svg.

Palette roles: background, surface, primary, primary_fg, accent, accent_2, success, ink, muted.

Resolution order:

1. Explicit --theme or "use theme X"
2. Figure sidecar theme
3. Project .imagen-diagrams/config.yaml
4. Built-in default (claude-clay for slides, manning-print for print and book)

Extract: sample surfaces, map onto roles, enforce contrast at least 4.5:1, write YAML plus a 16:9 swatch. Invalid YAML never reaches the worker.
