"""Jupyter notebook (.ipynb) compression.

Notebooks are token bombs: a single cell output can carry a megabyte of base64
PNG, and re-run logs pile up. This keeps what the agent actually needs — the
code and markdown — and reduces outputs to short summaries (images elided, long
text/streams truncated). Output is plain Markdown, far cheaper than the raw
notebook JSON.

Our own code; stdlib `json` only.
"""

from __future__ import annotations

import json
from typing import Tuple


def _join(src) -> str:
    if isinstance(src, list):
        return "".join(src)
    return src or ""


def _truncate(text: str, max_lines: int = 10, max_chars: int = 300) -> str:
    lines = text.splitlines()
    if len(lines) <= max_lines:
        flat = " ⏎ ".join(ln for ln in lines if ln.strip())
        return flat[:max_chars]
    head = " ⏎ ".join(lines[:max_lines])
    return head[:max_chars] + f" …(+{len(lines) - max_lines} more lines)"


def _summarize_output(o: dict) -> str:
    otype = o.get("output_type")
    data = o.get("data", {})
    if any(k.startswith("image/") for k in data):
        return "[image output elided]"
    if otype == "stream":
        return _truncate(_join(o.get("text", "")))
    if otype == "error":
        return f"ERROR {o.get('ename', '')}: {o.get('evalue', '')}".strip()
    if "text/plain" in data:
        return _truncate(_join(data["text/plain"]))
    if "text/html" in data:
        return "[html output elided]"
    return ""


def notebook_to_markdown(text: str) -> Tuple[str, dict]:
    """Return (markdown, stats). If `text` isn't a notebook, returns it as-is."""
    try:
        nb = json.loads(text)
    except (ValueError, TypeError):
        return text, {"kind": "notebook", "ok": False, "note": "not a notebook"}
    if not isinstance(nb, dict) or "cells" not in nb:
        return text, {"kind": "notebook", "ok": False, "note": "no cells"}

    out, images, n_out = [], 0, 0
    for i, cell in enumerate(nb.get("cells", []), 1):
        ctype = cell.get("cell_type", "code")
        src = _join(cell.get("source", "")).rstrip()
        out.append(f"## Cell {i} [{ctype}]")
        if src:
            out.append("```\n" + src + "\n```" if ctype == "code" else src)
        for o in cell.get("outputs", []) or []:
            summary = _summarize_output(o)
            if summary:
                n_out += 1
                if summary == "[image output elided]":
                    images += 1
                out.append(f"_output:_ {summary}")
        out.append("")

    md = "\n".join(out).strip() + "\n"
    stats = {"kind": "notebook", "ok": True,
             "cells": len(nb.get("cells", [])),
             "images_elided": images, "outputs": n_out}
    return md, stats
