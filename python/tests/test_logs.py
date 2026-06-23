from justokenmax.logs import compress_log


def _noisy_log():
    lines = ["\x1b[32mINFO\x1b[0m starting build"]
    lines += [f"\x1b[2mcompiling module {i}\x1b[0m" for i in range(200)]
    lines += ["downloading dep"] * 50          # exact repeats
    lines += [
        'Traceback (most recent call last):',
        '  File "a.py", line 1, in <module>',
        '  File "b.py", line 2, in foo',
        '  File "c.py", line 3, in bar',
        '  File "d.py", line 4, in baz',
        '  File "e.py", line 5, in qux',
        "ValueError: boom",
    ]
    lines += [f"cleanup step {i}" for i in range(40)]
    lines += ["WARNING: deprecated flag used", "Build FAILED"]
    return "\n".join(lines)


def test_strips_ansi_and_shrinks():
    raw = _noisy_log()
    digest, stats = compress_log(raw)
    assert "\x1b[" not in digest                     # ANSI gone
    assert stats["lines_after"] < stats["lines_before"]
    assert len(digest) < len(raw)


def test_keeps_errors_and_warnings():
    digest, _ = compress_log(_noisy_log())
    assert "ValueError: boom" in digest
    assert "Build FAILED" in digest
    assert "WARNING: deprecated flag used" in digest


def test_collapses_repeats_with_count():
    digest, _ = compress_log(_noisy_log())
    assert "(x" in digest                            # repeated lines collapsed


def test_folds_stack_frames():
    digest, _ = compress_log(_noisy_log())
    assert "stack frames elided" in digest
    # first and last frame preserved
    assert 'File "a.py"' in digest
    assert 'File "e.py"' in digest


def test_small_log_passthrough_shape():
    digest, stats = compress_log("line one\nline two\n")
    assert "line one" in digest and "line two" in digest
    assert stats["kind"] == "log"
