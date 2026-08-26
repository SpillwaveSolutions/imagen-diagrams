#!/usr/bin/env python3
"""Extract a theme YAML from a URL or list built-in themes."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

THEMES_DIR = Path(__file__).resolve().parent.parent / "themes"

HEX = re.compile(r"#(?:[0-9a-fA-F]{6})")
CSS_VAR = re.compile(
    r"--(?:color-)?([a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})", re.I
)


def srgb(c: float) -> float:
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return 0.2126 * srgb(r) + 0.7152 * srgb(g) + 0.0722 * srgb(b)


def contrast(a: str, b: str) -> float:
    l1, l2 = luminance(a), luminance(b)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def darken(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    rgb = [max(0, int(int(h[i : i + 2], 16) * 0.7)) for i in (0, 2, 4)]
    return "#" + "".join(f"{v:02X}" for v in rgb)


def lighten(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    rgb = [min(255, int(int(h[i : i + 2], 16) + (255 - int(h[i : i + 2], 16)) * 0.4)) for i in (0, 2, 4)]
    return "#" + "".join(f"{v:02X}" for v in rgb)


def enforce_pair(bg: str, fg: str) -> tuple[str, str]:
    pair = (bg, fg)
    for _ in range(8):
        if contrast(pair[0], pair[1]) >= 4.5:
            return pair
        pair = (lighten(pair[0]), darken(pair[1]))
    return pair


def list_themes() -> None:
    for path in sorted(THEMES_DIR.glob("*.yaml")):
        print(path.stem)


def extract_from_url(url: str) -> dict[str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "imagen-diagrams/0.1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    named = {k.lower(): v.upper() for k, v in CSS_VAR.findall(html)}
    hexes = [h.upper() for h in HEX.findall(html)]
    bg = named.get("background") or named.get("bg") or named.get("paper") or (hexes[0] if hexes else "#F2EFE6")
    ink = named.get("ink") or named.get("fg") or named.get("text") or "#221E18"
    primary = named.get("primary") or named.get("accent") or named.get("brand") or (hexes[1] if len(hexes) > 1 else "#C15F3C")
    surface = named.get("surface") or lighten(bg)
    accent = named.get("accent") or (hexes[2] if len(hexes) > 2 else "#F0D584")
    bg, ink = enforce_pair(bg, ink)
    return {
        "background": bg,
        "surface": surface,
        "primary": primary,
        "primary_fg": "#FFFFFF",
        "accent": accent,
        "accent_2": named.get("accent-2") or named.get("lilac") or "#E2D8F0",
        "success": named.get("success") or named.get("sage") or "#B6C9A8",
        "ink": ink,
        "muted": named.get("muted") or "#8A8376",
    }


def write_theme(slug: str, palette: dict[str, str], source_kind: str, ref: str) -> Path:
    out = THEMES_DIR / "extracted" / f"{slug}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"id: {slug}",
        f"name: {slug}",
        "version: 1",
        "source:",
        f"  kind: {source_kind}",
        f"  ref: {ref}",
        'aspect_default: "16:9"',
        "style:",
        "  summary: Extracted theme. Clean minimalist technical illustration.",
        "  label_min_px: 24",
        "  arrow_px: [2, 3]",
        "  text_orientation: horizontal",
        "  contrast_min: 4.5",
        "palette:",
    ]
    for k, v in palette.items():
        lines.append(f'  {k}: "{v}"')
    lines += [
        "roles:",
        "  title: { bg: surface, fg: ink }",
        "  node_default: { bg: surface, fg: ink }",
        "  node_emphasis: { bg: primary, fg: primary_fg }",
        "  node_success: { bg: success, fg: ink }",
        "  node_decision: { bg: accent, fg: ink }",
        "  subgraph: { bg: accent_2, fg: ink }",
        "  arrow: { stroke: ink }",
        "negatives:",
        "  - mermaid or plantuml source syntax",
        "  - ASCII art",
        "  - tiny labels",
        "  - watermarks or logos",
        "  - node IDs as visible labels",
        "svg:",
        "  label_px: [18, 26]",
        "  max_kb: 30",
        "  max_kb_small: 15",
        "  small_node_threshold: 8",
        "",
    ]
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--url")
    p.add_argument("--image", help="Path to a screenshot. Writes a stub for model-assisted mapping.")
    p.add_argument("--slug")
    args = p.parse_args()
    if not args.url and not args.image:
        list_themes()
        return 0
    if args.image:
        print(
            "Image extract is model-assisted in v0.1.0. Sample the image, map onto schema roles, "
            "enforce contrast at least 4.5:1, and write YAML under themes/extracted/.",
            file=sys.stderr,
        )
        return 4
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", args.url.split("//", 1)[-1])[:40].strip("-")
    palette = extract_from_url(args.url)
    path = write_theme(slug, palette, "url", args.url)
    print(path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
