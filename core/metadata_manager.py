import os
import datetime
from typing import List, Dict, Any, Optional
from PIL import Image, ExifTags
from core.variant_models import MetadataConfig

def build_ffmpeg_metadata_args(meta: MetadataConfig) -> List[str]:
    """Generates FFmpeg command-line flags for metadata injection."""
    args = []
    
    if meta.strip_all_first:
        # Drops global and stream metadata before adding new tags
        args.extend(["-map_metadata", "-1"])
        
    if meta.title.strip():
        args.extend(["-metadata", f"title={meta.title.strip()}"])
        
    if meta.author.strip():
        args.extend(["-metadata", f"artist={meta.author.strip()}"])
        args.extend(["-metadata", f"author={meta.author.strip()}"])
        
    if meta.creator.strip():
        args.extend(["-metadata", f"composer={meta.creator.strip()}"])
        args.extend(["-metadata", f"creator={meta.creator.strip()}"])

    if meta.description.strip():
        args.extend(["-metadata", f"description={meta.description.strip()}"])
        
    if meta.comment.strip():
        args.extend(["-metadata", f"comment={meta.comment.strip()}"])
        
    if meta.copyright.strip():
        args.extend(["-metadata", f"copyright={meta.copyright.strip()}"])
        
    if meta.software.strip():
        args.extend(["-metadata", f"encoder={meta.software.strip()}"])
        args.extend(["-metadata", f"encoded_by={meta.software.strip()}"])
        
    if meta.keywords.strip():
        args.extend(["-metadata", f"genre={meta.keywords.strip()}"])
        args.extend(["-metadata", f"keywords={meta.keywords.strip()}"])
        
    if meta.creation_date.strip():
        date_val = meta.creation_date.strip()
        if date_val.lower() == "now":
            date_val = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args.extend(["-metadata", f"creation_time={date_val}"])
        args.extend(["-metadata", f"date={date_val}"])

    return args

def apply_image_metadata(img: Image.Image, meta: MetadataConfig) -> Image.Exif:
    """Creates/modifies Pillow EXIF object according to MetadataConfig."""
    exif = img.getexif()
    if meta.strip_all_first:
        exif.clear()

    # Standard EXIF Tag IDs:
    # 0x010E (270): ImageDescription
    # 0x013B (315): Artist
    # 0x8298 (33432): Copyright
    # 0x0131 (305): Software
    # 0x0132 (306): DateTime
    
    if meta.description.strip():
        exif[0x010E] = meta.description.strip()
    elif meta.title.strip():
        exif[0x010E] = meta.title.strip()
        
    if meta.author.strip():
        exif[0x013B] = meta.author.strip()
    elif meta.creator.strip():
        exif[0x013B] = meta.creator.strip()
        
    if meta.copyright.strip():
        exif[0x8298] = meta.copyright.strip()
        
    if meta.software.strip():
        exif[0x0131] = meta.software.strip()
        
    date_val = meta.creation_date.strip()
    if date_val.lower() == "now":
        date_val = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    if date_val:
        exif[0x0132] = date_val

    return exif
