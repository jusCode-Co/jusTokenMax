# Configuration — optimize your way

Every lever is **on by default**. Turn any of them off when a project needs the
raw file.

## CLI

```bash
justokenmax config                 # show what's on/off
justokenmax config disable pdf     # persist: skip PDFs from now on
justokenmax config enable pdf      # back on
```

## Environment (one-off)

```bash
JUSTOKENMAX_DISABLE=pdf,image justokenmax optimize x.pdf
```

## Config file

`~/.justokenmax/config.json` (or `JUSTOKENMAX_CONFIG`):

```json
{ "disabled": ["pdf", "image"] }
```

Either source disables a lever (whichever applies). **Kinds:** `pdf image log
json notebook csv diff redact`.

## Behaviour when disabled

- A disabled kind is **skipped** by `optimize()` (the result note reads
  `disabled by config`), so the Claude Code Read hook leaves those files
  untouched.
- Disabling `redact` stops the secret/blob masking pass inside text digests.

## Other knobs

- `JUSTOKENMAX_HOME` — where the cache, ledger, and config live (default
  `~/.justokenmax`, created `0700` owner-only).
- `justokenmax optimize --quality N --max-edge PX` — image compression tuning.
