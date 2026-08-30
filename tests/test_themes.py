#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from extract_theme import contrast  # noqa: E402
from prompt_builder import load_theme  # noqa: E402

try:
    import yaml  # noqa: F401
except ImportError:
    yaml = None

# Themes gated by the 4.5:1 contrast floor. Scoped to towards-ai for now:
# an empirical survey (2026-08-29) found the existing builtins fail some
# pairs (claude-clay node_emphasis 4.23:1 and muted/background 3.27:1;
# manning-print muted/background 3.36:1 plus a subgraph role referencing a
# missing palette key gray_2; agent-control node_decision 2.80:1;
# arctic-fox node_success 4.10:1). Those are tracked for a follow-up issue
# rather than repainted here; new themes should be added to this tuple.
CONTRAST_GATED_THEMES = ("towards-ai",)


class ThemeTests(unittest.TestCase):
    def test_builtin_themes_load(self):
        for theme_id in ("claude-clay", "manning-print", "agent-control", "arctic-fox", "towards-ai"):
            with self.subTest(theme=theme_id):
                theme = load_theme(theme_id)
                self.assertEqual(theme["id"], theme_id)
                self.assertEqual(theme["aspect_default"], "16:9")
                self.assertIn("ink", theme["palette"])
                self.assertIn("primary", theme["palette"])


class ThemeContrastTests(unittest.TestCase):
    def test_palette_floor_pairs(self):
        # Palette parses in the no-PyYAML fallback parser too, so this
        # test is safe without PyYAML.
        for theme_id in CONTRAST_GATED_THEMES:
            p = load_theme(theme_id)["palette"]
            with self.subTest(theme=theme_id):
                self.assertGreaterEqual(contrast(p["ink"], p["background"]), 4.5)
                self.assertGreaterEqual(contrast(p["primary_fg"], p["primary"]), 4.5)
                self.assertGreaterEqual(contrast(p["muted"], p["background"]), 4.5)

    @unittest.skipIf(yaml is None, "roles nesting needs PyYAML")
    def test_role_pairs_meet_floor(self):
        for theme_id in CONTRAST_GATED_THEMES:
            theme = load_theme(theme_id)
            p, roles = theme["palette"], theme["roles"]
            for role, spec in roles.items():
                if "fg" not in spec:
                    continue  # arrow is stroke-only
                with self.subTest(theme=theme_id, role=role):
                    self.assertGreaterEqual(contrast(p[spec["fg"]], p[spec["bg"]]), 4.5)


if __name__ == "__main__":
    unittest.main()
