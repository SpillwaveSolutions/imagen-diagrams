#!/usr/bin/env python3
"""Backend detection, brace policy, and argv for image workers.

Spillwave portable edition: adds keyed REST backends (gemini-api, xai-api)
so the skill works without installing any image CLI.
"""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

BackendName = Literal["imagen", "gemini-api", "grok-img", "xai-api", "grok-agent", "codex"]
BracePolicy = Literal[
    "imagen-cli-vars",
    "imagen-cli-scan",
    "imagen-cli-bracket",
    "grok-imagine",
]

# The imagen CLI templates its prompt with Jinja, on stdin as well as argv.
# Doubling a brace therefore creates the very failure it is meant to prevent:
# a mermaid label like `skill://{name}` becomes `{{name}}`, which Jinja reads as
# a required variable, and the CLI exits with
# "Missing required variables: name". Doubling only looks safe on labels that
# are not valid identifiers, such as `{Where is your value?}`, which is why the
# bug hides until one diagram uses a single plain word.
#
# Replacing every brace with a bracket is the default because it is the only
# policy no input can defeat. Pairing braces is not enough: mermaid emits
# `{{label}}` natively for a hexagon node, the inner pair matches first, and
# `N{{x}}` becomes `N({x)}`, which still carries a brace. `imagen-scan` and
# `imagen-vars` stay reachable for a caller who wants them.
POLICY_FOR: dict[str, BracePolicy] = {
    "imagen": "imagen-cli-bracket",
    "imagen-scan": "imagen-cli-scan",
    "imagen-vars": "imagen-cli-vars",
    "gemini-api": "grok-imagine",
    "grok-img": "grok-imagine",
    "xai-api": "grok-imagine",
    "grok-agent": "grok-imagine",
    "codex": "grok-imagine",
}

AUTO_ORDER: tuple[BackendName, ...] = (
    "imagen", "gemini-api", "grok-img", "xai-api", "grok-agent", "codex"
)
# Backends whose binary name differs from the backend name.
BINARY_FOR = {"grok-agent": "grok"}
API_BACKENDS = ("gemini-api", "xai-api")


@dataclass
class ResolvedBackend:
    name: BackendName
    policy: BracePolicy
    binary: str


def escape_for_backend(text: str, policy: BracePolicy) -> str:
    """Apply the brace policy for the chosen image worker.

    imagen-cli-bracket  -> rewrite every { and } to [ and ] (default for imagen)
    imagen-cli-vars     -> double every { and } (gemini-imagen template vars)
    imagen-cli-scan     -> rewrite {token} to (token)
    grok-imagine        -> no brace rewrite
    """
    if policy == "imagen-cli-vars":
        return text.replace("{", "{{").replace("}", "}}")
    if policy == "imagen-cli-scan":
        return re.sub(r"\{([^}]*)\}", r"(\1)", text)
    if policy == "imagen-cli-bracket":
        # Unconditional, and that is the point. Any policy that pairs braces
        # leaves a stray one on mermaid's native `{{hexagon}}`: the inner pair
        # matches first and `N{{x}}` becomes `N({x)}`. A bracket cannot begin a
        # Jinja construct, so no input can produce one.
        return text.replace("{", "[").replace("}", "]")
    return text


def detect_backend(requested: str = "auto") -> ResolvedBackend | None:
    """Resolve the first installed backend, retained for API compatibility."""
    found = detect_backends(requested)
    return found[0] if found else None


def _api_available(name: str) -> bool:
    try:
        from api_backends import google_key, xai_key
    except ImportError:  # pragma: no cover - module ships alongside
        return False
    finder = google_key if name == "gemini-api" else xai_key
    return finder()[0] is not None


def _resolve_one(name: str, policy_key: str | None = None) -> ResolvedBackend | None:
    if name in API_BACKENDS:
        if _api_available(name):
            return ResolvedBackend(name, POLICY_FOR[name], "rest")  # type: ignore[arg-type]
        return None
    path = shutil.which(BINARY_FOR.get(name, name))
    if not path:
        return None
    return ResolvedBackend(name, POLICY_FOR[policy_key or name], path)  # type: ignore[arg-type]


REQUEST_CHAINS: dict[str, tuple[tuple[str, str | None], ...]] = {
    "imagen": (("imagen", "imagen"), ("gemini-api", None)),
    "imagen-scan": (("imagen", "imagen-scan"),),
    "imagen-vars": (("imagen", "imagen-vars"),),
    "gemini": (("gemini-api", None),),
    "gemini-api": (("gemini-api", None),),
    "grok": (("grok-img", None), ("xai-api", None), ("grok-agent", None)),
    "grok-agent": (("grok-agent", None),),
    "grok-img": (("grok-img", None),),
    "xai": (("xai-api", None),),
    "xai-api": (("xai-api", None),),
    "codex": (("codex", None),),
}


def detect_backends(requested: str = "auto") -> list[ResolvedBackend]:
    """Resolve all usable candidates in preference order.

    Auto mode returns every usable worker: CLIs on PATH and REST backends whose
    key is configured. A CLI on PATH does not prove it has credentials, so the
    caller fails over to the next candidate after a failed attempt.
    """
    requested = (requested or "auto").strip().lower()
    chain = REQUEST_CHAINS.get(requested)
    if chain is None:
        chain = tuple((name, None) for name in AUTO_ORDER)
    resolved: list[ResolvedBackend] = []
    for name, policy_key in chain:
        found = _resolve_one(name, policy_key)
        if found:
            resolved.append(found)
    return resolved


def argv_for(
    backend: ResolvedBackend,
    prompt_file: str,
    out_file: str,
    aspect: str,
    model: str | None = None,
) -> list[str]:
    """Build the worker command. Prompt is always also on disk at prompt_file.

    imagen (gemini-imagen): positional/stdin prompt, -o, --aspect-ratio, -m
    grok-img: direct xAI image CLI, generated separately via grok_img_argv.
    codex: Codex agent running a prompt from stdin. It uses image_gen when
    the host makes that tool available.
    """
    if backend.name == "imagen":
        cmd = [
            backend.binary,
            "generate",
            "--prompt-file",
            prompt_file,
            "--aspect-ratio",
            aspect,
            "-o",
            out_file,
        ]
        if model:
            cmd.extend(["-m", model])
        return cmd
    cmd: list[str] = [
        backend.binary,
        "exec",
        "--skip-git-repo-check",
        "--ephemeral",
        "--add-dir",
        str(Path(out_file).resolve().parent),
        "-",
    ]
    if model:
        cmd[2:2] = ["--model", model]
    return cmd


def grok_img_argv(
    backend: ResolvedBackend,
    prompt: str,
    output_dir: str,
    aspect: str,
    model: str | None = None,
) -> list[str]:
    """Build the documented grok-img invocation for a single new image."""
    if backend.name != "grok-img":
        raise ValueError("grok_img_argv requires a grok-img backend")
    cmd = [
        backend.binary,
        "generate",
        prompt,
        "--aspect-ratio",
        aspect,
        "--count",
        "1",
        "--output",
        output_dir,
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


def grok_agent_argv(
    backend: ResolvedBackend,
    prompt_file: str,
    cwd: str,
    model: str | None = None,
) -> list[str]:
    """Headless run of the xAI `grok` agent CLI (Grok Build), for hosts with no grok-img.

    Only the image_gen tool is allowed. The agent does not write files or run
    commands. The caller collects the image from the grok session folder.
    """
    if backend.name != "grok-agent":
        raise ValueError("grok_agent_argv requires a grok-agent backend")
    cmd = [
        backend.binary,
        "--prompt-file",
        prompt_file,
        "--allow",
        "image_gen",
        "--output-format",
        "json",
        "--cwd",
        cwd,
    ]
    if model:
        cmd.extend(["--model", model])
    return cmd


def imagen_fallback_argv(
    backend: ResolvedBackend,
    prompt: str,
    out_file: str,
    aspect: str,
    model: str | None = None,
) -> list[str]:
    """gemini-imagen 0.6.x has no --prompt-file. Prompt as argv + -o."""
    cmd = [backend.binary, "generate", prompt, "-o", out_file, "--aspect-ratio", aspect]
    if model:
        cmd.extend(["-m", model])
    return cmd
