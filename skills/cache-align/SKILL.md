---
name: cache-align
description: Preserve prompt-prefix stability so the provider's KV cache keeps hitting, cutting cost and latency on long sessions. Use when structuring system prompts, memory files, or tool definitions, when a long session is getting expensive, or when deciding where to put changing vs stable content.
---

# cache-align — keep the prompt cache warm (a jusTokenMax module)

Providers cache the KV state of a stable prompt *prefix*; a cache hit is far
cheaper and faster than recomputing it. Any edit near the START of the context
invalidates everything after it. This skill is the discipline that keeps the
prefix stable so the cache keeps paying off.

## Rules of thumb

- **Stable first, volatile last.** Order context most-stable → least-stable:
  system prompt and tool definitions (rarely change) at the top; the live,
  changing task/turn at the bottom. Never inject changing values (timestamps,
  counters, random IDs) into otherwise-static prefixes.
- **Don't churn memory files mid-session.** Edits to CLAUDE.md / system prompt
  bust the cache for the whole session. Batch such edits, or make them between
  sessions, not turn-by-turn.
- **Append, don't rewrite.** Add new context at the end rather than reflowing
  existing text — appends preserve the cached prefix; reflows destroy it.
- **Keep tool definitions fixed.** Reordering or rewording tool/MCP definitions
  invalidates the cache even when behavior is unchanged. Settle them early.
- **Pin volatile data behind a marker.** If you must include changing data, put
  it at the very end, clearly separated, so it can't shift earlier tokens.

## When advising the user

If a long session is getting expensive, check for prefix churn first: a memory
file being rewritten each turn, a timestamp in the system prompt, tool
definitions being regenerated. Fixing prefix stability often saves more than any
single compression.
