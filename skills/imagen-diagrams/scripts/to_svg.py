#!/usr/bin/env python3
"""SVG mechanical gate, plus PNG preview render.

The agent writes the SVG itself, either by translating a passing PNG (PNG is
the visual spec, source is the structure of record) or by drawing the figure
directly when no image backend is available. This script checks the result:

- raw document: first char `<`, ends with `</svg>`, well-formed XML
- no raster embed (<image>, data: URIs), no animation, no <script>
- size budget 30 KB (15 KB when the source has 8 nodes or fewer)
- text elements at least half the source node count
- every source node label appears as text (case-insensitive) when --strict-labels
- renders with rsvg-convert (or Chrome headless) when available; writes PNG preview

Usage:
  python3 to_svg.py --svg fig.svg --source fig.mmd [--png-out fig_imagen.png] [--strict-labels]
Exit 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from inventory import inventory_from_source  # noqa: E402

SVG_NS = "{http://www.w3.org/2000/svg}"


def local(tag: str) -> str:
    return tag.split("}", 1)[-1]


def render_png(svg: Path, png: Path, width: int) -> str | None:
    """Rasterize the SVG. Returns the tool name used, or None."""
    rsvg = shutil.which("rsvg-convert")
    if rsvg:
        proc = subprocess.run([rsvg, "-w", str(width), "-o", str(png), str(svg)], capture_output=True)
        if proc.returncode == 0 and png.exists():
            return "rsvg-convert"
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        chrome = shutil.which(name)
        if not chrome:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            proc = subprocess.run(
                [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
                 f"--screenshot={png}", f"--window-size={width},{int(width * 0.5625)}",
                 svg.resolve().as_uri()],
                capture_output=True, cwd=tmp,
            )
        if proc.returncode == 0 and png.exists():
            return name
    return None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--svg", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--png-out", help="Write a PNG preview here")
    p.add_argument("--width", type=int, default=1920)
    p.add_argument("--strict-labels", action="store_true")
    p.add_argument("--budget-kb", type=int)
    args = p.parse_args()

    svg_path = Path(args.svg)
    text = svg_path.read_text(encoding="utf-8")
    inv = inventory_from_source(Path(args.source).read_text(encoding="utf-8"))
    misses: list[str] = []

    stripped = text.strip()
    if not stripped.startswith("<"):
        misses.append("Document does not start with '<'.")
    if not stripped.endswith("</svg>"):
        misses.append("Document does not end with '</svg>'.")

    texts: list[str] = []
    try:
        root = ET.fromstring(stripped)
        if local(root.tag) != "svg":
            misses.append("Root element is not <svg>.")
        for el in root.iter():
            tag = local(el.tag)
            if tag == "image":
                misses.append("Raster <image> embed found.")
            if tag in ("animate", "animateTransform", "animateMotion", "set"):
                misses.append(f"Animation element <{tag}> found.")
            if tag == "script":
                misses.append("<script> found.")
            if tag in ("text", "tspan"):
                content = "".join(el.itertext()).strip()
                if content and tag == "text":
                    texts.append(content)
    except ET.ParseError as err:
        misses.append(f"Not well-formed XML: {err}")
    if "data:image" in text:
        misses.append("data:image URI found.")

    budget = args.budget_kb or (15 if len(inv.nodes) <= 8 else 30)
    size_kb = len(text.encode("utf-8")) / 1024
    if size_kb > budget:
        misses.append(f"Size {size_kb:.1f} KB exceeds {budget} KB budget.")

    if inv.nodes and len(texts) < max(1, len(inv.nodes) // 2):
        misses.append(f"Only {len(texts)} text elements for {len(inv.nodes)} source nodes.")

    all_text = " ".join(texts).lower()
    all_text_norm = re.sub(r"\s+", " ", all_text)
    missing_labels = [
        n.label for n in inv.nodes
        if re.sub(r"\s+", " ", n.label.lower()) not in all_text_norm
    ]
    if args.strict_labels and missing_labels:
        misses.append("Labels missing: " + ", ".join(missing_labels[:12]))

    rendered_with = None
    if args.png_out:
        rendered_with = render_png(svg_path, Path(args.png_out), args.width)
        if not rendered_with:
            misses.append("Could not rasterize SVG (no rsvg-convert or Chrome).")

    result = {
        "pass": not misses,
        "size_kb": round(size_kb, 1),
        "budget_kb": budget,
        "text_elements": len(texts),
        "source_nodes": len(inv.nodes),
        "labels_not_found": missing_labels,
        "png_preview": args.png_out if rendered_with else None,
        "rasterizer": rendered_with,
        "misses": misses,
    }
    print(json.dumps(result, indent=2))
    if misses:
        print("SVG GATE FEEDBACK:", "; ".join(misses), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
