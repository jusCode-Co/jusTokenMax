#!/usr/bin/env node
/**
 * Thin Node wrapper over the jusTokenMax Python core.
 *
 * It does no PDF/image work itself — it locates a Python interpreter and runs
 * `python -m justokenmax`, forwarding all arguments. The Python package
 * (`pip install justokenmax`) is the single source of truth for the actual
 * conversion logic.
 *
 * Resolution order for the Python core:
 *   1. A sibling `python/` dir in the repo (dev / running from a clone).
 *   2. Otherwise the pip-installed `justokenmax` module on the active interpreter.
 */
"use strict";

const { spawnSync } = require("child_process");
const path = require("path");
const fs = require("fs");

// Repo checkout layout: <repo>/node/bin/justokenmax.js -> <repo>/python
const REPO_PY_DIR = path.resolve(__dirname, "..", "..", "python");

function findPython() {
  for (const cmd of ["python3", "python"]) {
    const probe = spawnSync(cmd, ["--version"], { stdio: "ignore" });
    if (!probe.error && probe.status === 0) return cmd;
  }
  return null;
}

function main() {
  const python = findPython();
  if (!python) {
    console.error(
      "justokenmax: no Python interpreter found. Install Python 3.9+, then:\n" +
        "  pip install justokenmax"
    );
    process.exit(127);
  }

  const env = { ...process.env };
  if (fs.existsSync(path.join(REPO_PY_DIR, "justokenmax"))) {
    // Running from a repo clone: make the local package importable.
    env.PYTHONPATH = env.PYTHONPATH
      ? `${REPO_PY_DIR}${path.delimiter}${env.PYTHONPATH}`
      : REPO_PY_DIR;
  }

  // Verify the module is importable; give an actionable message if not.
  const check = spawnSync(python, ["-c", "import justokenmax"], { env, stdio: "ignore" });
  if (check.status !== 0) {
    console.error(
      "justokenmax: the Python core isn't installed. Install it with:\n" +
        "  pip install justokenmax\n" +
        "(plus `pip install pypdf Pillow` for PDF/image support)."
    );
    process.exit(127);
  }

  const res = spawnSync(python, ["-m", "justokenmax", ...process.argv.slice(2)], {
    stdio: "inherit",
    env,
  });
  if (res.error) {
    console.error(`justokenmax: failed to run Python core: ${res.error.message}`);
    process.exit(1);
  }
  process.exit(res.status === null ? 1 : res.status);
}

main();
