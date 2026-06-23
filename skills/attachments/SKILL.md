---
name: attachments
description: Compress heavy context before it costs tokens. Use when the user attaches or asks to read a PDF, scanned document, screenshot/large image, or a verbose log / build output / CI output — convert PDFs to Markdown, compress oversized images, and digest noisy logs so the same content costs a fraction of the tokens.
---

# attachments — PDF / image / log compression (a jusTokenMax module)

The silent token sinks in a session are the heavy things you feed in: PDFs
(ingested as ~1,500-token page images *per page*), oversized screenshots, and
verbose logs (thousands of near-identical lines). justokenmax turns each into a
cheap, faithful equivalent.

## When to use

- A `.pdf` whose contents are needed → **PDF → page-delimited Markdown**.
- A `.png/.jpg/.jpeg/.webp` over a couple hundred KB → **downscale ≤1568px +
  recompress + strip metadata**.
- A `.log` or pasted build/test/CI output that's long and repetitive →
  **digest**: ANSI stripped, repeated lines collapsed (`×N`), stack traces
  folded, errors/warnings + head/tail kept.

The `Read` hook does the common case automatically — a `Read` on a `.pdf`, large
image, or `.log` is transparently rewritten to read the cheap artifact. Use this
skill for manual/batch runs and to report savings.

## How to run

```
justokenmax optimize spec.pdf screenshot.png build.log   # auto-dispatch by type
justokenmax pdf report.pdf                                # force PDF → Markdown
justokenmax image diagram.png --max-edge 1280             # force image compression
justokenmax logs ci-output.log                            # force log digest
justokenmax stats                                         # lifetime token savings
```

Add `--json` for machine-readable output. If `justokenmax` isn't on PATH, use
`python3 -m justokenmax <args>` with the plugin's `python/` dir on `PYTHONPATH`.

## After optimizing

Read the optimized artifact the command reports (`.md`, `.log.txt`, or the
compressed image), not the original. Everything is cached by content hash, so
re-running on an unchanged file is free and reversible — the original is one
read away.

## Limits

- No OCR: scanned/image-only PDFs have no text layer → empty Markdown; read the
  original instead.
- Tiny images/logs are skipped (already cheap).
