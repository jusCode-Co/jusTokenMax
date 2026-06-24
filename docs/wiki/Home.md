# jusTokenMax Wiki

**Token-reduction toolkit for Claude Code, OpenCode & other coding harnesses.**
Keep your coding agent under a token (and cost) budget — jusTokenMax shrinks every
expensive input before it reaches the model's context.

- Repo: https://github.com/Kalmantic/jusTokenMax
- License: MIT · Sponsor: https://github.com/sponsors/Kashi-KS

## Start here

- **[Installation](Installation)** — pip, npm, or Node-only (no Python).
- **[Try It in 5 Minutes](Try-It)** — copy-paste, savings on vs off.
- **[Features](Features)** — every lever, what it does, measured reductions.
- **[Configuration](Configuration)** — turn levers on/off your way.
- **[Cross-Agent Setup](Cross-Agent-Setup)** — Codex, OpenCode, Cursor, Claude.
- **[MCP Compression Proxy](MCP-Proxy)** — compress *any* MCP server's output.
- **[FAQ](FAQ)** — including "why text extraction, not image parsing?"

## In one line

| What you feed it | Typical reduction |
| --- | ---: |
| PDF spec / paper | −56% (real PDFs) |
| Verbose build/CI log | −99% |
| Large JSON / API response | −99% |
| Jupyter notebook | −99% |
| CSV (thousands of rows) | −99% |
| Git diff (lockfile churn) | lockfile → 1 line |
| Finding a symbol vs reading the file | −97% |

Zero dependencies, deterministic, fully auditable, reversible, with built-in
secret redaction — equally at home for a solo dev and a regulated enterprise.
