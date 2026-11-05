#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from backends import detect_backend  # noqa: E402


class DetectTests(unittest.TestCase):
    def test_auto_prefers_imagen(self):
        def which(name):
            return {"imagen": "/usr/bin/imagen", "grok": "/usr/bin/grok"}.get(name)

        with patch("backends.shutil.which", side_effect=which):
            resolved = detect_backend("auto")
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.name, "imagen")
        # Changed deliberately: the old default doubled braces, which the
        # imagen CLI reads as a Jinja variable. See DefaultPolicyTests in
        # test_brace_policy.py for the label that breaks under doubling.
        self.assertEqual(resolved.policy, "imagen-cli-bracket")

    def test_auto_falls_to_grok(self):
        def which(name):
            return {"grok": "/usr/bin/grok", "codex": "/usr/bin/codex"}.get(name)

        with patch("backends.shutil.which", side_effect=which):
            resolved = detect_backend("auto")
        self.assertEqual(resolved.name, "grok")
        self.assertEqual(resolved.policy, "grok-imagine")

    def test_auto_falls_to_codex(self):
        def which(name):
            return {"codex": "/usr/bin/codex"}.get(name)

        with patch("backends.shutil.which", side_effect=which):
            resolved = detect_backend("auto")
        self.assertEqual(resolved.name, "codex")
        self.assertEqual(resolved.policy, "grok-imagine")

    def test_none_when_missing(self):
        with patch("backends.shutil.which", return_value=None):
            self.assertIsNone(detect_backend("auto"))


if __name__ == "__main__":
    unittest.main()
