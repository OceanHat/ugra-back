from dataclasses import dataclass
from pathlib import Path

@dataclass
class ImageSize:
    width: int
    height: int
    quality: int = 85

ITEM_THUMBNAIL = ImageSize(width=200, height=200, quality=75)
ITEM_FULL = ImageSize(width=1200, height=800, quality=90)

STORAGE_DIR = Path("storage/images")
ITEM_IMAGES_DIR = STORAGE_DIR / "items"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024
