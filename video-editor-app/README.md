# Video Editor App

Build a full-stack video editing app: users upload a video, add overlays (text, image, video), preview on the frontend, then submit to a FastAPI backend which renders the final video using ffmpeg.

## Project Structure
- `frontend/` Expo React Native app (TypeScript)
- `backend/` FastAPI service with RQ + Redis worker and ffmpeg renderer
- `data/` Local storage for uploads, outputs, and assets
- `demo/` Walkthrough script and sample metadata

## Sample Assets
Use the assets from this Google Drive folder:
https://drive.google.com/drive/folders/1aQ1CxHvfppzfUaUF3wYLJsUfbak5rbvo?usp=sharing

Place downloaded files under:
- `data/assets/` for backend rendering
- `frontend/assets/` for frontend preview

Expected filenames:
- `base_video.mp4`
- `overlay_image.png`
- `overlay_clip.mp4`

## Backend Setup
Requirements: Python 3.10+, ffmpeg, Redis

Install ffmpeg:
- macOS: `brew install ffmpeg`
- Ubuntu: `sudo apt-get update && sudo apt-get install -y ffmpeg`
- Windows (winget): `winget install Gyan.FFmpeg`

Install dependencies and run FastAPI locally:
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Run Redis:
```
docker run -p 6379:6379 redis:7-alpine
```

Run the RQ worker:
```
python -m app.worker_entry
```

Environment variables: see `.env.example` at repo root.

Optional S3:
Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `AWS_S3_BUCKET` for upload of rendered outputs. When unset, files are stored locally under `data/outputs`.

## Frontend Setup
Requirements: Node.js LTS, Expo CLI

```
cd frontend
npm install
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000 npm run start
```

Run on devices:
- iOS: `npm run ios`
- Android: `npm run android`
- Web: `npm run web`

The Editor screen supports:
- Picking a local video or using `base_video.mp4`
- Adding text/image/video overlays
- Drag/position (via UI coordinates), scale, rotate, opacity controls
- Timeline visualization and play/pause/seek
- Submit to backend and poll progress

## API Endpoints
- `POST /upload` multipart form: `file` (video) and `metadata` (JSON string). Returns `{ "job_id": "<uuid>" }`.
- `GET /status/{job_id}` returns `{ "status": "queued|processing|done|failed", "progress_percent": 42, "message": "" }`.
- `GET /result/{job_id}` streams the rendered video.

Optional API key auth: set `API_KEY` env and include header `x-api-key: <key>` on `POST /upload`.

## Docker Compose
Start backend, Redis, and worker:
```
docker compose up --build
```
Backend on `http://localhost:8000`.

## Example curl
Upload:
```
curl -X POST "http://localhost:8000/upload" \
  -F "file=@data/assets/base_video.mp4" \
  -F "metadata=@demo/sample_metadata.json"
```

Poll status:
```
curl "http://localhost:8000/status/<job_id>"
```

Download result:
```
curl -L -o rendered.mp4 "http://localhost:8000/result/<job_id>"
```

## ffmpeg Filter Complex Mapping
Rendering composes overlays by building a `filter_complex` chain:
- Base: scale/pad to target resolution
- Text: `drawtext` with `x`, `y`, `fontsize`, `alpha`, optional `box`
- Image/Video: per-input `scale`, `rotate`, `format=rgba`, `colorchannelmixer` for opacity, then `overlay=x:y:enable='between(t,start,end)'`

Progress reporting parses `ffmpeg` stderr `time=HH:MM:SS.xx` and maps to percent by dividing by input duration from `ffprobe`.

## Demo Script
See `demo/DEMO_SCRIPT.md` for a short screen-recording walkthrough.

Share the demo recording and rendered video via a public drive link and send to `arush@buttercut.ai`.

## Linting & Tests
- Frontend: ESLint + Prettier
- Backend: ruff + black + pytest

Run backend tests:
```
cd backend
pytest -q
```

## Sample Overlay Presets
The app includes presets using the Drive assets:
- Text: `Happy New Year!` at `(0.25, 0.8)` from `2.5s` to `6.0s`
- Image: `overlay_image.png` at `(0.1, 0.1)` from `1.0s` to `4.0s`
- Video: `overlay_clip.mp4` at `(0.6, 0.2)` from `3.0s` to `8.0s`

## Ambiguities & Defaults
- Fonts: DejaVuSans installed in container via `fonts-dejavu-core`
- Asset resolution mapping uses normalized positions against output resolution
- When Drive links are used, ensure they are direct file URLs; otherwise download into `data/assets`
