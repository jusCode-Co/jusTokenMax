# Try jusTokenMax in 5 minutes — see the savings, on vs off

A hands-on walkthrough you can copy-paste. Scenario: you're asking your agent to
**"build a website that lists these products"** — and you're feeding it a big
product **CSV**, a **PDF spec**, and a noisy **build log**. Those three inputs
are what blow up the token bill. Here's jusTokenMax shrinking them, and what
happens when you turn it off.

## 0. Install

```bash
git clone https://github.com/Kalmantic/jusTokenMax && cd jusTokenMax
pip install pypdf Pillow ./python
justokenmax --version
export JUSTOKENMAX_HOME=$(mktemp -d)/.jtm     # use a throwaway cache for this demo
```

## 1. Make the sample inputs

```bash
# a 5,000-row product catalog (CSV)
python - <<'PY'
import csv
with open("products.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id","name","price","in_stock"])
    for i in range(5000):
        w.writerow([i, f"Product {i}", round(i*1.99,2), i%2==0])
PY

# a noisy build log
{ for i in $(seq 1 4000); do echo "[12:00:0$((i%9))] DEBUG bundling chunk_$i"; done;
  printf 'fetching dep\n%.0s' {1..200}; echo "ERROR: build failed"; } > build.log
```

## 2. Feature ON — watch it shrink

```bash
justokenmax optimize products.csv build.log
```

You'll see something like:

```
ok    products.csv
      -> .../<hash>.csv.md
      57,340 -> 237 tokens (-57,103, -99%)  [csv]  5000 rows x 4 cols
ok    build.log
      -> .../<hash>.log.txt
      44,160 -> 230 tokens (-43,930, -99%)  [log]  ...
```

The CSV became a schema + sample rows; the log became a digest. Your agent gets
all the **shape** it needs to build the site, at ~1% of the tokens. Check the
running total:

```bash
justokenmax stats
# justokenmax: 100,000+ tokens saved across 2 runs
```

## 3. Feature OFF — optimize your way

Don't want CSV touched (maybe you need every row)? Turn that lever off:

```bash
justokenmax config disable csv
justokenmax optimize products.csv     # -> skip  products.csv  (disabled by config)
justokenmax config                    #  csv  OFF   (everything else still on)
justokenmax config enable csv         # back on
```

Same with `JUSTOKENMAX_DISABLE=pdf,image justokenmax optimize ...` for a one-off.

## 4. In Claude Code — it's automatic

Install it as a Claude Code plugin. From inside Claude Code, run these three
slash commands **one at a time** — Claude Code takes a single slash command per
prompt, so don't paste all three together:

1. `/plugin marketplace add https://github.com/Kalmantic/jusTokenMax.git`
2. `/plugin install justokenmax@justokenmax`
3. `/reload-plugins`

(Non-interactive equivalent in a terminal: `claude plugin marketplace add
https://github.com/Kalmantic/jusTokenMax.git` then `claude plugin install
justokenmax@justokenmax`.)

The plugin's hook needs the `justokenmax` CLI on your `PATH` — if you cloned and
`pip install ./python`'d in step 0 you're set; otherwise `pip install justokenmax`
(or just have Node, and it auto-provisions via `npx`/`uv`).

Now when your agent **reads** `products.csv` / `build.log` / a PDF spec while
building the site, the `Read` hook transparently swaps in the cheap artifact —
you do nothing. Turn a lever off with `justokenmax config disable <kind>` and the
hook leaves that file untouched. Run `justokenmax stats` anytime to see the
lifetime savings.

Prefer just the tools (no auto-hook)? `justokenmax install claude` registers the
MCP server in a project `.mcp.json` instead (remove it with `justokenmax
uninstall claude`).

**To uninstall the plugin** later, run these one at a time:

1. `/plugin uninstall justokenmax@justokenmax`
2. `/plugin marketplace remove justokenmax`
3. `/reload-plugins`

## 5. In Codex CLI / OpenCode / Cursor

```bash
justokenmax install            # auto-detects and registers the MCP server
# ...then in that agent, the justokenmax_* tools are available.
justokenmax uninstall          # clean removal
```

## 6. The real test — extend a website codebase, then measure

The bigger use case isn't a one-shot build — it's **day-to-day development on an
existing website**, where the token bill is dominated by the agent *reading*
source files, the lockfile, build output, and **re-reading** them as it
iterates. That's exactly where jusTokenMax saves tokens. Here's a self-contained
project to prove it.

### Scaffold a small e-commerce website project

```bash
mkdir -p shopsite/src shopsite/public shopsite/data && cd shopsite

cat > package.json <<'JSON'
{ "name":"shopsite","version":"1.0.0",
  "scripts":{"build":"node build.js","dev":"node server.js"},
  "dependencies":{"express":"^4.19.2","nanoid":"^5.0.7"} }
JSON

# a chunky package-lock.json — the classic token sink
python3 - <<'PY'
import json
d={f"node_modules/pkg-{i}":{"version":f"1.{i}.0",
   "resolved":f"https://registry.npmjs.org/pkg-{i}/-/pkg-{i}-1.{i}.0.tgz",
   "integrity":"sha512-"+"A"*86,
   "dependencies":{f"dep-{j}":"^1.0.0" for j in range(6)}} for i in range(800)}
json.dump({"name":"shopsite","lockfileVersion":3,"packages":d}, open("package-lock.json","w"), indent=2)
PY

# several source modules (so navigating the code costs real tokens)
for m in catalog cart filters render api utils format storage; do
  M="$(printf '%s' "${m:0:1}" | tr a-z A-Z)${m:1}"
  cat > "src/$m.js" <<JS
// $m module — part of the ShopSite frontend
export function ${m}Init(config) { return { ...config, ready: true }; }
export function ${m}Load(data) { return (data || []).map((x) => x); }
export class ${M}Manager {
  constructor(opts) { this.opts = opts || {}; }
  process(items) { return (items || []).filter(Boolean); }
  render(el) { if (el) el.innerHTML = ""; }
}
export const ${m}Defaults = { enabled: true, limit: 50 };
JS
done

# 5,000-row product catalog + a noisy build log
python3 - <<'PY'
import csv
with open("data/products.csv","w",newline="") as f:
    w=csv.writer(f); w.writerow(["id","name","price","category","in_stock"])
    for i in range(5000): w.writerow([i,f"Product {i}",round(i*1.99,2),f"cat{i%12}",i%2==0])
PY
{ for i in $(seq 1 3000); do echo "[12:00:0$((i%9))] bundling src/module_$i.js ok"; done;
  echo "ERROR: TypeError: cart is undefined (src/cart.js:42)"; } > build.log

printf '<!doctype html><html><body><div id="app"></div><script type="module" src="../src/render.js"></script></body></html>' > public/index.html
cd ..
echo "scaffolded ./shopsite"
```

### The prompt (paste into your agent, working inside `shopsite/`)

> **I'm building an e-commerce product website. Add three features to this
> existing codebase:**
> 1. a **product search + category filter** bar,
> 2. a **shopping cart** that persists in `localStorage`,
> 3. a **dark-mode toggle**.
>
> Work like a real engineer:
> - First **explore the codebase** to understand how the modules fit together
>   (catalog, cart, filters, render, api, utils, format, storage) before changing
>   anything.
> - Check `package.json` and the dependency tree, and skim `package-lock.json` if
>   you need to confirm a version.
> - Wire the data from `data/products.csv` into the catalog.
> - Implement the features across the relevant `src/*.js` modules and update
>   `public/index.html`.
> - Read `build.log` to see the current build error and make sure your changes
>   address it.
> - After each edit, re-read the file you changed to verify it, and re-check
>   `build.log` at the end.

This is a normal dev loop: it **navigates 8 source modules**, reads
`package.json` + the big `package-lock.json`, the **5,000-row CSV**, the noisy
**build log**, and **re-reads** files as it edits — every one of which
jusTokenMax compresses (code index/outline, JSON, diff, CSV, log, delta).

### Measure it (on vs off)

1. **jusTokenMax ON** (plugin installed, or `justokenmax install`). Optionally
   pre-build the symbol index so navigation is cheap:
   ```bash
   justokenmax index shopsite
   ```
   Run the prompt. When it finishes, check Claude Code's context/cost with
   **`/cost`**, and run **`justokenmax stats`** for the tokens it saved.
2. **Turn it OFF**, `/clear`, and run the **identical** prompt again:
   ```bash
   justokenmax config disable json diff csv log     # or uninstall the plugin
   ```
3. **Compare `/cost`.** The "off" run drags whole source files, the full
   `package-lock.json`, the raw CSV, and the noisy log into context — and pays
   again on every re-read. The "on" run carries outlines, digests, and diffs.
   In a real multi-file dev loop the input savings compound; re-enable with
   `justokenmax config enable json diff csv log`.

> Tip: keep the task identical and `/clear` between runs so the only variable is
> jusTokenMax on vs off.

---

That's it — the same tool, the same savings, your toggles. Liked it?
**[Sponsor ❤](https://github.com/sponsors/Kashi-KS)**.
