---
description: Optimize attachments or logs (PDF→Markdown, image compression, log digest) to cut token cost.
argument-hint: <path> [more paths...]
---

Run justokenmax on the given file(s) and report token savings.

1. Run: `justokenmax optimize --json $ARGUMENTS`
   (Fallback if `justokenmax` isn't on PATH: `python3 -m justokenmax optimize --json
   $ARGUMENTS` from the plugin's `python/` directory.)
2. Parse the JSON. For each file report: optimized output path, tokens
   before→after, percent saved, cache-hit or not.
3. If you need the content, read the optimized output (`.md` for PDFs,
   `.log.txt` for logs, the compressed image) — not the original.

Handles `.pdf`, images/screenshots, and `.log` files automatically. The Read
hook already does this transparently for files you Read; use this for explicit
or batch runs.
