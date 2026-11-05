#!/usr/bin/env python3
"""Render diagram source to a themed PNG via the shared image engine.

Backend order (auto): imagen CLI, gemini-api (REST), grok-img CLI, xai-api
(REST), codex. Each failed attempt falls through to the next. With no usable
backend, the layout-hints prompt is still written and the script exits 2 so
the agent can take the code-drawn SVG path.

Exit codes: 0 ok, 2 no backend, 3 Salt wireframe, 4 worker produced nothing,
5 network blocked.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from generate import generate_image  # noqa: E402
from inventory import inventory_from_source  # noqa: E402
from prompt_builder import build_layout_hints_prompt, load_theme  # noqa: E402

DEFAULT_DIAGRAM_MODEL = "nano-banana-pro"  # best in-image text; labels are the point


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def project_config(start: Path) -> dict:
    """Read the nearest .imagen-diagrams/config.yaml or .imagen-diagrams.yaml."""
    try:
        import yaml  # type: ignore
    except ImportError:
        return {}
    for folder in [start, *start.parents]:
        for candidate in (folder / ".imagen-diagrams" / "config.yaml", folder / ".imagen-diagrams.yaml"):
            if candidate.is_file():
                try:
                    return yaml.safe_load(candidate.read_text(encoding="utf-8")) or {}
                except Exception:
                    return {}
    return {}


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
    p.add_argument("--theme")
    p.add_argument("--density", choices=("slide", "article"), default="slide")
    p.add_argument("--backend", default=None, help="auto|imagen|gemini|grok|xai|codex|imagen-scan")
    p.add_argument("--model", default=None, help=f"default {DEFAULT_DIAGRAM_MODEL}")
    p.add_argument("--aspect")
    p.add_argument("--output-dir")
    p.add_argument("--feedback", help="REGENERATION FEEDBACK text to prepend on a retry")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    source_path = Path(args.source)
    source = source_path.read_text(encoding="utf-8")
    cfg = project_config(source_path.resolve().parent)

    inv = inventory_from_source(source)
    if inv.salt:
        print(
            "Salt wireframe detected. Skip image generation. Use the plantuml skill.",
            file=sys.stderr,
        )
        return 3

    theme = args.theme or cfg.get("theme") or "claude-clay"
    aspect = args.aspect or cfg.get("aspect") or ("16:9" if args.density == "slide" else "4:3")
    requested = args.backend or cfg.get("backend") or "auto"
    model = args.model or cfg.get("model") or DEFAULT_DIAGRAM_MODEL
    output_dir = args.output_dir or cfg.get("output_dir")

    load_theme(theme)
    prompt = build_layout_hints_prompt(
        source=source,
        topic=args.topic,
        theme_id=theme,
        density=args.density,
        policy="grok-imagine",  # raw text; the engine escapes per backend
    )
    if args.feedback:
        prompt = f"REGENERATION FEEDBACK: {args.feedback.strip()}\n\n{prompt}"

    out = default_output(source_path, Path(output_dir) if output_dir else None)
    extra = {
        "source": str(source_path),
        "theme": theme,
        "density": args.density,
        "hash": sha256_text(source),
        "kind_of_diagram": inv.kind,
        "language": inv.language,
        "nodes": [n.label for n in inv.nodes],
        "edges": len(inv.edges),
    }
    code = generate_image(
        prompt,
        out,
        kind="cover",  # routes Google backends to Nano Banana Pro unless --model says otherwise
        aspect=aspect,
        requested=requested,
        model_arg=model,
        dry_run=args.dry_run,
        engine_hint=requested,
        extra_sidecar=extra,
    )
    if code == 2:
        print(
            "No image backend. Next: draw the figure as a themed SVG by hand "
            "(see SKILL.md 'Code-drawn SVG path') and gate it with to_svg.py.",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    sys.exit(main())
