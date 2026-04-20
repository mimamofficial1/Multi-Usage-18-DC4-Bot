from datetime import datetime, timedelta
from pymongo import MongoClient
from config import Config

_client = None
_db     = None

def get_db():
    global _client, _db
    if _db is None:
        _client = MongoClient(Config.MONGO_URI)
        _db     = _client["muzaffar_bot"]
    return _db

# ─────────────────────────── USERS ────────────────────────────────────

def get_user(user_id: int) -> dict:
    db   = get_db()
    user = db.users.find_one({"user_id": user_id})
    if not user:
        user = _create_user(user_id)
    return user

def _create_user(user_id: int) -> dict:
    db   = get_db()
    user = {
        "user_id":    user_id,
        "plan":       "free",
        "activated":  None,
        "expires":    None,
        "banned":     False,
        "settings": {
            "bulk_mode":    False,
            "thumbnail":    True,
            "rename_file":  True,
            "upload_type":  "document",   # document | audio | video
            "split_size":   "4GB",
            "url_mode":     "aria2c",
            "ytdl_filter":  "mp4",
        },
        "usettings": {
            "caption_adder":     False,
            "caption_text":      "",
            "words_remover":     False,
            "remove_words":      "",
            "rename_prefix":     "",
            "rename_suffix":     "",
            "words_replacer":    False,
            "replace_pairs":     "",
            "caption_formatter": False,
            "spoiler_video":     False,
        },
        "created_at": datetime.utcnow(),
    }
    db.users.insert_one(user)
    return user

def update_user(user_id: int, data: dict):
    get_db().users.update_one({"user_id": user_id}, {"$set": data}, upsert=True)

def activate_plan(user_id: int, plan: str, days: int):
    now     = datetime.utcnow()
    expires = now + timedelta(days=days)
    update_user(user_id, {
        "plan":      plan,
        "activated": now,
        "expires":   expires,
    })

def is_plan_active(user: dict) -> bool:
    if user.get("plan") == "free":
        return True
    expires = user.get("expires")
    if not expires:
        return False
    return datetime.utcnow() < expires

def ban_user(user_id: int):
    update_user(user_id, {"banned": True})

def unban_user(user_id: int):
    update_user(user_id, {"banned": False})

def get_banned_users() -> list:
    return list(get_db().users.find({"banned": True}))

def get_all_users() -> list:
    return list(get_db().users.find({}))

def get_users_count() -> int:
    return get_db().users.count_documents({})

# ─────────────────────────── SETTINGS ─────────────────────────────────

def get_settings(user_id: int) -> dict:
    return get_user(user_id).get("settings", {})

def update_settings(user_id: int, key: str, value):
    get_db().users.update_one(
        {"user_id": user_id},
        {"$set": {f"settings.{key}": value}},
        upsert=True,
    )

def get_usettings(user_id: int) -> dict:
    return get_user(user_id).get("usettings", {})

def update_usettings(user_id: int, key: str, value):
    get_db().users.update_one(
        {"user_id": user_id},
        {"$set": {f"usettings.{key}": value}},
        upsert=True,
    )

# ─────────────────────────── THUMBNAILS ───────────────────────────────

def save_thumb(user_id: int, file_id: str):
    get_db().thumbnails.update_one(
        {"user_id": user_id},
        {"$set": {"file_id": file_id}},
        upsert=True,
    )

def get_thumb(user_id: int) -> str | None:
    doc = get_db().thumbnails.find_one({"user_id": user_id})
    return doc["file_id"] if doc else None

def delete_thumb(user_id: int):
    get_db().thumbnails.delete_one({"user_id": user_id})

# ─────────────────────────── TASKS ────────────────────────────────────

def set_task(user_id: int, task: dict):
    get_db().tasks.update_one(
        {"user_id": user_id},
        {"$set": {"task": task, "created_at": datetime.utcnow()}},
        upsert=True,
    )

def get_task(user_id: int) -> dict | None:
    doc = get_db().tasks.find_one({"user_id": user_id})
    return doc["task"] if doc else None

def clear_task(user_id: int):
    get_db().tasks.delete_one({"user_id": user_id})
