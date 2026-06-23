---
description: Find a symbol in the code index (file:line + signature) instead of reading files.
argument-hint: <symbol-or-substring>
---

Look up a symbol in the jusTokenMax code index.

Run: `justokenmax query $ARGUMENTS` (fallback `python3 -m justokenmax query
$ARGUMENTS`). Add `--kind func|class|method` to filter.

Each hit is `file:line  [kind]  signature  — docstring`. Use the location to
read just that symbol's range rather than the whole file. If the result says the
index is missing, run `/justokenmax:index` first.
