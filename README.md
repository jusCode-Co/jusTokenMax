# jusTokenMax

**A token-reduction toolkit for coding agents, packaged as a Claude Code
plugin.** It attacks every avoidable corner of the token budget — the
attachments you feed in, the logs you paste, the files you read, and the
sub-tasks that bloat the thread — and shrinks each one before it costs you.

Ships as a **Python library + `justokenmax` CLI** that does the work, and a **Claude
Code plugin** (hooks, commands, skills) that runs it automatically.

> Built by **Kashi** ([linkedin](https://www.linkedin.com/in/kashiks/)) and
> **Rajan** ([linkedin](https://www.linkedin.com/in/thiyagarajan/)), founders of
> [Kalmantic](https://www.kalmantic.com) — [jusCode.co](https://juscode.co).
> MIT licensed. Public repo — contributions and better benchmarks welcome.

---

## The levers

| Module | Reduces | How | Measured |
| --- | --- | --- | --- |
| **Attachments** | PDFs & images you read | PDF → page-delimited Markdown (drops the per-page image channel); images downscaled ≤1568px + recompressed | **−56%** on real PDFs |
| **Logs** | verbose build/test/CI output | strip ANSI, collapse repeats (`×N`), fold stack traces, keep errors/warnings + head/tail | **−99%** |
| **JSON / tool output** | big structured payloads | sample long arrays, truncate long strings, cap depth, minify whitespace | **−99%** |
| **Notebooks** | `.ipynb` files | drop base64 image outputs, truncate cell outputs, keep code + markdown | **−99%** |
| **CSV / tabular** | large tables | header + inferred column types + sample rows + row count | **−99%** |
| **Delta reads** | re-reading the same file | return only the diff since the last read, not the whole file | **−96%** |
| **Redaction** | secrets & blobs in text | mask API keys/tokens/passwords, elide base64/data-URIs (tokens **+** safety) | safety + tokens |
| **Code index** | reading whole files to find code | symbol map (`file:line` + signature) so you read only the relevant range | **−97%** to locate a symbol |
| **Terse output** | tokens the agent *writes* | output-style steering: lead with answer, fragments, no filler — facts kept exact | output-side |
| **Chat branching** | sub-tasks that bloat the thread | offload heavy work to an isolated subagent context, merge back only a digest | workflow skill |
| **Cache alignment** | recompute on long sessions | keep the prompt prefix stable so the provider KV cache keeps hitting | guidance |

All compression is **reversible** — originals are cached by content hash and
`justokenmax retrieve <artifact>` hands the full version back — and tracked in a
lifetime ledger (`justokenmax stats`). A content **sniffer** routes generic files
(`.txt`/`.out`/no-extension) to the right compressor automatically.

---

## How each lever works

**Attachments.** A PDF is billed as *text + a rendered page-image* (~1,500
tokens/page after the API clamps a page to ≤1.15MP). jusTokenMax extracts the
text to clean Markdown and **drops the image channel** — you keep the words,
stop paying for the picture, and gain something searchable and quotable. Images
are downscaled to the model's resolution ceiling and recompressed (the always-
real win is bytes; the token win lands in base64-inline pipelines).

**Logs.** Build/test/CI output is mostly noise: ANSI codes, progress spam, the
same line hundreds of times, 50-frame stack traces. jusTokenMax digests it —
strips colour, collapses repeated lines into `(×N)`, folds long traces to
first+last frame, and always keeps error/warning lines plus the head and tail.

**Code index.** Reading entire files to find one function is the biggest
avoidable input cost. jusTokenMax parses the repo (Python via `ast`; JS/TS/Go/
Rust/Java/Ruby/C++ via regex) into a symbol map, so `justokenmax query parse_config`
returns `file:line` + signature in a few tokens and you read only that range.

**Chat branching.** Every file read stays in context for the rest of the
session. Branching runs a self-contained sub-task in a subagent whose context is
discarded afterward, returning only a compact digest — the main thread grows by
a paragraph instead of tens of thousands of tokens.

---

## Results

Measured by [`benchmarks/benchmark.py`](benchmarks/benchmark.py). Text is counted
with a real tokenizer (tiktoken / `cl100k`); the PDF "before" uses the page-image
model above at a conservative ~1,500 tokens/page. Full detail (regenerable) in
[`benchmarks/RESULTS.md`](benchmarks/RESULTS.md).

**PDF → Markdown** (real public PDFs)

| Document | Pages | Before | After | Reduction |
| --- | ---: | ---: | ---: | ---: |
| *Attention Is All You Need* (arXiv 1706.03762) | 15 | 37,074 | 14,574 | **−60%** |
| IRS Form W-9 | 6 | 18,305 | 9,305 | **−49%** |
| **Total** | 21 | **55,379** | **23,879** | **−56%** |

**Logs**

| Input | Lines | Tokens before | Tokens after | Reduction |
| --- | ---: | ---: | ---: | ---: |
| representative build log | 4,345 → 21 | 107,668 | 396 | **−99%** |

**JSON / structured output**

| Input | Tokens before | Tokens after | Reduction |
| --- | ---: | ---: | ---: |
| representative API response (2,000-row payload) | 168,023 | 374 | **−99%** |

**Notebook · CSV · delta**

| Input | Tokens before | Tokens after | Reduction |
| --- | ---: | ---: | ---: |
| notebook, 20 cells w/ image outputs | 401,170 | 610 | **−99%** |
| CSV, 5,000 rows | 57,340 | 237 | **−99%** |
| delta re-read, 1 edit in 600 lines | 2,407 | 88 | **−96%** |

**Code index** — cost to locate a symbol, summed over 21 lookups in jusTokenMax's
own source (123 symbols / 21 files):

| Approach | Tokens |
| --- | ---: |
| read each whole file | 16,691 |
| one `justokenmax query` hit each | 486 |
| **reduction** | **−97%** |

**Images** — 3000×2000 → 1568×1045, 186 KB → 107 KB (**−42% bytes**).

Reproduce: `python benchmarks/benchmark.py --fetch`. Numbers vary with content;
drop your own files into `benchmarks/fixtures/`.

---

## Install

The canonical install is the Python package; it provides the `justokenmax` CLI.

**From this repo (works today — Python 3.9+):**

```bash
git clone https://github.com/jusCode-Co/jusTokenMax && cd jusTokenMax
pip install pypdf Pillow            # required codecs
pip install pdfplumber              # optional: better PDF table extraction
pip install ./python                # installs the `justokenmax` CLI (pip dist: justokenmax)
justokenmax --version
```

**From PyPI** (once published): `pip install justokenmax`.

**npm** (optional thin shim — runs `python -m justokenmax`, so it still needs the
Python package above): `npm install -g @kalmantic/justokenmax`.

**As a Claude Code plugin:** add this repo as a plugin. The `Read` hook then
optimizes PDFs / images / logs / JSON / notebooks / CSV automatically, and the
commands, skills, and MCP server become available. The hook calls
`python3 -m justokenmax`, so the Python package must be installed.

## Use

```bash
justokenmax optimize report.pdf shot.png build.log api.json data.csv nb.ipynb  # by type
justokenmax logs ci-output.log                      # compress a verbose log
justokenmax json response.json                      # compress a JSON payload
justokenmax delta src/app.py                        # only what changed since last read
justokenmax redact secrets.txt                      # mask secrets + elide blobs
justokenmax index && justokenmax query parse_config      # build index, find a symbol
justokenmax retrieve <artifact>                     # get the original back (reversible)
justokenmax stats                                   # lifetime token savings
```

### Plugin surface

- **Hook:** `PreToolUse(Read)` transparently rewrites a `Read` of a PDF / image /
  `.log` / JSON / `.ipynb` / CSV to the cheap artifact via `updatedInput`. It
  **never blocks a Read** — any failure falls through untouched.
- **MCP server:** `.mcp.json` launches a stdlib stdio server exposing
  `justokenmax_optimize`, `justokenmax_compress_json`, `justokenmax_compress_log`,
  `justokenmax_query`, `justokenmax_delta`, `justokenmax_redact`, `justokenmax_retrieve`,
  `justokenmax_stats` — so **any** MCP-capable agent can call the compressors.
- **Commands:** `/justokenmax:optimize`, `/justokenmax:logs`, `/justokenmax:index`,
  `/justokenmax:query`, `/justokenmax:delta`, `/justokenmax:redact`, `/justokenmax:retrieve`,
  `/justokenmax:terse`, `/justokenmax:branch`, `/justokenmax:compress-memory`, `/justokenmax:learn`,
  `/justokenmax:stats`.
- **Skills:** `attachments` (PDF/image/log), `code-index` (query-first
  navigation), `chat-branch` (offload sub-tasks), `terse-output` (cut written
  tokens), `cache-align` (keep the prompt cache warm).

```
.claude-plugin/plugin.json   plugin manifest
.mcp.json                    MCP server config (provider-agnostic access)
hooks/                       PreToolUse(Read) hook + config
commands/                    slash commands
skills/                      justokenmax, code-index, chat-branch, terse-output, cache-align
python/                      core library + CLI + MCP server + 57-test suite
node/                        thin npm wrapper over the Python core
benchmarks/                  benchmark harness + RESULTS.md
```

## Relation to headroom / caveman / codegraph

jusTokenMax is inspired by these but built independently. ✅ has it · ⚠️ partial ·
❌ no.

| Capability | jusTokenMax | headroom | caveman | codegraph |
|---|:--:|:--:|:--:|:--:|
| PDF → Markdown (drop page-image channel) | ✅ | ❌ | ❌ | ❌ |
| Image / log / JSON compression | ✅ | ✅ | ❌ | ❌ |
| **Notebook (.ipynb) compression** | ✅ | ❌ | ❌ | ❌ |
| **CSV / tabular sampling** | ✅ | ❌ | ❌ | ❌ |
| **Delta / incremental re-reads** | ✅ | ❌ | ❌ | ❌ |
| **Secret + base64-blob redaction** | ✅ | ❌ | ❌ | ❌ |
| Code symbol index (read symbols not files) | ⚠️ | ❌ | ❌ | ✅ |
| Output-token reduction (terse) | ✅ | ✅ | ✅ | ❌ |
| Chat branching → subagent + digest | ✅ | ⚠️ | ❌ | ❌ |
| Reversible + retrieve original | ✅ | ✅ | ❌ | ❌ |
| Transparent in-place Read rewrite | ✅ | ❌ | ❌ | ⚠️ |
| Content sniffer / auto-route | ✅ | ✅ | ❌ | ❌ |
| MCP server (any agent) | ✅ | ✅ | ⚠️ | ✅ |
| HTTP proxy / wrap / middleware | ❌ | ✅ | ❌ | ❌ |
| Trained compression model | ❌ | ✅ | ❌ | ❌ |
| Cross-agent shared memory | ❌ | ✅ | ❌ | ❌ |
| Zero-dependency / auditable | ✅ | ❌ | ✅ | ⚠️ |
| **Single unified plugin (all levers)** | ✅ | ⚠️ | ❌ | ❌ |

What it **shares**: local-first reversible compression, a stats ledger, terse
output (caveman), MCP access (headroom). What's **distinct to jusTokenMax**:

- **Claude-Code-native transparent rewrite.** The `Read` hook swaps a heavy file
  for its cheap artifact *in place* via `updatedInput`, mid-tool-call — the agent
  reads what it asked for, cheaper, with no proxy and no workflow change.
- **A queryable code symbol index** (codegraph-style): `justokenmax query` returns
  `file:line` + signature so you avoid reading whole files — a different lever
  than compressing code *content*.
- **PDF → Markdown** that eliminates the per-page image channel (not just image
  recompression).
- **Chat-branching as a first-class command** that offloads heavy work to an
  isolated Claude Code subagent and merges back only a digest.
- **Fully transparent, zero-dependency heuristics** — deterministic, auditable,
  no trained model and no network. Every transform is readable Python.

## Limits & honesty

- **No OCR.** Scanned / image-only PDFs have no text layer → empty Markdown;
  jusTokenMax detects no saving and passes the original through.
- **PDF per-page tokens are a conservative model**, not a billed number — treat
  the percentages as well-grounded estimates.
- **Image token savings are base64-pipeline only** (native vision downscales
  regardless); the always-real image win is bytes.
- **The code index is a snapshot**, not live — re-run `justokenmax index` after big
  changes. Non-Python symbols use regex heuristics (good enough to point you,
  not a full parser).

## Safety

Hooks run on untrusted files, so the converters are bounded: PDFs capped at
2,000 pages / ~5M chars of output, Pillow's decompression-bomb guard kept active,
no shell execution, output paths are content-hash names never derived from the
input filename, and the Read hook fails open.

## Test

```bash
cd python && pip install -e . pytest pdfplumber
pytest -q      # 75 tests: pdf, image, log, json, notebook, csv, delta, redact, code-index, optimize, cli, hook, mcp
```

## Roadmap

We'll keep improving: OCR fallback for scans, DOCX/PPTX/HTML inputs, AST-level
code *content* compression, live index refresh, calibrating the per-page token
model against real API counts, a cross-agent shared-memory store, and a learn
loop that mines sessions for durable corrections. PRs welcome.
