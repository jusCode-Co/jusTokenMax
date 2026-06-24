# Features

Every lever is on by default and individually [configurable](Configuration).
All compression is **reversible** (originals cached by content hash; `justokenmax
retrieve`) and tracked in a lifetime ledger (`justokenmax stats`).

## Input compressors

| Lever | What it does | Measured |
| --- | --- | --- |
| **Attachments** | PDF → page-delimited Markdown (drops the per-page image channel); images downscaled ≤1568px + recompressed | −56% on real PDFs |
| **Logs** | strip ANSI, collapse repeats (×N), fold stack traces, keep errors/warnings + head/tail | −99% |
| **JSON / tool output** | sample long arrays, truncate long strings, cap depth, minify | −99% |
| **Notebooks (.ipynb)** | drop base64 image outputs, truncate cell outputs, keep code + markdown | −99% |
| **CSV / tabular** | header + inferred column types + sample rows + row count | −99% |
| **Git diffs** | keep code hunks, collapse lockfile/generated/minified file diffs to one line | lockfile → 1 line |
| **Delta reads** | re-reading a file returns only the diff since the last read | −96% |
| **Redaction** | mask API keys/tokens/passwords, elide base64/data-URIs (tokens **+** safety) | safety + tokens |

## Code navigation

| Lever | What it does | Measured |
| --- | --- | --- |
| **Code index** | symbol map (`file:line` + full signature) — `justokenmax query foo` | −97% to locate a symbol |
| **Outline** | a file's shape (signatures + line numbers, no bodies) — `justokenmax outline f.py` | ~10–20× cheaper than reading |

Deep parsing: Python via `ast` (type-annotated signatures, return types,
decorators, constants); JS/TS/Java via brace-aware scanners (class methods,
interfaces/types/enums, modifiers); Go/Rust/Ruby/C/C++ via regex.

## Output & workflow

- **Terse output** — cut the tokens the agent *writes* (`/justokenmax:terse`).
- **Chat branching** — offload heavy sub-tasks to an isolated subagent, merge a digest.
- **Cache alignment** — keep the prompt KV cache warm.

## Reach

- **MCP server** — `justokenmax_*` tools for any MCP agent.
- **One-command install/uninstall** — Codex, OpenCode, Cursor, Claude.
- **[MCP compression proxy](MCP-Proxy)** — compress any *other* MCP server's output.
- **OpenCode plugin** — transparent read compression (`integrations/opencode/`).
- **Claude Code plugin** — automatic `PreToolUse(Read)` rewrite via `updatedInput`.
