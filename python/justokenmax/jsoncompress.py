"""Structured-output (JSON) compression.

Tool outputs, API responses, and RAG payloads are often huge JSON: pretty-
printed whitespace, arrays with thousands of near-identical elements, giant
embedded strings. This shrinks them while keeping the shape and a representative
sample, so the agent still understands the structure at a fraction of the cost.

Lossy by design (it elides bulk), reversible via the cache (the original is kept
by content hash). Our own code; only the stdlib `json` is used.
"""

from __future__ import annotations

import json
from typing import Tuple

SAMPLE = 3          # keep this many head + tail elements of a long array
MAX_STR = 400       # truncate strings longer than this
MAX_DEPTH = 12      # collapse structure deeper than this


def _shrink(node, depth: int, sample: int, max_str: int, max_depth: int):
    if depth > max_depth:
        return "...(nested structure elided)..."
    if isinstance(node, dict):
        return {k: _shrink(v, depth + 1, sample, max_str, max_depth)
                for k, v in node.items()}
    if isinstance(node, list):
        n = len(node)
        if n > 2 * sample + 1:
            head = [_shrink(x, depth + 1, sample, max_str, max_depth)
                    for x in node[:sample]]
            tail = [_shrink(x, depth + 1, sample, max_str, max_depth)
                    for x in node[-sample:]]
            return head + [f"...({n - 2 * sample} more of {n} items elided)..."] + tail
        return [_shrink(x, depth + 1, sample, max_str, max_depth) for x in node]
    if isinstance(node, str) and len(node) > max_str:
        return node[:max_str] + f"...(+{len(node) - max_str} chars)"
    return node


def looks_like_json(text: str) -> bool:
    s = text.lstrip()
    if not s or s[0] not in "{[":
        return False
    try:
        json.loads(text)
        return True
    except (ValueError, TypeError):
        return False


def compress_json(text: str, sample: int = SAMPLE, max_str: int = MAX_STR,
                  max_depth: int = MAX_DEPTH) -> Tuple[str, dict]:
    """Return (compact_json, stats). If `text` isn't JSON, returns it unchanged."""
    try:
        data = json.loads(text)
    except (ValueError, TypeError):
        return text, {"kind": "json", "ok": False, "note": "not valid JSON"}

    shrunk = _shrink(data, 0, sample, max_str, max_depth)
    # Minify: pretty-printed JSON wastes tokens on whitespace.
    digest = json.dumps(shrunk, separators=(",", ":"), ensure_ascii=False)
    stats = {
        "kind": "json",
        "ok": True,
        "bytes_before": len(text),
        "bytes_after": len(digest),
    }
    return digest, stats
