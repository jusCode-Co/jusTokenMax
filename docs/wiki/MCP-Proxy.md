# MCP Compression Proxy

The universal lever: compress the output of **any** MCP server — not just
jusTokenMax's own tools — for any agent.

```bash
justokenmax proxy -- npx -y some-mcp-server --flag
```

## What it does

It sits between the agent and one downstream MCP server, spawns the downstream
server, forwards every message, and compresses the responses on the way back:

- **`tools/call` results** — large text content blocks are routed through the
  right compressor (JSON / log / diff / generic) and **redacted**.
- **`tools/list`** — verbose tool descriptions are trimmed.
- Everything else passes through untouched.

## Register it as the server

Point your agent's MCP config at the proxy instead of the raw server, e.g.:

```jsonc
{ "mcpServers": {
  "search": { "command": "justokenmax",
              "args": ["proxy", "--", "npx", "-y", "@acme/search-mcp"] }
}}
```

Now every result that server returns is compressed before it reaches the model.

## Notes

- Small content blocks are still **redacted** (secrets masked) but otherwise left
  alone — compression only kicks in above a size threshold.
- Pure, deterministic, stdlib-only; the transform is unit-tested and there's an
  end-to-end test against a fake downstream server.
