---
description: Build the jusTokenMax code symbol index for this repo.
argument-hint: [path]
---

Build the symbol index so you can look up code by name instead of reading whole
files.

Run: `justokenmax index $ARGUMENTS` (defaults to the current directory; fallback
`python3 -m justokenmax index $ARGUMENTS`).

Report how many symbols across how many files were indexed. After this, use
`/justokenmax:query <name>` (or `justokenmax query <name>`) to locate any function, class,
or method as `file:line` + signature, then read only that range.
