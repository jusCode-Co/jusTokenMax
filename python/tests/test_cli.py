import json

from justokenmax.cli import main


def test_optimize_json_pdf(text_pdf, capsys):
    rc = main(["optimize", "--json", text_pdf])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["ok"] is True
    assert out["kind"] == "pdf"
    assert out["tokens_saved"] > 0


def test_optimize_multiple_returns_list(text_pdf, big_image, capsys):
    rc = main(["optimize", "--json", text_pdf, big_image])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert isinstance(out, list) and len(out) == 2


def test_stats_json_reflects_runs(text_pdf, capsys):
    main(["optimize", "--json", text_pdf])
    capsys.readouterr()  # discard the optimize output
    main(["stats", "--json"])
    led = json.loads(capsys.readouterr().out)
    assert led["runs"] >= 1
    assert led["total_tokens_saved"] > 0


def test_optimize_unsupported_returns_nonzero(tmp_path, capsys):
    p = tmp_path / "x.txt"
    p.write_text("hi")
    rc = main(["optimize", "--json", str(p)])
    capsys.readouterr()
    assert rc == 1  # nothing optimized
