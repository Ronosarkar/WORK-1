import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from PIL import Image

from core.variant_models import ImageVariantConfig
from core.metadata_manager import apply_image_metadata

logger = logging.getLogger(__name__)

def process_image(
    input_path: str,
    output_path: str,
    config: ImageVariantConfig,
    progress_callback: Optional[Callable[[float, str], None]] = None
) -> bool:
    """
    Processes an image using Pillow with strict quality preservation,
    optional Lanczos resizing, EXIF editing/stripping, and ICC profile retention.
    """
    try:
        if progress_callback:
            progress_callback(10.0, "Reading image...")

        with Image.open(input_path) as img:
            icc_profile = img.info.get("icc_profile") if config.preserve_icc else None
            out_img = img.copy()

            # Resize handling
            target_w, target_h = None, None
            if config.resize_mode == "1080p":
                target_w, target_h = 1920, 1080
            elif config.resize_mode == "1080x1920":
                target_w, target_h = 1080, 1920
            elif config.resize_mode == "custom":
                target_w, target_h = config.custom_width, config.custom_height

            if target_w and target_h:
                if progress_callback:
                    progress_callback(35.0, "Resampling with Lanczos filter...")
                out_img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

            # Metadata & EXIF
            exif_bytes = None
            if not config.strip_exif:
                exif_obj = apply_image_metadata(out_img, config.metadata)
                try:
                    exif_bytes = exif_obj.tobytes()
                except Exception:
                    exif_bytes = None

            # Format & Output handling
            fmt = config.output_format.upper()
            save_kwargs: Dict[str, Any] = {}

            if icc_profile:
                save_kwargs["icc_profile"] = icc_profile
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes

            if progress_callback:
                progress_callback(70.0, f"Encoding {fmt}...")

            if fmt in ("JPG", "JPEG"):
                # Handle alpha channel for JPEG
                if out_img.mode in ("RGBA", "LA", "P"):
                    rgb_img = Image.new("RGB", out_img.size, (255, 255, 255))
                    rgb_img.paste(out_img, mask=out_img.split()[-1] if out_img.mode in ("RGBA", "LA") else None)
                    out_img = rgb_img
                elif out_img.mode != "RGB":
                    out_img = out_img.convert("RGB")

                save_kwargs["quality"] = max(1, min(100, config.jpeg_quality))
                save_kwargs["subsampling"] = 0  # 4:4:4 chroma subsampling for sharpest edges
                save_kwargs["optimize"] = True
                out_img.save(output_path, "JPEG", **save_kwargs)

            elif fmt == "PNG":
                save_kwargs["optimize"] = True
                out_img.save(output_path, "PNG", **save_kwargs)

            elif fmt == "WEBP":
                save_kwargs["quality"] = max(1, min(100, config.jpeg_quality))
                save_kwargs["method"] = 6  # Highest compression efficiency
                out_img.save(output_path, "WEBP", **save_kwargs)
            else:
                out_img.save(output_path, **save_kwargs)

            if progress_callback:
                progress_callback(100.0, "Complete!")
                
            return True

    except Exception as e:
        logger.error(f"Error processing image {input_path}: {e}")
        return False
