#!/usr/bin/env python3
"""Six-block layout-hints prompt builder."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from backends import BracePolicy, escape_for_backend
from inventory import DiagramKind, inventory_from_source

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

Density = Literal["article", "slide"]

TYPE_BANS: dict[DiagramKind, list[str]] = {
    "flowchart": [
        "Do not invent or duplicate nodes.",
        "Do not reroute edges.",
        "Keep horizontal text.",
        "Do not print node IDs as labels.",
    ],
    "sequence": [
        "Preserve call order on lifelines.",
        "Do not invent actors.",
        "Keep request and response direction correct.",
    ],
    "class": [
        "Preserve inheritance, composition, and associations that appear in source.",
        "Do not invent attributes or methods.",
    ],
    "state": [
        "Preserve transition direction and terminal states.",
        "Do not invent states.",
    ],
    "activity": [
        "Preserve branch conditions that appear in source.",
        "Do not invent steps.",
    ],
    "c4": [
        "Preserve system boundaries and external actors.",
        "Do not invent containers.",
    ],
    "other": ["Do not invent nodes or relationships."],
}

THEMES_DIR = Path(__file__).resolve().parent.parent / "themes"


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    """Minimal YAML subset for theme files if PyYAML is missing."""
    data: dict[str, Any] = {"palette": {}, "style": {}, "negatives": []}
    section = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("  ") and ":" in line and section in ("palette", "style"):
            k, _, v = line.strip().partition(":")
            data[section][k.strip()] = v.strip().strip('"')
            continue
        if line.strip().startswith("- ") and section == "negatives":
            data["negatives"].append(line.strip()[2:].strip())
            continue
        if line[0].isspace():
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip().strip('"')
        if key in ("palette", "style", "roles", "svg", "source"):
            section = key
            continue
        if key == "negatives":
            section = "negatives"
            continue
        section = None
        if val:
            data[key] = val
    return data


def load_theme(theme_id: str) -> dict[str, Any]:
    path = THEMES_DIR / f"{theme_id}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"theme not found: {theme_id}")
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        return yaml.safe_load(text)
    return _parse_simple_yaml(text)


def build_layout_hints_prompt(
    *,
    source: str,
    topic: str,
    theme_id: str,
    density: Density,
    policy: BracePolicy,
) -> str:
    theme = load_theme(theme_id)
    inv = inventory_from_source(source)
    palette = theme.get("palette") or {}
    style_meta = theme.get("style") or {}
    summary = style_meta.get("summary") or theme.get("summary") or ""
    if isinstance(summary, str):
        summary = " ".join(summary.split())
    label_min = style_meta.get("label_min_px") or 24
    contrast = style_meta.get("contrast_min") or 4.5
    arrow = style_meta.get("arrow_px") or [2, 3]
    if isinstance(arrow, str):
        arrow = [2, 3]

    density_line = (
        "Slide density. Fewer nodes. Larger labels. One primary flow. Readable from presentation distance."
        if density == "slide"
        else "Article density. Clear labels. Limited node count. Key path visually dominant. Still simplified for editorial layout."
    )

    framing = (
        f"This is a {density} diagram for a technical presentation about {topic}. "
        "Render an illustration of the concept below."
    )
    style = " ".join(
        [
            summary,
            "Boxes, arrows, and labels.",
            f"Labels at least {label_min} pixels at {density} scale.",
            f"Arrows {arrow[0]} to {arrow[1]} px.",
            "Horizontal text. Landscape layout unless the structure is a tall flowchart.",
            density_line,
            "The image must look like a professionally designed technical illustration, not a diagramming-tool screenshot.",
        ]
    )
    palette_block = " ".join(
        [
            f"Background {palette.get('background', '')}.",
            f"Surface {palette.get('surface', '')}.",
            f"Primary {palette.get('primary', '')} with text {palette.get('primary_fg', '')}.",
            f"Accent {palette.get('accent', '')}.",
            f"Secondary accent {palette.get('accent_2', '')}.",
            f"Success {palette.get('success', '')}.",
            f"Ink arrows {palette.get('ink', '')}.",
            f"Muted {palette.get('muted', '')}.",
            f"Text contrast at least {contrast}:1.",
        ]
    )
    negatives = " ".join(
        [
            *(theme.get("negatives") or []),
            *TYPE_BANS[inv.kind],
            "No mermaid syntax such as graph LR, -->, subgraph.",
            "No plantuml syntax such as @startuml.",
            "No ASCII art.",
            "No watermarks or logos.",
            "No em dash characters in labels.",
            "Do not expose source notation.",
            "Do not add a title, heading, caption, or banner text of any kind. "
            "The source names nodes, never the diagram, so any title would be "
            "invented. Render only the nodes, edges, and their labels.",
        ]
    )
    layout = "\n".join(
        [
            "Use the following source only as guidance for structure. Convert the visual boxes, arrows, and labels.",
            "```",
            source.strip(),
            "```",
        ]
    )
    closer = (
        "Convert the visual boxes, arrows, and labels. "
        "The image must show a finished diagram, not Mermaid or PlantUML code."
    )
    raw = "\n\n".join(
        [
            f"FRAMING\n{framing}",
            f"STYLE\n{style}",
            f"PALETTE\n{palette_block}",
            f"NEGATIVE LIST\n{negatives}",
            f"DIAGRAM TYPE\n{inv.kind}",
            f"LAYOUT HINTS\n{layout}",
            closer,
        ]
    )
    return escape_for_backend(raw, policy)


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--topic", default="diagram")
    p.add_argument("--theme", default="claude-clay")
    p.add_argument("--density", choices=("slide", "article"), default="slide")
    p.add_argument(
        "--policy",
        choices=("imagen-cli-vars", "imagen-cli-scan", "grok-imagine"),
        default="imagen-cli-vars",
    )
    args = p.parse_args()
    src = Path(args.source).read_text(encoding="utf-8")
    sys.stdout.write(
        build_layout_hints_prompt(
            source=src,
            topic=args.topic,
            theme_id=args.theme,
            density=args.density,
            policy=args.policy,
        )
    )
