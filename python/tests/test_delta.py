from justokenmax.delta import delta


def test_first_read_is_full(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("line1\nline2\nline3\n")
    art, st = delta(str(p))
    assert st["had_prior"] is False
    assert "line1" in art and "line3" in art


def test_second_read_returns_diff(tmp_path):
    p = tmp_path / "f.txt"
    lines = [f"line{i}" for i in range(200)]
    p.write_text("\n".join(lines) + "\n")
    delta(str(p))                          # snapshot v1
    lines[100] = "CHANGED_LINE"
    p.write_text("\n".join(lines) + "\n")  # edit one line
    art, st = delta(str(p))
    assert st["had_prior"] and st["changed"]
    assert "CHANGED_LINE" in art
    assert "@@" in art                     # unified-diff hunk header
    assert st["tokens_delta"] < st["tokens_full"]


def test_unchanged_read_reports_no_change(tmp_path):
    p = tmp_path / "f.txt"
    p.write_text("same content\n")
    delta(str(p))
    art, st = delta(str(p))
    assert st["changed"] is False
    assert "no changes" in art
