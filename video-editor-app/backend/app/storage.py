import os
import uuid
from typing import Optional
from .config import settings


def ensure_dirs() -> None:
    os.makedirs(settings.STORAGE_ROOT, exist_ok=True)
    os.makedirs(settings.OUTPUT_ROOT, exist_ok=True)
    os.makedirs(settings.ASSETS_DIR, exist_ok=True)


def save_upload(filename: str, data: bytes) -> str:
    ensure_dirs()
    ext = os.path.splitext(filename)[1]
    name = f"{uuid.uuid4()}{ext}"
    path = os.path.join(settings.STORAGE_ROOT, name)
    with open(path, "wb") as f:
        f.write(data)
    return path


def get_asset_path(name_or_url: str) -> Optional[str]:
    if name_or_url.startswith("http://") or name_or_url.startswith("https://"):
        return None
    p = os.path.join(settings.ASSETS_DIR, name_or_url)
    return p if os.path.exists(p) else None


def output_path(job_id: str, extension: str = ".mp4") -> str:
    ensure_dirs()
    return os.path.join(settings.OUTPUT_ROOT, f"{job_id}{extension}")
