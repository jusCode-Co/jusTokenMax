---
description: Get the original file behind an optimized artifact (reverses a jusTokenMax compression).
argument-hint: <optimized-artifact-path>
---

Recover the full original that an optimized artifact was produced from.

Run: `justokenmax retrieve $ARGUMENTS` (fallback `python3 -m justokenmax retrieve
$ARGUMENTS`). It prints the original file path. Read that if you need the
un-compressed content (e.g. a detail the digest/Markdown dropped, or a scanned
PDF the converter couldn't extract).

All jusTokenMax compression is reversible — originals are cached by content hash —
so this never loses data.
