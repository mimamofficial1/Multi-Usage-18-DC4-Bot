import os

class Config:
    # ── Bot Credentials ──────────────────────────────────────────────
    BOT_TOKEN   = os.environ.get("BOT_TOKEN", "")
    MONGO_URI   = os.environ.get("MONGO_URI", "")

    # ── Admin / Channels ─────────────────────────────────────────────
    ADMIN_IDS   = list(map(int, os.environ.get("ADMIN_IDS", "0").split(",")))
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "0"))   # optional

    # ── Paths ────────────────────────────────────────────────────────
    DOWNLOAD_DIR = "/tmp/muzaffar_bot"

    # ── Limits ───────────────────────────────────────────────────────
    FREE_PLAN_SIZE    = 2  * 1024 * 1024 * 1024   # 2 GB
    STANDARD_PLAN_SIZE= 4  * 1024 * 1024 * 1024   # 4 GB

    # ── Plans ────────────────────────────────────────────────────────
    PLANS = {
        "free":     {"name": "Free",     "days": 0,  "price": 0},
        "standard": {"name": "Standard", "days": 30, "price": 99},
        "premium":  {"name": "Premium",  "days": 30, "price": 199},
    }

    # ── Supported formats ────────────────────────────────────────────
    VIDEO_FORMATS    = ["mp4", "mkv", "avi", "m4v", "mov", "webm"]
    AUDIO_FORMATS    = ["mp3", "wav", "flac", "aac", "ogg", "opus", "m4a", "wma", "ac3"]
    ARCHIVE_FORMATS  = ["zip", "rar", "7z", "tar", "tar.gz"]
    SUBTITLE_FORMATS = ["srt", "vtt", "ass", "sbv"]
