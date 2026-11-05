#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from backends import detect_backend  # noqa: E402


def only_clis(table):
    """Patch PATH lookup to `table` and hide any REST API key in the environment."""
    return (
        patch("backends.shutil.which", side_effect=table.get),
        patch("backends._api_available", return_value=False),
    )


class DetectTests(unittest.TestCase):
    def detect(self, table, requested="auto"):
        which, api = only_clis(table)
        with which, api:
            return detect_backend(requested)

    def test_auto_prefers_imagen(self):
        resolved = self.detect({"imagen": "/usr/bin/imagen", "grok-img": "/usr/bin/grok-img"})
        self.assertEqual(resolved.name, "imagen")
        # Changed deliberately: the old default doubled braces, which the
        # imagen CLI reads as a Jinja variable. See DefaultPolicyTests in
        # test_brace_policy.py for the label that breaks under doubling.
        self.assertEqual(resolved.policy, "imagen-cli-bracket")

    def test_auto_falls_to_grok_img(self):
        resolved = self.detect({"grok-img": "/usr/bin/grok-img", "codex": "/usr/bin/codex"})
        self.assertEqual(resolved.name, "grok-img")
        self.assertEqual(resolved.policy, "grok-imagine")

    def test_auto_falls_to_codex(self):
        resolved = self.detect({"codex": "/usr/bin/codex"})
        self.assertEqual(resolved.name, "codex")
        self.assertEqual(resolved.policy, "grok-imagine")

    def test_none_when_missing(self):
        self.assertIsNone(self.detect({}))

    def test_gemini_api_when_key_present(self):
        with patch("backends.shutil.which", return_value=None), patch(
            "backends._api_available", side_effect=lambda name: name == "gemini-api"
        ):
            resolved = detect_backend("auto")
        self.assertEqual(resolved.name, "gemini-api")
        self.assertEqual(resolved.binary, "rest")


if __name__ == "__main__":
    unittest.main()
