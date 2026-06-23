import os

import pytest

from justokenmax import codeindex


@pytest.fixture
def sample_repo(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "core.py").write_text(
        'def parse_config(path, strict=False):\n'
        '    """Load and validate config."""\n'
        '    return {}\n'
        '\n'
        'class Engine:\n'
        '    """The engine."""\n'
        '    def run(self, x, *args, **kw):\n'
        '        return x\n'
    )
    (tmp_path / "web.js").write_text(
        "export function renderPage(props) {}\n"
        "const handleClick = (e) => {}\n"
        "class Widget {}\n"
    )
    # a dir that must be skipped
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "junk.js").write_text("function shouldNotIndex(){}\n")
    return str(tmp_path)


def test_build_index_python_symbols(sample_repo):
    idx = codeindex.build_index(sample_repo)
    names = {s["name"] for s in idx["symbols"]}
    assert {"parse_config", "Engine", "run", "renderPage", "Widget"} <= names
    # skip dir respected
    assert "shouldNotIndex" not in names
    # index file written
    assert os.path.exists(os.path.join(sample_repo, ".justokenmax", "index.json"))


def test_python_signature_and_kind(sample_repo):
    codeindex.build_index(sample_repo)
    hits = codeindex.query(sample_repo, "parse_config")
    assert hits[0]["kind"] == "func"
    assert hits[0]["sig"] == "def parse_config(path, strict)"
    assert hits[0]["doc"] == "Load and validate config."
    assert hits[0]["file"].endswith("core.py")


def test_method_is_qualified(sample_repo):
    codeindex.build_index(sample_repo)
    hits = codeindex.query(sample_repo, "run", kind="method")
    assert hits and hits[0]["sig"] == "Engine.run(self, x, *args, **kw)"


def test_query_exact_match_ranks_first(sample_repo):
    codeindex.build_index(sample_repo)
    hits = codeindex.query(sample_repo, "Widget")
    assert hits[0]["name"] == "Widget"
    assert hits[0]["kind"] == "class"


def test_query_without_index_returns_empty(tmp_path):
    assert codeindex.query(str(tmp_path), "anything") == []


def test_format_hits_compact(sample_repo):
    codeindex.build_index(sample_repo)
    out = codeindex.format_hits(codeindex.query(sample_repo, "parse_config"))
    assert "core.py:1" in out and "[func]" in out
