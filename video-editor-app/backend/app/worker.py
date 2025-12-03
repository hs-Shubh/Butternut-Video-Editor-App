import os
import uuid
import json
from typing import Any

from redis import Redis
from .config import settings
from .models import Metadata
from .storage import output_path
from .ffmpeg_renderer import render_ffmpeg


redis = Redis.from_url(settings.REDIS_URL)


def progress_update(job_id: str, percent: int, message: str) -> None:
    redis.hset(f"job:{job_id}", mapping={"status": "processing", "progress_percent": percent, "message": message})


def render_job(job_id: str, input_video_path: str, metadata_json: str) -> dict[str, Any]:
    redis.hset(f"job:{job_id}", mapping={"status": "processing", "progress_percent": 0, "message": "starting"})
    try:
        meta = Metadata.model_validate_json(metadata_json)
        out_path = output_path(job_id, ".mp4")

        def cb(pct: int, msg: str):
            progress_update(job_id, pct, msg)

        render_ffmpeg(input_video_path, meta, out_path, cb)
        redis.hset(
            f"job:{job_id}", mapping={"status": "done", "progress_percent": 100, "message": "completed", "result_path": out_path}
        )
        return {"result_path": out_path}
    except Exception as e:
        redis.hset(
            f"job:{job_id}", mapping={"status": "failed", "progress_percent": 0, "message": str(e)}
        )
        raise
