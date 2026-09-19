#!/usr/bin/env python3
"""The framing block names a topic. Without an explicit ban, the model is
liable to render that topic as a heading across the top of the image.

That is not hypothetical. A published course guide shipped 16 diagrams titled
"Claude Code" because the framing named a topic and nothing forbade a title.
The mermaid source names nodes, never the diagram, so any title is invented.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from prompt_builder import build_layout_hints_prompt  # noqa: E402

SOURCE = "flowchart TB\n    A[Listen on port 8088] --> B[Return 200 OK]\n"


def prompt_for(theme_id: str = "claude-clay", density: str = "slide") -> str:
    return build_layout_hints_prompt(
        source=SOURCE,
        topic="Microsoft Foundry hosted agents",
        theme_id=theme_id,
        density=density,
        policy="imagen-cli-scan",
    )


class NoInventedTitleTests(unittest.TestCase):
    def test_negative_list_bans_a_title(self):
        prompt = prompt_for()
        lowered = prompt.lower()
        for banned in ("title", "heading", "caption", "banner"):
            self.assertIn(banned, lowered, f"negative list must name {banned!r}")

    def test_ban_survives_every_theme(self):
        themes = Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/themes"
        ids = sorted(p.stem for p in themes.glob("*.yaml"))
        self.assertTrue(ids, "expected built-in themes")
        for theme_id in ids:
            with self.subTest(theme=theme_id):
                self.assertIn("Do not add a title", prompt_for(theme_id=theme_id))

    def test_ban_survives_both_densities(self):
        for density in ("slide", "article"):
            with self.subTest(density=density):
                self.assertIn("Do not add a title", prompt_for(density=density))

    def test_topic_still_reaches_the_framing(self):
        # The ban must not remove the topic; the framing needs it for context.
        self.assertIn("Microsoft Foundry hosted agents", prompt_for())


if __name__ == "__main__":
    unittest.main()
