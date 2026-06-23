"""End-to-end test of the PreToolUse(Read) hook script.

Runs the actual hook the way Claude Code would: a JSON payload on stdin, JSON
decision on stdout. Verifies the transparent-rewrite contract and, critically,
that the hook NEVER blocks a Read (always exits 0, passthrough = empty stdout).
"""

import json
import os
import pathlib
import subprocess
import sys

HOOK = (pathlib.Path(__file__).resolve().parents[2] / "hooks"
        / "justokenmax_read.py")


def run_hook(payload: dict):
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload).encode(),
        capture_output=True,
        env=os.environ.copy(),  # inherits JUSTOKENMAX_HOME from isolated_home
    )
    return proc


def test_pdf_read_is_rewritten(text_pdf):
    proc = run_hook({
        "tool_name": "Read",
        "tool_input": {"file_path": text_pdf},
    })
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    hso = out["hookSpecificOutput"]
    assert hso["permissionDecision"] == "allow"
    assert hso["updatedInput"]["file_path"].endswith(".md")
    assert "justokenmax" in hso["additionalContext"]


def test_non_read_tool_passthrough(text_pdf):
    proc = run_hook({
        "tool_name": "Bash",
        "tool_input": {"command": "ls"},
    })
    assert proc.returncode == 0
    assert proc.stdout.strip() == b""


def test_unsupported_file_passthrough(tmp_path):
    p = tmp_path / "readme.txt"
    p.write_text("nothing to optimize")
    proc = run_hook({
        "tool_name": "Read",
        "tool_input": {"file_path": str(p)},
    })
    assert proc.returncode == 0
    assert proc.stdout.strip() == b""


def test_missing_file_passthrough(tmp_path):
    proc = run_hook({
        "tool_name": "Read",
        "tool_input": {"file_path": str(tmp_path / "nope.pdf")},
    })
    assert proc.returncode == 0
    assert proc.stdout.strip() == b""


def test_malformed_stdin_passthrough():
    proc = subprocess.run(
        [sys.executable, str(HOOK)],
        input=b"not json",
        capture_output=True,
        env=os.environ.copy(),
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == b""
