---
name: code-index
description: Find code by symbol name instead of reading whole files. Use when you need to locate a function, class, or method, understand where something is defined, or navigate an unfamiliar repo — query the jusTokenMax code index to get file:line + signature in a few tokens, then read only that range.
---

# code-index — read symbols, not files (a jusTokenMax module)

Reading entire files to find one function is the biggest avoidable input cost in
a coding session. jusTokenMax keeps a lightweight symbol index of the repo so you
can jump straight to a definition.

## Use it query-first

Before grepping or reading files to find where something lives, query the index:

```
justokenmax query parse_config              # substring match on symbol name
justokenmax query Engine --kind class       # filter by kind (func|class|method|...)
justokenmax query render --limit 10
```

Each hit is `file:line  [kind]  signature  — docstring`. Read just that line
range; don't open the whole file.

## Building / refreshing the index

```
justokenmax index            # index the current repo -> .justokenmax/index.json
justokenmax index path/to/repo
```

Python is parsed precisely (via `ast`: functions, classes, methods, signatures,
docstrings); JS/TS/Go/Rust/Java/Ruby/C++ use fast regex heuristics. Re-run
`justokenmax index` after substantial code changes — the index is a snapshot, not
live. If a query says the index is missing, build it first.

Fallback if `justokenmax` isn't on PATH: `python3 -m justokenmax query <term>` /
`python3 -m justokenmax index` with the plugin's `python/` dir on `PYTHONPATH`.

## When NOT to use

For exact-string or regex searches across file *contents* (not symbol names),
plain grep is still right. The index is for "where is this symbol defined?".
