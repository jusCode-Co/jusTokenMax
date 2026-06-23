---
description: Branch a self-contained sub-task into an isolated subagent context to keep the main thread cheap.
argument-hint: <task description>
---

Offload the following sub-task so its verbose work never enters this
conversation's token budget: **$ARGUMENTS**

Do this:
1. Launch a subagent (Task tool) with a tight, self-contained brief for the
   sub-task. All of its file reads, tool output, and reasoning stay in ITS
   context window, not ours.
2. Instruct the subagent to return only a compact digest: the decision/result,
   any file:line references, and a 3–8 line summary — not transcripts or full
   file dumps.
3. When it returns, integrate just that digest here. Do not re-read everything
   it read.

Use this for research sweeps, large-file investigations, log triage, or any
exploration whose intermediate output is large but whose conclusion is small.
This is the "branch the chat" pattern: fork the heavy work, merge back only the
summary.
