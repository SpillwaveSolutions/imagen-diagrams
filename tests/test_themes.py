#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from prompt_builder import load_theme  # noqa: E402


class ThemeTests(unittest.TestCase):
    def test_builtin_themes_load(self):
        for theme_id in ("claude-clay", "manning-print", "agent-control", "arctic-fox"):
            with self.subTest(theme=theme_id):
                theme = load_theme(theme_id)
                self.assertEqual(theme["id"], theme_id)
                self.assertEqual(theme["aspect_default"], "16:9")
                self.assertIn("ink", theme["palette"])
                self.assertIn("primary", theme["palette"])


if __name__ == "__main__":
    unittest.main()
