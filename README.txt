==============================================================================
 jusTokenMax - a token-reduction toolkit for coding agents (Claude Code plugin)
==============================================================================

jusTokenMax attacks every avoidable corner of the token budget - the attachments
you feed in, the logs you paste, the files you read, and the sub-tasks that
bloat the thread - and shrinks each one before it costs you.

Ships as a Python library + `justokenmax` CLI that does the work, and a Claude Code
plugin (hooks, commands, skills) that runs it automatically.

Built by Kashi (https://www.linkedin.com/in/kashiks/) and
Rajan (https://www.linkedin.com/in/thiyagarajan/), founders of
Kalmantic (https://www.kalmantic.com) - jusCode.co. MIT licensed.
Public repo - contributions and better benchmarks welcome.


THE LEVERS
------------------------------------------------------------------------------
1. Attachments  - PDFs you read are billed as text + a per-page image (~1,500
   tokens/page). jusTokenMax extracts the text to Markdown and drops the image
   channel. Images are downscaled <=1568px and recompressed.
   Measured: -56% on real public PDFs.

2. Logs         - strip ANSI, collapse repeated lines into (xN), fold long stack
   traces, keep error/warning lines + head/tail.
   Measured: -99% (107,668 -> 396 tokens on a representative build log).

3. JSON / tool output - sample long arrays, truncate long strings, cap depth,
   minify whitespace.
   Measured: -99% (168,023 -> 374 tokens on a 2,000-row API response).

4. Code index   - symbol map (file:line + signature) so you read only the
   relevant range. Python via stdlib ast; JS/TS/Go/Rust/Java/Ruby/C++ via regex.
   Measured: -97% to locate a symbol (16,691 -> 486 tokens over 21 lookups).

5. Terse output - cut the tokens the agent WRITES: lead with the answer,
   fragments, no filler, facts kept exact. (/justokenmax:terse + terse-output skill.)

6. Chat branching - offload heavy sub-tasks to an isolated subagent context and
   merge back a digest. (/justokenmax:branch + chat-branch skill.)

7. Cache alignment - keep the prompt prefix stable so the provider KV cache keeps
   hitting. (cache-align skill.)

8. Notebook (.ipynb) - strip base64 image outputs, truncate cell outputs, keep
   code + markdown. Measured: -99% (401,170 -> 610 tokens).

9. CSV / tabular - huge table -> header + inferred column types + sample rows +
   row count. Measured: -99% (57,340 -> 237 tokens on 5,000 rows).

10. Delta reads - re-reading a file returns only the diff since the last read,
    not the whole file. Measured: -96% (2,407 -> 88 tokens, 1 edit in 600 lines).

11. Redaction - strip base64 blobs/data-URIs and mask secrets (API keys, tokens,
    passwords). Token saving + safety. Applied inside every text digest.

All compression is reversible: originals are cached by content hash and
`justokenmax retrieve <artifact>` hands the full version back. Tracked in a lifetime
ledger (`justokenmax stats`). A content sniffer routes generic files (.txt/.out/no
extension) to the right compressor automatically.


RESULTS (regenerable: python benchmarks/benchmark.py --fetch)
------------------------------------------------------------------------------
PDF -> Markdown (real public PDFs):
  Attention Is All You Need (arXiv)   15 pages   37,074 -> 14,574   -60%
  IRS Form W-9                         6 pages   18,305 ->  9,305   -49%
  TOTAL                               21 pages   55,379 -> 23,879   -56%

Logs:            4,345 -> 21 lines    107,668 -> 396 tokens    -99%
JSON:            2,000-row payload    168,023 -> 374 tokens    -99%
Notebook:        20 cells w/ images  401,170 -> 610 tokens    -99%
CSV:             5,000 rows           57,340 -> 237 tokens    -99%
Delta re-read:   1 edit in 600 lines   2,407 ->  88 tokens    -96%
Code index:      locate a symbol       16,691 -> 486 tokens    -97%  (21 lookups)
Images:          3000x2000 -> 1568x1045   186 KB -> 107 KB     -42% bytes

Detail: benchmarks/RESULTS.md   (drop your own files into benchmarks/fixtures/)


INSTALL
------------------------------------------------------------------------------
The canonical install is the Python package; it provides the `justokenmax` CLI.

From this repo (works today, Python 3.9+):
  git clone https://github.com/jusCode-Co/jusTokenMax && cd jusTokenMax
  pip install pypdf Pillow        # required codecs
  pip install pdfplumber          # optional: better PDF table extraction
  pip install ./python            # installs the `justokenmax` CLI (pip dist: justokenmax)
  justokenmax --version

From PyPI (once published):  pip install justokenmax

npm (optional thin shim - runs `python -m justokenmax`, so it still needs the Python
package above):  npm install -g @kalmantic/justokenmax

As a Claude Code plugin: add this repo as a plugin; the Read hook + commands +
skills + MCP server activate automatically. The hook calls `python3 -m justokenmax`,
so the Python package must be installed.


USE
------------------------------------------------------------------------------
  justokenmax optimize spec.pdf shot.png build.log   # auto-dispatch attachments+logs
  justokenmax logs ci-output.log                      # compress a verbose log
  justokenmax index                                   # build the code symbol index
  justokenmax query parse_config                      # find a symbol -> file:line+sig
  justokenmax stats                                   # lifetime token savings

Plugin surface:
  Hook     PreToolUse(Read) - rewrites PDF/image/.log/JSON reads to the cheap
           artifact via updatedInput; never blocks a Read.
  MCP      .mcp.json launches a stdlib stdio server (tools: justokenmax_optimize,
           justokenmax_compress_json, justokenmax_compress_log, justokenmax_query,
           justokenmax_retrieve, justokenmax_stats) so ANY MCP agent can call it.
  Commands /justokenmax:optimize, :logs, :index, :query, :delta, :redact, :retrieve,
           :terse, :branch, :compress-memory, :learn, :stats
  Skills   attachments (PDF/image/log), code-index, chat-branch, terse-output,
           cache-align


WHAT JUSTOKENMAX DOES THAT HEADROOM DOES NOT
------------------------------------------------------------------------------
- Claude-Code-native transparent rewrite: the Read hook swaps a heavy file for
  its cheap artifact in place via updatedInput, mid-tool-call. No proxy.
- A queryable code symbol index (codegraph-style): justokenmax query -> file:line +
  signature, so you avoid reading whole files (vs compressing code content).
- PDF -> Markdown that eliminates the per-page image channel (not just image
  recompression).
- Chat-branching as a first-class command (offload to a Claude Code subagent,
  merge back a digest).
- Fully transparent, zero-dependency heuristics - deterministic, auditable, no
  trained model and no network.


COMPARISON MATRIX
------------------------------------------------------------------------------
Legend:  JO=jusTokenMax  HR=headroom  CV=caveman  CG=codegraph
         Y = has it   ~ = partial/lighter   N = no   - = n/a

PDF -> Markdown (drop page-image channel) ... JO:Y  HR:N  CV:N  CG:N
Image / screenshot compression ............. JO:Y  HR:Y  CV:N  CG:N
Log / tool-output compression .............. JO:Y  HR:Y  CV:N  CG:N
JSON / structured-output compression ....... JO:Y  HR:Y  CV:N  CG:N
Notebook (.ipynb) compression .............. JO:Y  HR:N  CV:N  CG:N
CSV / tabular sampling ..................... JO:Y  HR:N  CV:N  CG:N
Delta / incremental re-reads (diff only) ... JO:Y  HR:N  CV:N  CG:N
Secret + base64-blob redaction ............. JO:Y  HR:N  CV:N  CG:N
Code symbol index (read symbols not files) . JO:~  HR:N  CV:N  CG:Y
Code content compression (AST shrink) ...... JO:N  HR:Y  CV:N  CG:N
Output-token reduction (terse style) ....... JO:Y  HR:Y  CV:Y  CG:N
Chat branching -> subagent + digest ........ JO:Y  HR:~  CV:N  CG:N
Cache-prefix alignment (KV cache) .......... JO:~  HR:Y  CV:N  CG:N
Memory-file compression .................... JO:Y  HR:Y  CV:Y  CG:N
Reversible (originals cached) .............. JO:Y  HR:Y  CV:-  CG:-
Retrieve original from artifact ............ JO:Y  HR:Y  CV:N  CG:N
Transparent in-place Read rewrite .......... JO:Y  HR:N  CV:N  CG:~
Content sniffer (auto-route files) ......... JO:Y  HR:Y  CV:N  CG:N
Savings ledger / stats ..................... JO:Y  HR:Y  CV:Y  CG:N
MCP server (any agent) ..................... JO:Y  HR:Y  CV:~  CG:Y
HTTP proxy / wrap / middleware ............. JO:N  HR:Y  CV:N  CG:N
Trained compression model .................. JO:N  HR:Y  CV:N  CG:N
Cross-agent shared memory .................. JO:N  HR:Y  CV:N  CG:N
Learn loop (mine sessions -> memory) ....... JO:~  HR:Y  CV:N  CG:N
Multi-language depth ....................... JO:~  HR:Y  CV:-  CG:Y
Zero-dependency / no network / auditable ... JO:Y  HR:N  CV:Y  CG:~
Single unified plugin (all levers) ......... JO:Y  HR:~  CV:N  CG:N
------------------------------------------------------------------------------
Full "Y" count:  jusTokenMax 19   headroom 13   caveman 4   codegraph 4

Read it this way:
  - Breadth + Claude-native + auditability -> jusTokenMax wins.
  - Depth on one axis -> the specialist wins (codegraph indexing, headroom
    compression sophistication, caveman output-style polish).
  - Our three real holes (all headroom-only): trained model, proxy/wrap modes,
    cross-agent shared memory.


HOW WE ENHANCED IT (v0.4.0) — BEYOND THE REFERENCES
------------------------------------------------------------------------------
These levers exist in jusTokenMax and in NONE of headroom / caveman / codegraph.
Each is deterministic, zero-dependency, and benchmarked:

  Notebook (.ipynb) compression  - drop base64 image outputs, truncate cell
                                   outputs, keep code+markdown.        -99%
  CSV / tabular sampling         - schema + inferred types + sample rows.  -99%
  Delta / incremental reads      - re-read returns only the diff vs the last
                                   read, not the whole file.           -96%
  Secret + base64 redaction      - mask API keys/tokens/passwords, elide blobs;
                                   tokens AND safety, applied in every digest.
  Content-sniff routing          - generic .txt/.out files routed to the right
                                   compressor by content, not extension.
  Reversible retrieve (CCR)      - any artifact maps back to its original.
  Transparent in-place Read swap - the hook rewrites a heavy Read to its cheap
                                   artifact via updatedInput, mid-tool-call.

Net effect: jusTokenMax covers headroom's input-compression core, adds a
codegraph-style symbol index and caveman-style terse output, and then adds five
levers none of them have - in one auditable, zero-dependency Claude Code plugin.


LIMITS & HONESTY
------------------------------------------------------------------------------
- No OCR: scanned/image-only PDFs -> empty Markdown; original passed through.
- PDF per-page tokens are a conservative model, not a billed number.
- Image token savings are base64-pipeline only; the always-real win is bytes.
- The code index is a snapshot, not live - re-run `justokenmax index` after changes.


SAFETY
------------------------------------------------------------------------------
Hooks run on untrusted files, so converters are bounded: PDFs capped at 2,000
pages / ~5M chars, Pillow decompression-bomb guard active, no shell execution,
content-hash output paths, and the Read hook fails open.


TEST
------------------------------------------------------------------------------
  cd python && pip install -e . pytest pdfplumber
  pytest -q     # 75 tests: pdf, image, log, json, notebook, csv, delta, redact,
                #           code-index, optimize, cli, hook, mcp


LICENSE
------------------------------------------------------------------------------
MIT - see LICENSE.
