#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "skills/imagen-diagrams/scripts"))

from backends import ResolvedBackend, argv_for  # noqa: E402


class BackendArgvTests(unittest.TestCase):
    def test_imagen_uses_stdin_compatible_flags(self):
        backend = ResolvedBackend("imagen", "imagen-cli-vars", "/usr/bin/imagen")
        argv = argv_for(backend, "prompt.txt", "figure.png", "16:9")
        self.assertEqual(
            argv,
            [
                "/usr/bin/imagen",
                "generate",
                "--aspect-ratio",
                "16:9",
                "-o",
                "figure.png",
            ],
        )
        self.assertNotIn("--prompt-file", argv)


if __name__ == "__main__":
    unittest.main()
