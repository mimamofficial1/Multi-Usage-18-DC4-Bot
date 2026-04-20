"""
helpers/downloader.py
Download files from URLs using httpx (pure Python).
"""
import os, subprocess, time
from pathlib import Path
from config import Config


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def download_file(url: str, dest_dir: str, filename: str | None = None) -> str | None:
    """Download a direct URL using httpx. Returns output file path or None."""
    import httpx
    os.makedirs(dest_dir, exist_ok=True)
    try:
        with httpx.stream("GET", url, follow_redirects=True, timeout=300) as r:
            r.raise_for_status()
            if not filename:
                cd = r.headers.get("content-disposition", "")
                if "filename=" in cd:
                    filename = cd.split("filename=")[-1].strip().strip('"')
                else:
                    filename = Path(url.split("?")[0]).name or f"file_{int(time.time())}"
            out_path = os.path.join(dest_dir, filename)
            with open(out_path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=1024 * 1024):
                    f.write(chunk)
        return out_path
    except Exception as e:
        print(f"[download_file] Error: {e}")
        return None


def download_with_ytdlp(url: str, dest_dir: str, fmt: str = "mp4") -> str | None:
    """Download YouTube/Instagram/Spotify etc via yt-dlp."""
    os.makedirs(dest_dir, exist_ok=True)
    out_tmpl = os.path.join(dest_dir, "%(title)s.%(ext)s")
    cmd = ["yt-dlp", url, "-o", out_tmpl,
           "--no-playlist", "--merge-output-format", fmt,
           "-f", f"bestvideo[ext={fmt}]+bestaudio/best[ext={fmt}]/best"]
    rc, out, err = _run(cmd)
    if rc == 0:
        files = list(Path(dest_dir).glob("*"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return str(files[0]) if files else None
    return None


def download_gdrive(url: str, dest_dir: str) -> str | None:
    """Download from Google Drive using gdown."""
    os.makedirs(dest_dir, exist_ok=True)
    rc, out, _ = _run(["gdown", "--fuzzy", url, "-O", dest_dir])
    if rc == 0:
        files = list(Path(dest_dir).glob("*"))
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return str(files[0]) if files else None
    return None


def shorten_url(url: str) -> str:
    import urllib.request
    try:
        api = f"https://tinyurl.com/api-create.php?url={url}"
        with urllib.request.urlopen(api, timeout=10) as r:
            return r.read().decode()
    except Exception:
        return url


def unshorten_url(url: str) -> str:
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.url
    except Exception:
        return url


def is_direct_link(url: str) -> bool:
    import urllib.request
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=8) as r:
            ct = r.headers.get("Content-Type", "")
            return not ct.startswith("text/html")
    except Exception:
        return False
