# Backends and brace policy

## Auto order

1. `imagen` if on PATH. Policy `imagen-cli-vars`.
2. Else `grok` if on PATH. Policy `grok-imagine`.
3. Else `codex` if on PATH. Policy `grok-imagine`.
4. Else fail closed. Write `<stem>_imagen.prompt.txt` and exit 2.

Pin with `.imagen-diagrams/config.yaml`:

```yaml
backend: auto    # auto | imagen | grok | codex | imagen-scan
```

`imagen-scan` rewrites `{token}` to `(token)` for binaries that still scan the inner token.

## Policies

```text
imagen-cli-vars     -> double every { and }
imagen-cli-scan     -> rewrite {token} to (token)
grok-imagine        -> no brace rewrite
```

A `{Decision?}` node must not crash either adapter. Tests live in `tests/test_brace_policy.py`.

## Why this exists

The course copy doubles braces because Imagen treats a single brace as a variable placeholder. The book copy rewrites braces to parentheses because its binary still scans the inner token. Copying the wrong escape is the first merge bug.
