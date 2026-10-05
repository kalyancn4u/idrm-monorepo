"""Server-side image processing for uploads (PICS-FIL-002/003/005).

The client is asked to compress on-device, but the **server re-checks and re-processes every
image** — never trust the client (doc 22 §7). Pipeline: apply EXIF orientation, then **strip all
metadata (incl. GPS)**, downscale to the max edge, enforce the minimum dimensions, run a blur check,
and pass a **face-detection-only quality gate**. Pillow is imported lazily so the module loads
without it.

**Face detection is a documented seam** (:func:`passes_face_quality_gate`): the MVP decision is a
*detection-only* gate with **nothing biometric stored** (ADR-011). A real lightweight detector needs
a heavier vision library and is wired in as a follow-up; until then the gate passes and
PICS-FIL-005 stays ``Planned``.
"""

from __future__ import annotations

from io import BytesIO

from app.core.config import Settings
from app.core.exceptions import AppError

# The image content types the MVP accepts (PDFs are handled without image processing).
IMAGE_TYPES = {"image/jpeg": "JPEG", "image/png": "PNG"}


def passes_face_quality_gate(image: object) -> bool:  # noqa: ARG001 - seam signature
    """Face **detection-only** quality gate (ADR-011) — server-side is intentionally a no-op.

    Per ADR-011 the detection gate is **client-side** (on-device, advisory): see
    ``frontend/static/js/face-quality.js``, which warns before upload and computes **nothing
    biometric** server-side. Keeping this a pass-through is deliberate privacy design — the server
    never receives or computes face data. The server's authoritative re-checks (size, dimensions,
    EXIF/GPS stripping, blur) run in :func:`process_image`. FaceNet *recognition* is → FFP.
    """
    return True


def _blur_variance(image: object) -> float:
    """A lightweight blur metric: variance of the edge-detected grayscale image (more = sharper)."""
    from PIL import ImageFilter, ImageStat

    edges = image.convert("L").filter(ImageFilter.FIND_EDGES)
    return float(ImageStat.Stat(edges).var[0])


def process_image(raw: bytes, content_type: str, settings: Settings) -> bytes:
    """Validate + normalise an uploaded image, returning clean, metadata-free bytes.

    Raises :class:`AppError` (422) if the image is corrupt, too small, or too blurry.
    """
    from PIL import Image, ImageOps, UnidentifiedImageError

    pil_format = IMAGE_TYPES[content_type]
    try:
        image = Image.open(BytesIO(raw))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise AppError(422, "invalid_image", "The uploaded image could not be read.") from exc

    # Apply then discard EXIF orientation; rebuild from raw pixels to strip ALL metadata (GPS too).
    image = ImageOps.exif_transpose(image)
    clean = Image.new(image.mode, image.size)
    clean.putdata(list(image.getdata()))

    # Downscale so the longest edge is within the limit (never upscale).
    clean.thumbnail((settings.image_max_dimension, settings.image_max_dimension))

    width, height = clean.size
    if width < settings.image_min_width or height < settings.image_min_height:
        raise AppError(
            422,
            "image_too_small",
            f"Image must be at least {settings.image_min_width}x{settings.image_min_height}px.",
        )
    if _blur_variance(clean) < settings.image_blur_min_variance:
        raise AppError(422, "image_too_blurry", "Image is too blurry; please retake it.")
    if not passes_face_quality_gate(clean):
        raise AppError(422, "image_quality", "Image did not pass the quality check.")

    out = BytesIO()
    save_kwargs = {"quality": 85} if pil_format == "JPEG" else {}
    clean.save(out, format=pil_format, **save_kwargs)
    return out.getvalue()
