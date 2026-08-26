# PlantUML notes

Do not convert PUML to Mermaid as a hard requirement.

- Parser extracts node labels, edges, and diagram type from @startuml and diagram keywords.
- Full .puml body is the layout-hints block.
- Negatives also ban @startuml, class X {, and Salt syntax in the image.
- If the PUML is a Salt wireframe, skip Imagen and tell the user to use the plantuml skill deterministic renderer.

Wireframes are not slide illustrations.
