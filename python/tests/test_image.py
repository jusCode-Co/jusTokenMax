import os

from justokenmax.image import compress_image


def test_downscales_to_max_edge_and_shrinks_bytes(big_image, tmp_path):
    out = str(tmp_path / "out")
    out_path, stats = compress_image(big_image, out, max_edge=1568, quality=80)

    assert os.path.exists(out_path)
    assert max(stats["new_size"]) <= 1568
    assert stats["bytes_after"] < stats["bytes_before"]
    assert stats["tokens_after"] < stats["tokens_before"]
    assert stats["tokens_saved"] > 0


def test_keeps_aspect_ratio(big_image, tmp_path):
    out = str(tmp_path / "out")
    _, stats = compress_image(big_image, out, max_edge=1568)
    ow, oh = stats["orig_size"]
    nw, nh = stats["new_size"]
    assert abs((ow / oh) - (nw / nh)) < 0.02


def test_custom_max_edge(big_image, tmp_path):
    out = str(tmp_path / "out")
    _, stats = compress_image(big_image, out, max_edge=800)
    assert max(stats["new_size"]) <= 800
