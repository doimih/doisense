from io import BytesIO
from pathlib import Path
import re

from django.core.files.base import ContentFile
from PIL import Image, ImageSequence, UnidentifiedImageError


def normalize_image_stem(original_name: str, fallback: str = "image") -> str:
    stem = Path(str(original_name or fallback)).stem
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-") or fallback


def convert_uploaded_image_to_webp(uploaded_file, *, quality: int = 82) -> tuple[ContentFile, str]:
    uploaded_file.seek(0)
    try:
        image = Image.open(uploaded_file)
    except UnidentifiedImageError as exc:
        raise ValueError("Invalid image file.") from exc

    stem = normalize_image_stem(getattr(uploaded_file, "name", "image"))
    output = BytesIO()
    save_kwargs = {
        "format": "WEBP",
        "quality": quality,
        "method": 6,
    }

    if getattr(image, "is_animated", False):
        frames = [frame.convert("RGBA") for frame in ImageSequence.Iterator(image)]
        if not frames:
            raise ValueError("Invalid animated image.")
        frames[0].save(
            output,
            save_all=True,
            append_images=frames[1:],
            duration=image.info.get("duration", 100),
            loop=image.info.get("loop", 0),
            **save_kwargs,
        )
    else:
        if image.mode in {"RGBA", "LA", "P"}:
            converted = image.convert("RGBA")
        else:
            converted = image.convert("RGB")
        converted.save(output, **save_kwargs)

    output.seek(0)
    return ContentFile(output.getvalue(), name=f"{stem}.webp"), stem