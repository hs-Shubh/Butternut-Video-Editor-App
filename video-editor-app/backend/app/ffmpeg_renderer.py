import os
import shlex
import subprocess
import tempfile
from typing import Any

from .models import Metadata, Overlay
from .storage import get_asset_path


def ffprobe_duration(path: str) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        path,
    ]
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode().strip()
    try:
        return float(out)
    except Exception:
        return 0.0


def build_filter_complex(meta: Metadata, inputs: list[str]) -> tuple[str, list[str]]:
    filters: list[str] = []
    maps: list[str] = []
    v_label = "[v0]"
    a_map = "0:a?"

    filters.append(
        f"[0:v]scale={meta.resolution.width}:{meta.resolution.height}:force_original_aspect_ratio=decrease,pad={meta.resolution.width}:{meta.resolution.height}:(ow-iw)/2:(oh-ih)/2[v0]"
    )

    overlays = sorted(meta.overlays, key=lambda o: o.z_index)
    next_index = 1
    for o in overlays:
        if o.type == "text":
            fontsize = o.font_size or 36
            x = int(o.position.x * meta.resolution.width)
            y = int(o.position.y * meta.resolution.height)
            enabled = f"between(t\\,{o.start_time}\\,{o.end_time})"
            bg = ":box=1:boxcolor=black@0.5:boxborderw=10" if o.background_box else ""
            alpha = max(0.0, min(1.0, o.opacity))
            draw = (
                f"{v_label}drawtext=text={shlex.quote(o.content)}:x={x}:y={y}:fontsize={fontsize}:fontcolor=white:alpha={alpha}{bg}:enable={enabled}[v{next_index}]"
            )
            filters.append(draw)
            v_label = f"[v{next_index}]"
            next_index += 1
        else:
            src_idx = len(inputs)
            inputs.append(o.content)
            asset_path = get_asset_path(o.content)
            input_ref = f"[{src_idx}:v]"
            scale_factor = o.scale
            rot = (o.rotation or 0.0) * 3.14159265 / 180.0
            alpha = max(0.0, min(1.0, o.opacity))
            w = meta.resolution.width
            h = meta.resolution.height
            x = int(o.position.x * w)
            y = int(o.position.y * h)
            enable = f"between(t\\,{o.start_time}\\,{o.end_time})"
            prep = (
                f"{input_ref}scale=iw*{scale_factor}:ih*{scale_factor},rotate={rot}:c=none,format=rgba,colorchannelmixer=aa={alpha}[ov{src_idx}]"
            )
            filters.append(prep)
            filters.append(
                f"{v_label}[ov{src_idx}]overlay={x}:{y}:enable={enable}[v{next_index}]"
            )
            v_label = f"[v{next_index}]"
            next_index += 1

    maps.append(v_label)
    maps.append(a_map)
    return ",".join(filters), maps


def render_ffmpeg(
    input_video: str,
    meta: Metadata,
    output_path: str,
    progress_cb,
) -> None:
    duration = ffprobe_duration(input_video)
    inputs = [os.path.abspath(input_video)]
    for o in meta.overlays:
        if o.type in ("image", "video"):
            local = get_asset_path(o.content)
            if local:
                inputs.append(os.path.abspath(local))
            else:
                inputs.append(o.content)
    fc, maps = build_filter_complex(meta, inputs)

    cmd = ["ffmpeg", "-y"]
    for p in inputs:
        cmd += ["-i", p]
    cmd += ["-filter_complex", fc]
    cmd += ["-map", maps[0]]
    if maps[1]:
        cmd += ["-map", maps[1]]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "20"]
    cmd += ["-pix_fmt", "yuv420p", output_path]

    proc = subprocess.Popen(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    if not proc.stderr:
        return
    stderr_lines = []
    for line in proc.stderr:
        stderr_lines.append(line)
        if "time=" in line:
            try:
                from .utils import parse_ffmpeg_time

                t = parse_ffmpeg_time(line)
                if duration > 0:
                    pct = max(0, min(100, int((t / duration) * 100)))
                    progress_cb(pct, "processing")
            except Exception:
                pass
    rc = proc.wait()
    if rc != 0:
        stderr_content = ''.join(stderr_lines[-20:])  # Last 20 lines of stderr
        raise RuntimeError(f"ffmpeg failed: {stderr_content}")
