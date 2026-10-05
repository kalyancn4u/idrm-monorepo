"""Unit tests for the image pipeline (needs Pillow; no database).

Uses noise images so the blur gate has real edge variance to measure.
"""

from __future__ import annotations

from io import BytesIO

import pytest

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.modules.files.imaging import passes_face_quality_gate, process_image


def _noise_png(width: int, height: int) -> bytes:
    from PIL import Image

    img = Image.effect_noise((width, height), 128).convert("RGB")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_large_image_is_downscaled_and_stripped() -> None:
    from PIL import Image

    settings = get_settings()
    out = process_image(_noise_png(4000, 3000), "image/png", settings)
    result = Image.open(BytesIO(out))
    assert max(result.size) <= settings.image_max_dimension
    assert not result.getexif()  # metadata stripped


def test_small_image_is_rejected() -> None:
    with pytest.raises(AppError) as exc:
        process_image(_noise_png(100, 100), "image/png", get_settings())
    assert exc.value.code == "image_too_small"


def test_corrupt_bytes_are_rejected() -> None:
    with pytest.raises(AppError) as exc:
        process_image(b"not really an image", "image/png", get_settings())
    assert exc.value.code == "invalid_image"


def test_face_gate_is_a_passing_seam() -> None:
    assert passes_face_quality_gate(object()) is True
