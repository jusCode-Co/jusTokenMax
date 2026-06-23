"""Code index — read symbols, not whole files.

The biggest avoidable input cost in a coding session is reading entire files to
find one function. This builds a lightweight symbol map of the repo so the agent
can ask "where is `parse_config`?" and get `file:line` + signature in a few
tokens, then read only that range.

Our own design: Python is parsed precisely with the stdlib `ast`; other
languages use fast regex heuristics. No heavy parser dependency.
"""

from __future__ import annotations

import ast
import json
import os
import re
from typing import List, Optional

INDEX_DIRNAME = ".justokenmax"
INDEX_FILE = "index.json"

SKIP_DIRS = {
    ".git", ".justokenmax", "node_modules", ".venv", "venv", "__pycache__",
    "dist", "build", ".next", "target", ".pytest_cache", ".mypy_cache",
    "vendor", ".idea", ".vscode",
}

# extension -> language label
LANGS = {
    ".py": "python",
    ".js": "js", ".jsx": "js", ".mjs": "js", ".cjs": "js",
    ".ts": "ts", ".tsx": "ts",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".c": "c", ".h": "c", ".cc": "cpp", ".cpp": "cpp", ".hpp": "cpp",
}

# Regex heuristics for non-Python languages: (kind, pattern with `name` group).
_GENERIC = {
    "js": [
        ("func", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(?P<name>\w+)")),
        ("func", re.compile(r"^\s*(?:export\s+)?const\s+(?P<name>\w+)\s*=\s*(?:async\s*)?\(?.*=>")),
        ("class", re.compile(r"^\s*(?:export\s+)?(?:default\s+)?class\s+(?P<name>\w+)")),
    ],
    "go": [
        ("func", re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?(?P<name>\w+)\s*\(")),
        ("type", re.compile(r"^\s*type\s+(?P<name>\w+)\s+(?:struct|interface)")),
    ],
    "rust": [
        ("fn", re.compile(r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(?P<name>\w+)")),
        ("struct", re.compile(r"^\s*(?:pub\s+)?struct\s+(?P<name>\w+)")),
        ("trait", re.compile(r"^\s*(?:pub\s+)?trait\s+(?P<name>\w+)")),
        ("impl", re.compile(r"^\s*impl(?:<[^>]*>)?\s+(?P<name>\w+)")),
    ],
    "java": [
        ("class", re.compile(r"^\s*(?:public|private|protected|\s)*class\s+(?P<name>\w+)")),
        ("interface", re.compile(r"^\s*(?:public|private|protected|\s)*interface\s+(?P<name>\w+)")),
    ],
    "ruby": [
        ("def", re.compile(r"^\s*def\s+(?P<name>[\w.?!]+)")),
        ("class", re.compile(r"^\s*class\s+(?P<name>\w+)")),
        ("module", re.compile(r"^\s*module\s+(?P<name>\w+)")),
    ],
    "cpp": [("class", re.compile(r"^\s*(?:class|struct)\s+(?P<name>\w+)"))],
    "c": [],
}
_GENERIC["ts"] = _GENERIC["js"] + [
    ("type", re.compile(r"^\s*(?:export\s+)?(?:type|interface)\s+(?P<name>\w+)")),
]


def _iter_source_files(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1].lower()
            if ext in LANGS:
                yield os.path.join(dirpath, fn), LANGS[ext]


def _py_call(node) -> str:
    """`name(arg, arg, *args, **kw)` — no def/class keyword."""
    args = []
    a = node.args
    for arg in a.posonlyargs + a.args:
        args.append(arg.arg)
    if a.vararg:
        args.append("*" + a.vararg.arg)
    for arg in a.kwonlyargs:
        args.append(arg.arg)
    if a.kwarg:
        args.append("**" + a.kwarg.arg)
    return f"{node.name}({', '.join(args)})"


def _index_python(path: str, rel: str) -> List[dict]:
    try:
        tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    except (SyntaxError, ValueError):
        return []
    out = []

    def doc1(node):
        d = ast.get_docstring(node)
        return d.strip().splitlines()[0] if d else ""

    def visit(node, cls=None):
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                call = _py_call(child)
                if cls:
                    sig = f"{cls}.{call}"
                else:
                    prefix = "async def " if isinstance(
                        child, ast.AsyncFunctionDef) else "def "
                    sig = prefix + call
                out.append({
                    "name": child.name, "kind": "method" if cls else "func",
                    "file": rel, "line": child.lineno,
                    "end": getattr(child, "end_lineno", child.lineno),
                    "sig": sig, "doc": doc1(child),
                })
            elif isinstance(child, ast.ClassDef):
                out.append({
                    "name": child.name, "kind": "class", "file": rel,
                    "line": child.lineno,
                    "end": getattr(child, "end_lineno", child.lineno),
                    "sig": f"class {child.name}", "doc": doc1(child),
                })
                visit(child, cls=child.name)

    visit(tree)
    return out


def _index_generic(path: str, rel: str, lang: str) -> List[dict]:
    patterns = _GENERIC.get(lang, [])
    if not patterns:
        return []
    out = []
    try:
        lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return []
    for i, line in enumerate(lines, 1):
        for kind, pat in patterns:
            m = pat.match(line)
            if m:
                out.append({
                    "name": m.group("name"), "kind": kind, "file": rel,
                    "line": i, "end": i, "sig": line.strip()[:120], "doc": "",
                })
                break
    return out


def build_index(root: str) -> dict:
    """Walk `root`, extract symbols, write `.justokenmax/index.json`, return it."""
    root = os.path.abspath(root)
    symbols: List[dict] = []
    n_files = 0
    for path, lang in _iter_source_files(root):
        rel = os.path.relpath(path, root)
        syms = _index_python(path, rel) if lang == "python" \
            else _index_generic(path, rel, lang)
        if syms:
            n_files += 1
            symbols.extend(syms)

    index = {"root": root, "files": n_files, "symbols": symbols}
    out_dir = os.path.join(root, INDEX_DIRNAME)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, INDEX_FILE), "w", encoding="utf-8") as f:
        json.dump(index, f)
    return index


def load_index(root: str) -> Optional[dict]:
    p = os.path.join(os.path.abspath(root), INDEX_DIRNAME, INDEX_FILE)
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return None


def query(root: str, term: str, kind: Optional[str] = None,
          limit: int = 50) -> List[dict]:
    """Return symbols whose name contains `term` (case-insensitive)."""
    index = load_index(root)
    if not index:
        return []
    term_l = term.lower()
    hits = [s for s in index["symbols"]
            if term_l in s["name"].lower() and (not kind or s["kind"] == kind)]
    # exact-name matches first, then by file/line
    hits.sort(key=lambda s: (s["name"].lower() != term_l, s["file"], s["line"]))
    return hits[:limit]


def format_hits(hits: List[dict]) -> str:
    if not hits:
        return "no matches (build the index first with `justokenmax index`)"
    lines = []
    for s in hits:
        loc = f"{s['file']}:{s['line']}"
        doc = f"  — {s['doc']}" if s.get("doc") else ""
        lines.append(f"{loc}  [{s['kind']}]  {s['sig']}{doc}")
    return "\n".join(lines)
