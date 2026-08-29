#!/usr/bin/env python3
"""Backend detection and brace policy."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from typing import Literal

BackendName = Literal["imagen", "grok", "codex"]
BracePolicy = Literal["imagen-cli-vars", "imagen-cli-scan", "grok-imagine"]

POLICY_FOR: dict[str, BracePolicy] = {
    "imagen": "imagen-cli-vars",
    "imagen-scan": "imagen-cli-scan",
    "grok": "grok-imagine",
    "codex": "grok-imagine",
}

AUTO_ORDER: tuple[BackendName, ...] = ("imagen", "grok", "codex")


@dataclass
class ResolvedBackend:
    name: BackendName
    policy: BracePolicy
    binary: str


def escape_for_backend(text: str, policy: BracePolicy) -> str:
    if policy == "imagen-cli-vars":
        return text.replace("{", "{{").replace("}", "}}")
    if policy == "imagen-cli-scan":
        return re.sub(r"\{([^}]*)\}", r"(\1)", text)
    return text


def detect_backend(requested: str = "auto") -> ResolvedBackend | None:
    requested = (requested or "auto").strip().lower()
    if requested in ("imagen", "imagen-scan"):
        path = shutil.which("imagen")
        if not path:
            return None
        return ResolvedBackend("imagen", POLICY_FOR[requested], path)
    if requested in ("grok", "codex"):
        path = shutil.which(requested)
        if not path:
            return None
        return ResolvedBackend(requested, POLICY_FOR[requested], path)  # type: ignore[arg-type]
    for name in AUTO_ORDER:
        path = shutil.which(name)
        if path:
            return ResolvedBackend(name, POLICY_FOR[name], path)
    return None


def argv_for(
    backend: ResolvedBackend, prompt_file: str, out_file: str, aspect: str
) -> list[str]:
    if backend.name == "imagen":
        # gemini-imagen 0.6.x accepts a prompt as stdin or a positional argument.
        # It does not support the prompt-file flag used by Grok and Codex.
        # render.py pipes the prompt for this branch to avoid putting a long
        # diagram prompt in the process list.
        return [
            backend.binary,
            "generate",
            "--aspect-ratio",
            aspect,
            "-o",
            out_file,
        ]
    if backend.name == "grok":
        return [
            backend.binary,
            "imagine",
            "generate",
            "--prompt-file",
            prompt_file,
            "--aspect",
            aspect,
            "--output",
            out_file,
        ]
    return [
        backend.binary,
        "image",
        "generate",
        "--prompt-file",
        prompt_file,
        "--aspect",
        aspect,
        "--output",
        out_file,
    ]
