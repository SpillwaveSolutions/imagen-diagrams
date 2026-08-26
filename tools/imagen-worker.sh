#!/bin/sh
# Compatibility shim for hackathon-course tools/imagen-worker.sh callers.
# Forwards to the Python renderer. Brace policy is chosen by backend auto-detect.
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
SCRIPT="$ROOT/skills/imagen-diagrams/scripts/render.py"
exec python3 "$SCRIPT" "$@"
