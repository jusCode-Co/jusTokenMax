"""Image compression.

Downscale to the model's resolution ceiling and recompress. We don't reinvent
codecs — Pillow does the encoding. Metadata is stripped (EXIF can be kilobytes
of nothing the model needs).
"""

from __future__ import annotations

import os
from typing import Tuple

from .tokens import MAX_EDGE, bytes_to_tokens


def _ensure_bomb_guard() -> None:
    """Keep Pillow's decompression-bomb protection active.

    Pillow raises DecompressionBombError above ~2x MAX_IMAGE_PIXELS. Since the
    Read hook feeds untrusted images here, we assert the guard is set rather
    than left at None (which would disable it).
    """
    from PIL import Image

    if Image.MAX_IMAGE_PIXELS is None:
        Image.MAX_IMAGE_PIXELS = 89_478_485  # Pillow's documented default


def _target_ext(fmt: str, has_alpha: bool) -> str:
    # Keep transparency in PNG; otherwise JPEG is the smaller win.
    if has_alpha:
        return ".png"
    return ".jpg"


def compress_image(
    path: str,
    out_path: str,
    max_edge: int = MAX_EDGE,
    quality: int = 80,
) -> Tuple[str, dict]:
    """Downscale + recompress an image. Returns (out_path, stats)."""
    from PIL import Image

    _ensure_bomb_guard()
    src_bytes = os.path.getsize(path)
    img = Image.open(path)
    orig_w, orig_h = img.size

    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )

    long_edge = max(img.size)
    if long_edge > max_edge:
        scale = max_edge / long_edge
        img = img.resize(
            (round(orig_w * scale), round(orig_h * scale)),
            Image.LANCZOS,
        )

    ext = _target_ext(img.format or "", has_alpha)
    out_path = os.path.splitext(out_path)[0] + ext

    if ext == ".jpg":
        img = img.convert("RGB")
        img.save(out_path, "JPEG", quality=quality, optimize=True)
    else:
        img.save(out_path, "PNG", optimize=True)

    out_w, out_h = img.size
    out_bytes = os.path.getsize(out_path)
    # Image savings are measured in bytes (always real) and translated to tokens
    # via the base64-inline model — see tokens.bytes_to_tokens.
    tokens_before = bytes_to_tokens(src_bytes)
    tokens_after = bytes_to_tokens(out_bytes)

    stats = {
        "kind": "image",
        "orig_size": [orig_w, orig_h],
        "new_size": [out_w, out_h],
        "bytes_before": src_bytes,
        "bytes_after": out_bytes,
        "tokens_before": tokens_before,
        "tokens_after": tokens_after,
        "tokens_saved": max(0, tokens_before - tokens_after),
    }
    return out_path, stats
