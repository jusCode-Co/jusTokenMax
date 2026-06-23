# jusTokenMax benchmarks

Measures how much jusTokenMax reduces tokens across its modules — attachments
(PDF/image), logs, and the code index. Designed to keep improving — drop
better/real documents in and regenerate.

## Run

```bash
pip install pypdf Pillow pdfplumber tiktoken   # tiktoken = real token counts
python benchmark.py            # uses ./fixtures, generates samples if empty
python benchmark.py --fetch    # also downloads a couple of real public PDFs
```

Results print to stdout and are written to [`RESULTS.md`](RESULTS.md).

## Bring your own documents

Put any `.pdf`, `.png`, `.jpg`, `.jpeg`, or `.webp` into `fixtures/` and re-run.
Downloaded/generated fixtures are git-ignored (we don't redistribute
third-party PDFs), so the harness re-fetches or regenerates them on demand.

## Method (and its honesty)

- **Markdown side** is counted with a real tokenizer (`tiktoken`/`cl100k`) when
  installed, falling back to a `chars/4` estimate. The label in the output says
  which was used.
- **PDF "before"** models how a PDF is actually billed: extracted **text** plus a
  per-page **image** (~1,500 tokens/page after the API clamps a page to
  ≤1.15MP). justokenmax keeps the text and removes the image channel, so
  `before = text + pages×1500`, `after = text`. The conservative per-page figure
  means we under- rather than over-state the saving.
- **Image side** reports bytes (always real) and a base64-inline token estimate
  (`bytes/3`). Native-vision token cost is unchanged because the API downscales
  regardless — so we don't claim a native-vision token saving for images.

## Caveats we want to fix

- Per-page image tokens are a model, not a billed measurement; a calibration pass
  against real API token counts would tighten the numbers.
- 2-column / heavily-tabular PDFs extract imperfectly with the current text
  extractor; better table fidelity is on the roadmap.
