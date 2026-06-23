---
name: chat-branch
description: Keep the main conversation cheap by offloading heavy sub-tasks to isolated subagent contexts. Use when a sub-task (research sweep, large-file investigation, log triage, broad search) will generate a lot of intermediate output whose conclusion is small — branch it to a subagent so the verbose work never enters the main thread, and merge back only a compact digest.
---

# chat-branch — fork heavy work, merge back the summary (a jusTokenMax module)

Every file read and tool result in the main conversation stays in its context
for the rest of the session, compounding cost. The fix is to *branch*: run
self-contained sub-tasks in a subagent whose context is thrown away afterward,
returning only what matters.

## When to branch

- Research/exploration sweeps ("how does X work across these 12 files?").
- Investigations over large files or logs where you need a conclusion, not the
  raw content.
- Broad searches that surface a lot but resolve to a short answer.
- Any step whose *intermediate* output is large but whose *result* is small.

## How

1. Launch a subagent (Task tool) with a tight, self-contained brief.
2. Tell it to return ONLY a compact digest: the result/decision, relevant
   `file:line` references, and a few lines of summary — never transcripts or
   full file dumps.
3. Integrate just that digest into the main thread. Do not re-read what the
   subagent read; trust its digest (and its cited locations if you need detail).

This is the cheapest big lever: the main conversation grows by a paragraph
instead of by tens of thousands of tokens. Combine with `code-index` (have the
subagent query the index) and `justokenmax` (have it digest logs) for compounding
savings.

The `/justokenmax:branch` command is a shortcut for this pattern.
