---
description: Translate a passing PNG into a raw SVG that still matches the source inventory.
---

Run `skills/imagen-diagrams/scripts/to_svg.py` only after the fidelity judge passes.

PNG is the visual spec. Source is structure of record. Do not translate a failing PNG.

Mechanical gate: well-formed XML, first char `<`, last `</svg>`, no raster embed, no animation, size budget 30 KB (15 KB if 8 nodes or fewer), real text nodes at least half the source node count.
