#!/usr/bin/env python3
"""SVG translation gate. Fail closed if grok CLI is missing or the PNG has not passed."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--png", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--out")
    args = p.parse_args()
    png = Path(args.png)
    if not png.exists():
        print("PNG missing. Judge the raster first.", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else png.with_suffix(".svg")
    grok = shutil.which("grok")
    if not grok:
        print(
            "SVG backend is grok CLI. Fail closed. Raster still ships at "
            f"{png}.",
            file=sys.stderr,
        )
        return 2
    print(f"{grok} would translate {png} using {args.source} as structure of record -> {out}")
    print("v0.1.0 does not invoke the translator automatically. Keep the passing PNG.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
