---
description: Tersely rewrite a memory/context file (CLAUDE.md, notes) to cut its per-session token cost.
argument-hint: <path-to-file>
---

Rewrite the file at **$ARGUMENTS** into a denser form that costs fewer tokens
every session it loads, WITHOUT losing meaning.

Rules:
- Keep all code, commands, paths, URLs, and identifiers byte-for-byte.
- Cut filler, hedging, and repetition. Prefer fragments and bullet lists over
  prose. Merge redundant points.
- Preserve every distinct instruction, fact, and constraint — this is lossless
  on meaning, lossy only on words.
- Show the estimated before→after character/token reduction.

Write the result back to the same file only after showing the diff and getting a
quick confirmation.
