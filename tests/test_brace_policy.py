#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from backends import escape_for_backend  # noqa: E402
from prompt_builder import build_layout_hints_prompt  # noqa: E402


class BracePolicyTests(unittest.TestCase):
    def test_vars_doubles_decision_node(self):
        src = "flowchart LR\n  A[Start] --> J{Decision?}\n"
        out = escape_for_backend(src, "imagen-cli-vars")
        self.assertIn("{{Decision?}}", out)
        self.assertNotIn("{Decision?}", out.replace("{{Decision?}}", ""))

    def test_scan_rewrites_to_parens(self):
        src = "flowchart LR\n  A[Start] --> J{Decision?}\n"
        out = escape_for_backend(src, "imagen-cli-scan")
        self.assertIn("(Decision?)", out)
        self.assertNotIn("{Decision?}", out)

    def test_grok_keeps_braces(self):
        src = "flowchart LR\n  A[Start] --> J{Decision?}\n"
        out = escape_for_backend(src, "grok-imagine")
        self.assertIn("{Decision?}", out)
        self.assertNotIn("{{Decision?}}", out)

    def test_prompt_builder_applies_policy(self):
        src = Path(__file__).parent / "fixtures" / "flowchart.mmd"
        text = src.read_text(encoding="utf-8")
        prompt = build_layout_hints_prompt(
            source=text,
            topic="imagen-diagrams",
            theme_id="claude-clay",
            density="slide",
            policy="imagen-cli-vars",
        )
        self.assertIn("{{Fidelity judge}}", prompt)
        self.assertIn("FRAMING", prompt)
        self.assertIn("PALETTE", prompt)
        self.assertIn("finished diagram", prompt)


if __name__ == "__main__":
    unittest.main()
