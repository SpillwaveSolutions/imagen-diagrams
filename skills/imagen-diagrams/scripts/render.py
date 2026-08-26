#!/usr/bin/env python3
"""Render diagram source to a themed PNG via the auto image backend."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from backends import argv_for, detect_backend
from inventory import inventory_from_source
from prompt_builder import build_layout_hints_prompt, load_theme

SCRIPTS = Path(__file__).resolve().parent


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def default_output(source_path: Path, output_dir: Path | None) -> Path:
    stem = source_path.stem
    parts = source_path.resolve().parts
    if output_dir:
        return output_dir / f"{stem}_imagen.png"
    if "diagrams" in parts and "articles" in parts:
        improved = Path(
            *["improved_articles" if p == "articles" else p for p in parts[:-1]]
        )
        improved.mkdir(parents=True, exist_ok=True)
        return improved / f"{stem}_imagen.png"
    return source_path.with_name(f"{stem}_imagen.png")


def main() -> int:
    p = argparse.ArgumentParser(description="imagen-diagrams render")
    p.add_argument("--source", required=True)
    p.add_argument("--topic", default="diagram")
    p.add_argument("--theme", default="claude-clay")
    p.add_argument("--density", choices=("slide", "article"), default="slide")
    p.add_argument("--backend", default="auto")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--output-dir")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    source_path = Path(args.source)
    source = source_path.read_text(encoding="utf-8")
    inv = inventory_from_source(source)
    if inv.salt:
        print(
            "Salt wireframe detected. Skip Imagen. Use the plantuml JAR renderer.",
            file=sys.stderr,
        )
        return 3

    load_theme(args.theme)
    resolved = detect_backend(args.backend)
    policy = resolved.policy if resolved else "imagen-cli-vars"
    prompt = build_layout_hints_prompt(
        source=source,
        topic=args.topic,
        theme_id=args.theme,
        density=args.density,
        policy=policy,
    )

    out = default_output(
        source_path, Path(args.output_dir) if args.output_dir else None
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    prompt_file = out.with_suffix(".prompt.txt")
    sidecar = out.with_suffix(".json")
    prompt_file.write_text(prompt, encoding="utf-8")

    sidecar_data = {
        "source": str(source_path),
        "theme": args.theme,
        "density": args.density,
        "aspect": args.aspect,
        "backend": resolved.name if resolved else None,
        "policy": policy,
        "hash": sha256_text(source),
        "kind": inv.kind,
        "language": inv.language,
        "nodes": [n.label for n in inv.nodes],
        "edges": len(inv.edges),
        "png": str(out),
        "prompt": str(prompt_file),
    }
    sidecar.write_text(json.dumps(sidecar_data, indent=2) + "\n", encoding="utf-8")

    if not resolved:
        print(
            "No image backend on PATH (imagen, grok, or codex). "
            f"Wrote prompt to {prompt_file}.",
            file=sys.stderr,
        )
        return 2

    cmd = argv_for(resolved, str(prompt_file), str(out), args.aspect)
    print(" ".join(cmd))
    if args.dry_run:
        return 0
    try:
        proc = subprocess.run(cmd, check=False)
    except FileNotFoundError:
        print(f"backend binary missing: {resolved.binary}", file=sys.stderr)
        return 2
    if proc.returncode != 0:
        print(f"backend exited {proc.returncode}. Prompt kept at {prompt_file}.", file=sys.stderr)
        return proc.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
