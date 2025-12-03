import re


def parse_ffmpeg_time(ts: str) -> float:
    m = re.search(r"time=(\d\d):(\d\d):(\d\d)\.?(\d+)?", ts)
    if not m:
        return 0.0
    h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
    ms = m.group(4)
    frac = float(f"0.{ms}") if ms else 0.0
    return h * 3600 + mi * 60 + s + frac


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))
