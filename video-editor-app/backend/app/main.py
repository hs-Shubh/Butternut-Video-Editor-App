import os
import uuid
import json
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .models import Metadata
from .config import settings
from .storage import save_upload
from .queue import queue
from .worker import render_job
from redis import Redis


app = FastAPI(title="Video Editor Backend", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = Redis.from_url(settings.REDIS_URL)


def auth_guard(x_api_key: Optional[str]):
    if settings.API_KEY and (x_api_key != settings.API_KEY):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    metadata: str = Form(...),
    x_api_key: Optional[str] = Header(default=None),
):
    auth_guard(x_api_key)
    try:
        Metadata.model_validate_json(metadata)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid metadata: {e}")

    data = await file.read()
    stored = save_upload(file.filename, data)
    job_id = str(uuid.uuid4())
    redis.hset(f"job:{job_id}", mapping={"status": "queued", "progress_percent": 0, "message": "queued"})
    queue.enqueue(render_job, job_id, stored, metadata, job_id=job_id)
    return {"job_id": job_id}


@app.get("/status/{job_id}")
def status(job_id: str):
    h = redis.hgetall(f"job:{job_id}")
    if not h:
        raise HTTPException(status_code=404, detail="Not found")
    def _get(key: bytes, default: str) -> str:
        return h.get(key, default.encode()).decode()
    return {
        "status": _get(b"status", "queued"),
        "progress_percent": int(_get(b"progress_percent", "0")),
        "message": _get(b"message", ""),
    }


@app.get("/result/{job_id}")
def result(job_id: str):
    h = redis.hgetall(f"job:{job_id}")
    if not h:
        raise HTTPException(status_code=404, detail="Not found")
    status = h.get(b"status", b"").decode()
    if status != "done":
        raise HTTPException(status_code=400, detail="Not completed")
    result_path = h.get(b"result_path", b"").decode()
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Result file missing")
    return FileResponse(result_path, media_type="video/mp4", filename="rendered.mp4")
