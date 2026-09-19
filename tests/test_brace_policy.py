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


class DefaultPolicyTests(unittest.TestCase):
    """A plain identifier in braces is the case that breaks under doubling.

    `skill://{name}` becomes `{{name}}`, which Jinja reads as a required
    variable, and the imagen CLI exits with "Missing required variables: name".
    A label that is not a valid identifier, such as `{Where is your value?}`,
    survives doubling, which is why the bug hides until one diagram uses a
    single plain word.
    """

    def test_imagen_default_is_scan(self):
        from backends import POLICY_FOR
        self.assertEqual(POLICY_FOR["imagen-scan"], "imagen-cli-scan")

    def test_identifier_label_is_inert_under_default(self):
        out = escape_for_backend("skill://{name}", "imagen-cli-scan")
        self.assertEqual(out, "skill://(name)")
        self.assertNotIn("{{", out)

    def test_vars_policy_still_reachable(self):
        from backends import POLICY_FOR
        self.assertEqual(POLICY_FOR["imagen-vars"], "imagen-cli-vars")


class BracketPolicyTests(unittest.TestCase):
    """Mermaid's hexagon node is what defeats every pairing policy.

    `N{{hexagon}}` has a nested pair. Under `imagen-cli-scan` the inner pair
    matches first, producing `N({hexagon)}`, which still carries a brace and
    still reaches Jinja. Only an unconditional replacement is total.
    """

    CASES = (
        ("skill://{name}", "skill://[name]"),
        ("N{{hexagon label}}", "N[[hexagon label]]"),
        ("J{Decision?}", "J[Decision?]"),
        ('X{{"payload skills=[\'/skills/\']"}', 'X[["payload skills=[\'/skills/\']"]'),
    )

    def test_no_brace_survives(self):
        for src, want in self.CASES:
            with self.subTest(src=src):
                out = escape_for_backend(src, "imagen-cli-bracket")
                self.assertEqual(out, want)
                self.assertNotIn("{", out)
                self.assertNotIn("}", out)

    def test_scan_leaves_a_brace_on_the_hexagon(self):
        # The regression this default exists to prevent.
        out = escape_for_backend("N{{hexagon label}}", "imagen-cli-scan")
        self.assertIn("{", out)

    def test_imagen_default_is_bracket(self):
        from backends import POLICY_FOR
        self.assertEqual(POLICY_FOR["imagen"], "imagen-cli-bracket")
