# Quality gates

## Fidelity judge (PNG)

Inputs: source inventory (nodes, edges, labels), PNG, theme.

Checks:

- Every source label appears as readable text.
- Edge count is within 10 percent and connectivity is plausible.
- No source syntax visible.
- Contrast and label size meet the theme floors.

On failure prepend a REGENERATION FEEDBACK block with the concrete misses and rerun. Cap retries (default 2). Persist the last score in the sidecar.

v0.1.0 judge is inventory plus file checks. A vision pass (agent or model) must confirm labels when a raster exists. Do not accept a pretty PNG with wrong labels.

## SVG mechanical gate

- Raw document, first char `<`, last `</svg>`
- No raster embed, no animation
- Size budget 30 KB (15 KB if 8 nodes or fewer)
- Text count at least half the source node count
- xmllint well-formed if available
- rsvg-convert renders if available

Judge the PNG first. Only translate a passing PNG.
