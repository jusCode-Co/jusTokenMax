#!/usr/bin/env python3
"""PreToolUse(Read) hook for justokenmax.

When the agent tries to Read a PDF or an oversized image, we optimize it and
rewrite the Read to point at the cheap artifact (Markdown / compressed image)
via `updatedInput`. The agent reads exactly what it asked for — just at a
fraction of the token cost.

Safety contract: this hook NEVER blocks a Read. Any problem (justokenmax not
installed, parse failure, unsupported file) exits 0 with no output, so the
original Read proceeds untouched.
"""

import json
import os
import sys

# Hook lives at <plugin_root>/hooks/justokenmax_read.py — make the bundled library
# importable without requiring a global install.
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PLUGIN_ROOT, "python"))


def _passthrough():
    """Allow the Read unchanged."""
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        _passthrough()

    if payload.get("tool_name") != "Read":
        _passthrough()

    file_path = (payload.get("tool_input") or {}).get("file_path")
    if not file_path or not os.path.isfile(file_path):
        _passthrough()

    try:
        from justokenmax import optimize
    except Exception:
        # Library/deps not available — degrade silently.
        _passthrough()

    try:
        result = optimize(file_path)
    except Exception:
        _passthrough()

    if not result.ok or not result.output:
        _passthrough()

    saved = result.tokens_saved
    if saved <= 0:
        _passthrough()

    pct = (100 * saved // result.tokens_before) if result.tokens_before else 0
    note = (f"justokenmax: optimized {os.path.basename(file_path)} "
            f"({result.kind}) — reading {os.path.basename(result.output)} "
            f"instead, ~{saved} tokens saved (-{pct}%).")

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow",
            "updatedInput": {**payload["tool_input"], "file_path": result.output},
            "additionalContext": note,
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
