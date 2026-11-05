#!/usr/bin/env python3
"""Codex got a Gemini model, and a host with only the grok agent CLI had no grok backend."""
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from backends import ResolvedBackend, argv_for, detect_backends, grok_agent_argv  # noqa: E402
from generate import (  # noqa: E402
    GROK_IMG_DEFAULT_MODEL,
    grok_session_id,
    model_for_backend,
    newest_grok_image,
    save_as_png,
)


class ModelRoutingTests(unittest.TestCase):
    def test_gemini_alias_never_reaches_codex(self):
        self.assertIsNone(model_for_backend("codex", "nano-banana-pro", "cover"))
        backend = ResolvedBackend("codex", "grok-imagine", "/usr/bin/codex")
        argv = argv_for(backend, "p.txt", "out/fig.png", "4:3", model=None)
        self.assertNotIn("--model", argv)

    def test_codex_keeps_its_own_model(self):
        self.assertEqual(model_for_backend("codex", "gpt-5.5"), "gpt-5.5")

    def test_google_backends_resolve_alias(self):
        self.assertEqual(model_for_backend("gemini-api", "nano-banana-pro"), "gemini-3-pro-image")
        self.assertEqual(model_for_backend("imagen", None, "cover"), "gemini-3-pro-image")

    def test_xai_backends_fall_back_to_grok_imagine(self):
        self.assertEqual(model_for_backend("grok-img", "nano-banana-pro"), GROK_IMG_DEFAULT_MODEL)
        self.assertEqual(model_for_backend("xai-api", "gemini-3-pro-image"), GROK_IMG_DEFAULT_MODEL)

    def test_grok_agent_drops_gemini_id(self):
        self.assertIsNone(model_for_backend("grok-agent", "gemini-3-pro-image-preview"))
        self.assertEqual(model_for_backend("grok-agent", "grok-4.7"), "grok-4.7")


class GrokAgentTests(unittest.TestCase):
    def test_detected_from_grok_binary(self):
        with patch("backends.shutil.which", side_effect={"grok": "/opt/grok"}.get), patch(
            "backends._api_available", return_value=False
        ):
            found = detect_backends("auto")
        self.assertEqual([(b.name, b.binary) for b in found], [("grok-agent", "/opt/grok")])

    def test_argv_allows_only_image_gen(self):
        backend = ResolvedBackend("grok-agent", "grok-imagine", "/opt/grok")
        argv = grok_agent_argv(backend, "p.txt", "/work", model=None)
        self.assertEqual(argv[argv.index("--allow") + 1], "image_gen")
        self.assertNotIn("--always-approve", argv)
        self.assertNotIn("--permission-mode", argv)
        self.assertNotIn("--model", argv)

    def test_collects_newest_session_image(self):
        stdout = '{"stopReason": "end_turn", "sessionId": "abc-123", "cwd": "/work"}'
        self.assertEqual(grok_session_id(stdout), "abc-123")
        self.assertIsNone(grok_session_id("not json"))
        with tempfile.TemporaryDirectory() as tmp:
            images = Path(tmp) / "%2Fwork" / "abc-123" / "images"
            images.mkdir(parents=True)
            old, new = images / "1.png", images / "2.png"
            old.write_bytes(b"old")
            new.write_bytes(b"new")
            past = time.time() - 60
            os.utime(old, (past, past))
            (images / "notes.txt").write_text("skip")
            found = newest_grok_image("abc-123", root=Path(tmp))
            self.assertEqual(found, new)
            out = Path(tmp) / "fig.png"
            self.assertTrue(save_as_png(found, out))
            self.assertEqual(out.read_bytes(), b"new")
            self.assertIsNone(newest_grok_image("other", root=Path(tmp)))


if __name__ == "__main__":
    unittest.main()
