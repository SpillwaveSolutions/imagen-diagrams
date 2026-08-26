# Layout-hints prompt contract

Six blocks. Theme fills Palette and parts of Style. Type overlay fills extra bans.

1. Framing. This is a slide diagram (or article figure) for a technical presentation about {topic}. Render an illustration of the concept below.
2. Style. Clean minimalist technical illustration. Boxes, arrows, labels. Label size floor. Landscape unless theme or aspect says otherwise.
3. Palette. Injected from theme YAML. Named hex roles, not free prose.
4. Negative list. No source syntax, no ASCII, no tiny labels, no watermarks, no logos. Plus type-specific bans. No em dash characters in labels.
5. Diagram type. flowchart | sequence | class | state | activity | c4 | other.
6. Layout hints. Full source inside a fenced block, marked use only as guidance for structure.

Closer (bookend, last tokens): Convert the visual boxes, arrows, and labels. The image must show a finished diagram, not Mermaid or PlantUML code.

Prose prompt is the same framing, style, palette, and negatives with a plain-English description instead of source. Used only when source is empty or the user asks.

Brace escape is applied after the prompt is built. Policy lives next to the adapter.
