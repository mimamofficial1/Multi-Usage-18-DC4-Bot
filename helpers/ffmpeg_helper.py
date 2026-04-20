"""
helpers/ffmpeg_helper.py
All FFmpeg-based media operations used by the bot.
"""
import os, subprocess, asyncio, time, math, shutil
from pathlib import Path

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = shutil.which("ffprobe") or "ffprobe"


# ─────────────────────── helpers ──────────────────────────────────────

def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr

def _unique(path: str) -> str:
    base, ext = os.path.splitext(path)
    return f"{base}_{int(time.time())}{ext}"

def probe(path: str) -> dict:
    """Return ffprobe json info."""
    import json
    rc, out, _ = _run([
        FFPROBE, "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", path,
    ])
    return json.loads(out) if rc == 0 else {}

def human_readable_info(path: str) -> str:
    """Return a text block with media info."""
    info = probe(path)
    fmt  = info.get("format", {})
    lines = [
        f"📁 <b>File:</b> <code>{os.path.basename(path)}</code>",
        f"📦 <b>Size:</b> {_fmt_size(int(fmt.get('size', 0)))}",
        f"⏱ <b>Duration:</b> {_fmt_dur(float(fmt.get('duration', 0)))}",
        f"🎞 <b>Format:</b> {fmt.get('format_long_name', 'N/A')}",
    ]
    for s in info.get("streams", []):
        ctype = s.get("codec_type", "?").upper()
        codec = s.get("codec_name", "?")
        if ctype == "VIDEO":
            lines.append(
                f"🎬 <b>Video:</b> {codec} {s.get('width')}x{s.get('height')} "
                f"@ {s.get('r_frame_rate','?')} fps"
            )
        elif ctype == "AUDIO":
            lines.append(
                f"🔊 <b>Audio:</b> {codec} {s.get('sample_rate','?')} Hz "
                f"ch:{s.get('channels','?')} lang:{s.get('tags',{}).get('language','?')}"
            )
        elif ctype == "SUBTITLE":
            lines.append(
                f"💬 <b>Sub:</b> {codec} lang:{s.get('tags',{}).get('language','?')}"
            )
    return "\n".join(lines)

def _fmt_size(b: int) -> str:
    for unit in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"

def _fmt_dur(secs: float) -> str:
    h = int(secs // 3600); secs %= 3600
    m = int(secs // 60);   s = int(secs % 60)
    return f"{h:02}:{m:02}:{s:02}"


# ─────────────────────── VIDEO OPERATIONS ─────────────────────────────

def remove_audio(src: str, out: str) -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-an", "-c:v", "copy", out])
    return rc == 0

def remove_subtitles(src: str, out: str) -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-sn", "-c", "copy", out])
    return rc == 0

def remove_audio_and_subs(src: str, out: str) -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-an", "-sn", "-c:v", "copy", out])
    return rc == 0

def extract_audio(src: str, out: str, fmt="mp3", quality="192k") -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-vn", "-b:a", quality, out])
    return rc == 0

def extract_subtitles(src: str, out: str, track: int = 0) -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, f"-map", f"0:s:{track}", out])
    return rc == 0

def mute_video(src: str, out: str) -> bool:
    return remove_audio(src, out)

def trim_video(src: str, out: str, start: str, end: str) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-ss", start, "-to", end,
        "-c", "copy", out
    ])
    return rc == 0

def merge_videos(inputs: list[str], out: str) -> bool:
    """Concatenate video files."""
    list_file = out + "_list.txt"
    with open(list_file, "w") as f:
        for p in inputs:
            f.write(f"file '{p}'\n")
    rc, _, _ = _run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", out
    ])
    os.remove(list_file)
    return rc == 0

def video_to_gif(src: str, out: str, fps: int = 10, scale: int = 480) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src,
        "-vf", f"fps={fps},scale={scale}:-1:flags=lanczos",
        "-loop", "0", out
    ])
    return rc == 0

def split_video(src: str, out_dir: str, segment_secs: int = 300) -> list[str]:
    """Split video into equal chunks."""
    os.makedirs(out_dir, exist_ok=True)
    out_pattern = os.path.join(out_dir, "part_%03d.mp4")
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src,
        "-c", "copy", "-map", "0",
        "-segment_time", str(segment_secs),
        "-f", "segment", "-reset_timestamps", "1",
        out_pattern,
    ])
    if rc != 0:
        return []
    return sorted(Path(out_dir).glob("part_*.mp4"))

def take_screenshot(src: str, out: str, timestamp: str = "00:00:05") -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-ss", timestamp, "-i", src,
        "-frames:v", "1", "-q:v", "2", out
    ])
    return rc == 0

def generate_sample(src: str, out: str, duration: int = 30) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-t", str(duration),
        "-c", "copy", out
    ])
    return rc == 0

def convert_video(src: str, out: str, vcodec="copy", acodec="copy") -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src,
        "-c:v", vcodec, "-c:a", acodec, out
    ])
    return rc == 0

def merge_video_audio(video: str, audio: str, out: str) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", video, "-i", audio,
        "-c:v", "copy", "-c:a", "aac", "-map", "0:v:0", "-map", "1:a:0",
        "-shortest", out
    ])
    return rc == 0

def merge_video_subtitle(video: str, sub: str, out: str) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", video, "-i", sub,
        "-c:v", "copy", "-c:a", "copy", "-c:s", "mov_text", out
    ])
    return rc == 0

def optimize_video(src: str, out: str, crf: int = 28) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-c:v", "libx264",
        "-crf", str(crf), "-preset", "fast", "-c:a", "aac", out
    ])
    return rc == 0


# ─────────────────────── AUDIO OPERATIONS ─────────────────────────────

def convert_audio(src: str, out: str, quality: str = "192k") -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-b:a", quality, out])
    return rc == 0

def slowed_reverb(src: str, out: str, speed: float = 0.85, reverb: float = 0.5) -> bool:
    # atempo < 0.5 needs chaining
    filter_str = f"atempo={speed},aecho=0.8:{reverb}:60:0.4"
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-af", filter_str, out
    ])
    return rc == 0

def audio_8d(src: str, out: str) -> bool:
    filter_str = (
        "apulsator=hz=0.125,aecho=0.8:0.9:1000:0.3,"
        "equalizer=f=440:t=o:w=2:g=3"
    )
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-af", filter_str, out])
    return rc == 0

def adjust_eq(src: str, out: str, volume=0, bass=0, treble=0) -> bool:
    af = f"volume={volume}dB,equalizer=f=80:t=o:w=1:g={bass},equalizer=f=8000:t=o:w=1:g={treble}"
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-af", af, out])
    return rc == 0

def bass_boost(src: str, out: str, gain: int = 5) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src,
        "-af", f"equalizer=f=80:t=o:w=1:g={gain}", out
    ])
    return rc == 0

def treble_boost(src: str, out: str, gain: int = 5) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src,
        "-af", f"equalizer=f=8000:t=o:w=1:g={gain}", out
    ])
    return rc == 0

def trim_audio(src: str, out: str, start: str, end: str) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-ss", start, "-to", end,
        "-c", "copy", out
    ])
    return rc == 0

def change_speed(src: str, out: str, speed: float = 1.0) -> bool:
    rc, _, _ = _run([
        FFMPEG, "-y", "-i", src, "-af", f"atempo={speed}", out
    ])
    return rc == 0

def change_volume(src: str, out: str, volume: int = 100) -> bool:
    vol = volume / 100
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-af", f"volume={vol}", out])
    return rc == 0

def merge_audio_files(inputs: list[str], out: str) -> bool:
    if not inputs:
        return False
    if len(inputs) == 1:
        import shutil as sh
        sh.copy(inputs[0], out)
        return True
    # concat demuxer
    list_file = out + "_alist.txt"
    with open(list_file, "w") as f:
        for p in inputs:
            f.write(f"file '{p}'\n")
    rc, _, _ = _run([
        FFMPEG, "-y", "-f", "concat", "-safe", "0",
        "-i", list_file, "-c", "copy", out
    ])
    os.remove(list_file)
    return rc == 0

def compress_audio(src: str, out: str, bitrate: str = "64k") -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, "-b:a", bitrate, out])
    return rc == 0


# ─────────────────────── SUBTITLE CONVERSION ──────────────────────────

def convert_subtitle(src: str, out: str) -> bool:
    rc, _, _ = _run([FFMPEG, "-y", "-i", src, out])
    return rc == 0


# ─────────────────────── ARCHIVE ──────────────────────────────────────

def create_archive(files: list[str], out: str, fmt: str = "zip", password: str = "") -> bool:
    import zipfile, tarfile
    try:
        if fmt == "zip":
            with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
                for f in files:
                    zf.write(f, os.path.basename(f))
        elif fmt in ("tar", "tar.gz"):
            mode = "w:gz" if fmt == "tar.gz" else "w"
            with tarfile.open(out, mode) as tf:
                for f in files:
                    tf.add(f, arcname=os.path.basename(f))
        elif fmt in ("7z", "rar"):
            cmd = ["7z", "a"]
            if password:
                cmd += [f"-p{password}"]
            cmd += [out] + files
            rc, _, _ = _run(cmd)
            return rc == 0
        return True
    except Exception:
        return False

def extract_archive(src: str, out_dir: str) -> bool:
    os.makedirs(out_dir, exist_ok=True)
    rc, _, _ = _run(["7z", "x", src, f"-o{out_dir}", "-y"])
    return rc == 0
