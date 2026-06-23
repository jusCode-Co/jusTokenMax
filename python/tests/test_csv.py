from justokenmax.csvtable import compress_csv


def _csv(n=100):
    rows = ["id,name,active"]
    for i in range(n):
        rows.append(f"{i},user{i},{'true' if i % 2 == 0 else 'false'}")
    return "\n".join(rows) + "\n"


def test_schema_and_types():
    md, st = compress_csv(_csv())
    assert st["ok"] and st["rows"] == 100 and st["cols"] == 3
    assert "id: int" in md
    assert "name: str" in md
    assert "active: bool" in md


def test_samples_and_shrinks():
    src = _csv(500)
    md, _ = compress_csv(src)
    assert "500 rows" in md
    assert len(md) < len(src)
    assert "user0" in md       # head sample
    assert "user499" in md     # tail sample


def test_tsv_delimiter():
    src = "a\tb\tc\n1\t2\t3\n4\t5\t6\n"
    md, st = compress_csv(src)
    assert st["ok"] and st["cols"] == 3
    assert st["delimiter"] == "\t"
