"""Rough token estimators, used only to report savings.

These are deliberately simple and dependency-free. The point is a defensible
before/after number, not accounting-grade precision. Constants follow
Anthropic's published guidance for image tokens (~ width*height / 750) and the
common ~4 chars/token rule for text.
"""

from __future__ import annotations

# Long-edge ceiling Claude resizes images to before tokenizing. Anything larger
# is downscaled by the API anyway, so shipping bigger pixels just wastes bytes.
MAX_EDGE = 1568

# When a PDF is ingested, each page is sent BOTH as extracted text AND as a page
# image (so the model can see layout/figures). Converting to Markdown keeps the
# text and drops the image channel. This is the per-page image cost we remove —
# a US-letter page clamps to ~1.15MP, i.e. ~1,530 tokens; we use a conservative
# 1,500 so we never overclaim the saving.
PDF_PAGE_IMAGE_TOKENS = 1500


def text_tokens(text: str) -> int:
    """Estimate tokens for a chunk of text (~4 chars/token). Always >= 1."""
    return max(1, len(text) // 4)


def image_tokens(width: int, height: int) -> int:
    """Vision-cost reference: tokens an image costs a native-vision model.

    Mirrors the API: clamp the long edge to MAX_EDGE (preserving aspect), then
    tokens ~= (w * h) / 750. Note: because the API downscales automatically,
    OUR downscaling does not reduce this number — it only reduces bytes. For the
    savings ledger we use `bytes_to_tokens` instead (see below).
    """
    if width <= 0 or height <= 0:
        return 0
    long_edge = max(width, height)
    if long_edge > MAX_EDGE:
        scale = MAX_EDGE / long_edge
        width = round(width * scale)
        height = round(height * scale)
    return int((width * height) / 750)


def bytes_to_tokens(n_bytes: int) -> int:
    """Estimate tokens for an image carried as base64 text.

    Many agent pipelines inline images as base64 in the prompt; base64 expands
    bytes ~4/3 and tokenizes ~4 chars/token, so tokens ~= bytes / 3. This is the
    figure that actually shrinks when we recompress an image, so it's what the
    image savings ledger reports.
    """
    return max(0, n_bytes // 3)


def pdf_image_tokens(n_pages: int) -> int:
    """The page-image token cost that converting to Markdown removes.

    A PDF is billed as text + a per-page image; Markdown keeps the text and
    eliminates this image channel, so this is the saving.
    """
    return n_pages * PDF_PAGE_IMAGE_TOKENS
