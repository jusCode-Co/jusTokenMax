import json

from justokenmax.jsoncompress import compress_json, looks_like_json


def test_long_array_is_sampled():
    src = json.dumps({"items": list(range(1000))})
    digest, stats = compress_json(src)
    assert stats["ok"]
    assert "more of 1000 items elided" in digest
    assert len(digest) < len(src)
    assert stats["bytes_after"] < stats["bytes_before"]


def test_long_string_truncated():
    src = json.dumps({"blob": "y" * 5000})
    digest, _ = compress_json(src)
    assert "chars)" in digest
    assert len(digest) < 1000


def test_minifies_whitespace():
    src = json.dumps({"a": 1, "b": 2}, indent=4)
    digest, _ = compress_json(src)
    assert digest == '{"a":1,"b":2}'          # whitespace stripped


def test_keeps_head_and_tail_elements():
    src = json.dumps(list(range(100)))
    digest, _ = compress_json(src)
    assert digest.startswith("[0,1,2,")        # head sample kept
    assert digest.rstrip("]").endswith("97,98,99")  # tail sample kept


def test_non_json_unchanged():
    digest, stats = compress_json("this is not json")
    assert stats["ok"] is False
    assert digest == "this is not json"


def test_looks_like_json():
    assert looks_like_json('{"a":1}')
    assert looks_like_json("[1,2,3]")
    assert not looks_like_json("hello")
    assert not looks_like_json("")
