#!/usr/bin/env python3
"""Fidelity judge. Inventory plus file checks. Vision pass is agent-assisted."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from inventory import inventory_from_source


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True)
    p.add_argument("--png", required=True)
    p.add_argument("--sidecar")
    args = p.parse_args()

    source = Path(args.source).read_text(encoding="utf-8")
    inv = inventory_from_source(source)
    png = Path(args.png)
    misses: list[str] = []
    if inv.salt:
        misses.append("Salt wireframe. Do not judge through Imagen.")
    if not png.exists() or png.stat().st_size < 32:
        misses.append("PNG missing or empty.")
    if inv.language == "unknown":
        misses.append("Source language unknown.")
    if len(inv.nodes) == 0:
        misses.append("Inventory has zero nodes.")

    result = {
        "pass": len(misses) == 0,
        "nodes": [n.label for n in inv.nodes],
        "edges": len(inv.edges),
        "misses": misses,
        "note": (
            "Mechanical checks only. A vision pass must confirm every source label "
            "is readable text and that no source syntax is visible."
        ),
    }
    if args.sidecar:
        Path(args.sidecar).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if misses:
        print("REGENERATION FEEDBACK:", "; ".join(misses), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
