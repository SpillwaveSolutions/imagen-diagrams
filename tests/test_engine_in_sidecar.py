#!/usr/bin/env python3
"""The sidecar named imagen when the imagen CLI handed the drawing to codex."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

import generate  # noqa: E402
from backends import ResolvedBackend  # noqa: E402

IMAGEN = ResolvedBackend("imagen", "imagen-cli-bracket", "/usr/bin/imagen")


def fake_run(stdout):
    """A subprocess.run stand-in that writes the -o file and prints stdout."""
    def run(cmd, **kwargs):
        if "-o" in cmd:
            Path(cmd[cmd.index("-o") + 1]).write_bytes(b"png")
        return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")
    return run


class EngineInSidecarTests(unittest.TestCase):
    def render(self, backend, stdout):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fig.png"
            with patch.object(generate, "detect_backends", return_value=[backend]), \
                 patch.object(generate, "imagen_supports_prompt_file", return_value=True), \
                 patch.object(generate.subprocess, "run", side_effect=fake_run(stdout)), \
                 patch("sys.stdout"):
                code = generate.generate_image("a diagram", out)
            self.assertEqual(code, 0)
            return json.loads(out.with_suffix(".json").read_text())

    def test_imagen_cli_handoff_to_codex_is_recorded(self):
        data = self.render(IMAGEN, "imagen: generated via codex -> fig.png\n")
        self.assertEqual(data["backend"], "imagen")
        self.assertEqual(data["engine"], "codex")
        self.assertEqual(data["attempts"][-1]["engine"], "codex")

    def test_imagen_drawing_itself_is_imagen(self):
        data = self.render(IMAGEN, "saved fig.png\n")
        self.assertEqual(data["engine"], "imagen")

    def test_engine_names_map_to_three_families(self):
        self.assertEqual(generate.engine_from_imagen_output("imagen: generated via grok-imagine -> x.png"), "grok")
        self.assertEqual(generate.engine_from_imagen_output("imagen: generated via gemini -> x.png"), "imagen")
        self.assertIsNone(generate.engine_from_imagen_output("wrote x.png"))
        self.assertEqual(generate.ENGINE_FOR["grok-agent"], "grok")
        self.assertEqual(generate.ENGINE_FOR["gemini-api"], "imagen")


if __name__ == "__main__":
    unittest.main()
