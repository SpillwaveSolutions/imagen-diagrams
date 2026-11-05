---
description: Score a figure PNG against its diagram source and regenerate on failure.
---

Load the imagen-diagrams skill and follow its Judge section: run judge.py, then open the PNG and check every label, edge, and theme floor. On a miss, rerun render with --feedback listing the concrete misses. Cap at 2 retries.
