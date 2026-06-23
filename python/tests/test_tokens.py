import pytest

from justokenmax import tokens


def test_text_tokens_roughly_quarter_of_chars():
    assert tokens.text_tokens("x" * 400) == 100
    assert tokens.text_tokens("") == 1  # never zero


def test_image_tokens_clamp_to_max_edge():
    # Beyond MAX_EDGE the long edge is clamped, so a 4x-bigger image does not
    # cost 4x tokens.
    small = tokens.image_tokens(1568, 1000)
    huge = tokens.image_tokens(6272, 4000)  # 4x linear, same aspect
    assert huge == pytest.approx(small, rel=0.02)


def test_bytes_to_tokens_scales_with_bytes():
    assert tokens.bytes_to_tokens(3000) == 1000
    assert tokens.bytes_to_tokens(0) == 0
    assert tokens.bytes_to_tokens(900) < tokens.bytes_to_tokens(9000)


def test_pdf_page_cost_is_per_page():
    assert tokens.pdf_image_tokens(10) == 10 * tokens.PDF_PAGE_IMAGE_TOKENS
