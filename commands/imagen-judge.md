---
description: Score a PNG against the source inventory. Fail prepends regeneration feedback.
---

Run `skills/imagen-diagrams/scripts/judge.py`.

Checks: every source label appears as readable text, edge count within 10 percent, no source syntax, contrast and label size meet the theme floors.

On fail, prepend a REGENERATION FEEDBACK block and rerun render. Cap retries (default 2). Persist the last score in the sidecar.
