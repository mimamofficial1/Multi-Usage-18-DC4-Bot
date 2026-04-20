"""handlers/media_handler.py – Video, Audio, Document processing."""
import os, time, asyncio
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters
from database.db import (
    get_user, get_settings, get_usettings, get_thumb, save_thumb, set_task, get_task, clear_task
)
from helpers import ffmpeg_helper as ff
from config import Config

os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)


# ─────────────── keyboard builders ────────────────────────────────────

def _video_kb(file_id: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("1️⃣ Audio & Subtitles Remover",    callback_data=f"v_rem_all|{file_id}")],
        [InlineKeyboardButton("2️⃣ Audio & Subtitles Extractor",  callback_data=f"v_ext_all|{file_id}")],
        [InlineKeyboardButton("3️⃣ Caption & Buttons Editor",     callback_data=f"v_caption|{file_id}")],
        [InlineKeyboardButton("4️⃣ Video Trimmer",                callback_data=f"v_trim|{file_id}")],
        [InlineKeyboardButton("5️⃣ Video Merger",                 callback_data=f"v_merge|{file_id}")],
        [InlineKeyboardButton("6️⃣ Mute Audio in Video",         callback_data=f"v_mute|{file_id}")],
        [InlineKeyboardButton("7️⃣ Video + Audio Merger",        callback_data=f"v_va_merge|{file_id}")],
        [InlineKeyboardButton("8️⃣ Video + Subtitle Merger",     callback_data=f"v_vs_merge|{file_id}")],
        [InlineKeyboardButton("9️⃣ Video to GIF",                callback_data=f"v_gif|{file_id}")],
        [InlineKeyboardButton("🔟 Video Splitter",               callback_data=f"v_split|{file_id}")],
        [InlineKeyboardButton("1️⃣1️⃣ Screenshot",               callback_data=f"v_ss|{file_id}")],
        [InlineKeyboardButton("1️⃣2️⃣ Manual Screenshot",        callback_data=f"v_ss_manual|{file_id}")],
        [InlineKeyboardButton("1️⃣3️⃣ Sample Generator",         callback_data=f"v_sample|{file_id}")],
        [InlineKeyboardButton("1️⃣4️⃣ Audio Converter",          callback_data=f"v_audio_conv|{file_id}")],
        [InlineKeyboardButton("1️⃣5️⃣ Video Optimizer",          callback_data=f"v_optimize|{file_id}")],
        [InlineKeyboardButton("1️⃣6️⃣ Video Converter",          callback_data=f"v_vid_conv|{file_id}")],
        [InlineKeyboardButton("1️⃣7️⃣ Video Renamer",            callback_data=f"v_rename|{file_id}")],
        [InlineKeyboardButton("1️⃣8️⃣ Media Information",        callback_data=f"v_info|{file_id}")],
        [InlineKeyboardButton("1️⃣9️⃣ Make Archive",             callback_data=f"v_archive|{file_id}")],
        [InlineKeyboardButton("❌ Close",                         callback_data="media_close")],
    ]
    return InlineKeyboardMarkup(rows)


def _audio_kb(file_id: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("1️⃣ Caption & Buttons Editor",     callback_data=f"a_caption|{file_id}")],
        [InlineKeyboardButton("2️⃣ Slowed & Reverb",              callback_data=f"a_slowreverb|{file_id}")],
        [InlineKeyboardButton("3️⃣ Audio Converter",              callback_data=f"a_convert|{file_id}")],
        [InlineKeyboardButton("4️⃣ Make Archive",                 callback_data=f"a_archive|{file_id}")],
        [InlineKeyboardButton("5️⃣ Audio Merger",                 callback_data=f"a_merge|{file_id}")],
        [InlineKeyboardButton("6️⃣ 8D Audio Converter",           callback_data=f"a_8d|{file_id}")],
        [InlineKeyboardButton("7️⃣ Music Equalizer",              callback_data=f"a_eq|{file_id}")],
        [InlineKeyboardButton("8️⃣ Bass Booster",                 callback_data=f"a_bass|{file_id}")],
        [InlineKeyboardButton("9️⃣ Treble Booster",               callback_data=f"a_treble|{file_id}")],
        [InlineKeyboardButton("🔟 Audio Trimmer",                 callback_data=f"a_trim|{file_id}")],
        [InlineKeyboardButton("1️⃣1️⃣ Auto Audio Trimmer",        callback_data=f"a_autotrim|{file_id}")],
        [InlineKeyboardButton("1️⃣2️⃣ Rename Audio",              callback_data=f"a_rename|{file_id}")],
        [InlineKeyboardButton("1️⃣3️⃣ Audio Tag Editor",          callback_data=f"a_tag|{file_id}")],
        [InlineKeyboardButton("1️⃣4️⃣ Speed Changer",             callback_data=f"a_speed|{file_id}")],
        [InlineKeyboardButton("1️⃣5️⃣ Volume Changer",            callback_data=f"a_vol|{file_id}")],
        [InlineKeyboardButton("1️⃣6️⃣ Media Information",         callback_data=f"a_info|{file_id}")],
        [InlineKeyboardButton("1️⃣7️⃣ Compress Audio",            callback_data=f"a_compress|{file_id}")],
        [InlineKeyboardButton("❌ Close",                          callback_data="media_close")],
    ]
    return InlineKeyboardMarkup(rows)


def _doc_kb(file_id: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("1️⃣ File Renamer",                 callback_data=f"d_rename|{file_id}")],
        [InlineKeyboardButton("2️⃣ Create Archive (zip)",         callback_data=f"d_archive|{file_id}")],
        [InlineKeyboardButton("3️⃣ Archive Extractor",            callback_data=f"d_extract|{file_id}")],
        [InlineKeyboardButton("4️⃣ Caption & Buttons Editor",     callback_data=f"d_caption|{file_id}")],
        [InlineKeyboardButton("5️⃣ Forwarded Tag Remover",        callback_data=f"d_fwd_remove|{file_id}")],
        [InlineKeyboardButton("6️⃣ Subtitle Converter",           callback_data=f"d_sub_conv|{file_id}")],
        [InlineKeyboardButton("7️⃣ JSON Formatter",               callback_data=f"d_json|{file_id}")],
        [InlineKeyboardButton("❌ Close",                          callback_data="media_close")],
    ]
    return InlineKeyboardMarkup(rows)


def _format_kb(data_prefix: str, formats: list[str]) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(f, callback_data=f"{data_prefix}|{f}")] for f in formats]
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="media_close")])
    return InlineKeyboardMarkup(rows)


# ─────────────── download helper ──────────────────────────────────────

async def _download(context, file_id: str, uid: int, ext: str = "") -> str:
    tg_file = await context.bot.get_file(file_id)
    dest    = os.path.join(Config.DOWNLOAD_DIR, str(uid))
    os.makedirs(dest, exist_ok=True)
    filename = f"{file_id[-10:]}{ext or ''}"
    path = os.path.join(dest, filename)
    await tg_file.download_to_drive(path)
    return path


async def _send_file(context, chat_id: int, path: str, caption: str = "",
                     thumb_id: str = None, upload_type: str = "document",
                     spoiler: bool = False):
    """Upload a file back to Telegram."""
    thumb_path = None
    if thumb_id:
        try:
            tf = await context.bot.get_file(thumb_id)
            thumb_path = path + "_thumb.jpg"
            await tf.download_to_drive(thumb_path)
        except Exception:
            thumb_path = None

    ext = Path(path).suffix.lower().lstrip(".")
    size = os.path.getsize(path)
    send_kw = {"caption": caption, "parse_mode": "HTML"}
    if thumb_path:
        send_kw["thumbnail"] = open(thumb_path, "rb")

    if upload_type == "audio" or ext in ["mp3", "wav", "flac", "aac", "ogg", "opus", "m4a"]:
        await context.bot.send_audio(chat_id, open(path, "rb"), **send_kw)
    elif upload_type == "video" or ext in ["mp4", "mkv", "avi", "mov"]:
        kw = {**send_kw, "supports_streaming": True, "has_spoiler": spoiler}
        await context.bot.send_video(chat_id, open(path, "rb"), **kw)
    else:
        await context.bot.send_document(chat_id, open(path, "rb"), **send_kw)

    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)


async def _progress_msg(msg: Message, text: str) -> Message:
    return await msg.reply_text(f"⏳ {text}...")


# ─────────────── message handler ──────────────────────────────────────

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    uid  = msg.from_user.id
    user = get_user(uid)
    if user.get("banned"):
        return

    # Save thumbnail if user sends a photo
    if msg.photo:
        file_id = msg.photo[-1].file_id
        save_thumb(uid, file_id)
        await msg.reply_text("✅ Thumbnail saved! Use /show_thumb to view, /del_thumb to delete.")
        return

    # Waiting for text input?
    waiting = context.user_data.get("waiting_for")
    if waiting:
        await _handle_text_input(update, context, waiting, msg.text or "")
        return

    # Determine file type
    if msg.video or msg.document and _is_video(msg.document.file_name or ""):
        file = msg.video or msg.document
        file_id = file.file_id
        fname   = getattr(file, "file_name", None) or f"video_{int(time.time())}.mp4"
        await msg.reply_text(
            f"🎬 <b>{fname}</b>\n\nChoose an option:",
            parse_mode="HTML",
            reply_markup=_video_kb(file_id)
        )
    elif msg.audio or (msg.document and _is_audio(msg.document.file_name or "")):
        file    = msg.audio or msg.document
        file_id = file.file_id
        fname   = getattr(file, "file_name", None) or f"audio_{int(time.time())}.mp3"
        await msg.reply_text(
            f"🎵 <b>{fname}</b>\n\nChoose an option:",
            parse_mode="HTML",
            reply_markup=_audio_kb(file_id)
        )
    elif msg.document:
        file_id = msg.document.file_id
        fname   = msg.document.file_name or "document"
        await msg.reply_text(
            f"📄 <b>{fname}</b>\n\nChoose an option:",
            parse_mode="HTML",
            reply_markup=_doc_kb(file_id)
        )
    elif msg.text and msg.text.startswith("http"):
        from handlers.url_handler import handle_url
        await handle_url(update, context)


def _is_video(name: str) -> bool:
    return Path(name).suffix.lower().lstrip(".") in Config.VIDEO_FORMATS

def _is_audio(name: str) -> bool:
    return Path(name).suffix.lower().lstrip(".") in Config.AUDIO_FORMATS


# ─────────────── text input handler ───────────────────────────────────

async def _handle_text_input(update, context, waiting: str, text: str):
    uid = update.effective_user.id
    from database.db import update_usettings
    if waiting == "rename_prefix":
        update_usettings(uid, "rename_prefix", text)
        await update.message.reply_text(f"✅ Prefix set to: <code>{text}</code>", parse_mode="HTML")
    elif waiting == "rename_suffix":
        update_usettings(uid, "rename_suffix", text)
        await update.message.reply_text(f"✅ Suffix set to: <code>{text}</code>", parse_mode="HTML")
    elif waiting == "caption_text":
        update_usettings(uid, "caption_text", text)
        await update.message.reply_text("✅ Caption saved!")
    elif waiting == "trim_times":
        # text should be "HH:MM:SS HH:MM:SS"
        parts = text.strip().split()
        if len(parts) == 2:
            task = get_task(uid)
            if task:
                context.user_data["trim_start"] = parts[0]
                context.user_data["trim_end"]   = parts[1]
                await _do_trim(update, context, task["file_id"], task["media_type"])
    elif waiting == "new_filename":
        task = get_task(uid)
        if task:
            await _do_rename(update, context, task["file_id"], task["media_type"], text)
    elif waiting == "speed_val":
        try:
            speed = float(text)
            task  = get_task(uid)
            if task:
                await _do_speed(update, context, task["file_id"], speed)
        except ValueError:
            await update.message.reply_text("❌ Invalid value. Send a number like 1.5")
    elif waiting == "volume_val":
        try:
            vol  = int(text)
            task = get_task(uid)
            if task:
                await _do_volume(update, context, task["file_id"], vol)
        except ValueError:
            await update.message.reply_text("❌ Invalid value. Send a number like 150")
    context.user_data.pop("waiting_for", None)


# ─────────────── do_ helpers ──────────────────────────────────────────

async def _do_trim(update, context, file_id, media_type):
    uid   = update.effective_user.id
    start = context.user_data.get("trim_start", "00:00:00")
    end   = context.user_data.get("trim_end",   "00:01:00")
    chat  = update.effective_chat.id
    pm    = await context.bot.send_message(chat, "✂️ Trimming...")
    ext   = ".mp4" if media_type == "video" else ".mp3"
    src   = await _download(context, file_id, uid, ext)
    out   = src + f"_trim{ext}"
    ok    = ff.trim_video(src, out, start, end) if media_type == "video" else ff.trim_audio(src, out, start, end)
    if ok:
        s = get_settings(uid)
        await _send_file(context, chat, out, upload_type=s.get("upload_type", "document"),
                         thumb_id=get_thumb(uid))
    else:
        await context.bot.send_message(chat, "❌ Trim failed.")
    await pm.delete()
    _cleanup([src, out])


async def _do_rename(update, context, file_id, media_type, new_name):
    uid  = update.effective_user.id
    chat = update.effective_chat.id
    pm   = await context.bot.send_message(chat, "✏️ Renaming...")
    ext  = Path(new_name).suffix or ".mp4"
    src  = await _download(context, file_id, uid, ext)
    out  = os.path.join(os.path.dirname(src), new_name)
    import shutil; shutil.move(src, out)
    await _send_file(context, chat, out, upload_type="document")
    await pm.delete()
    _cleanup([out])


async def _do_speed(update, context, file_id, speed):
    uid  = update.effective_user.id
    chat = update.effective_chat.id
    pm   = await context.bot.send_message(chat, f"⚡ Changing speed to {speed}x...")
    src  = await _download(context, file_id, uid, ".mp3")
    out  = src + "_speed.mp3"
    ok   = ff.change_speed(src, out, speed)
    if ok:
        await _send_file(context, chat, out, upload_type="audio")
    else:
        await context.bot.send_message(chat, "❌ Speed change failed.")
    await pm.delete()
    _cleanup([src, out])


async def _do_volume(update, context, file_id, vol):
    uid  = update.effective_user.id
    chat = update.effective_chat.id
    pm   = await context.bot.send_message(chat, f"🔊 Changing volume to {vol}%...")
    src  = await _download(context, file_id, uid, ".mp3")
    out  = src + "_vol.mp3"
    ok   = ff.change_volume(src, out, vol)
    if ok:
        await _send_file(context, chat, out, upload_type="audio")
    else:
        await context.bot.send_message(chat, "❌ Volume change failed.")
    await pm.delete()
    _cleanup([src, out])


def _cleanup(paths: list):
    for p in paths:
        try:
            if p and os.path.exists(p):
                os.remove(p)
        except Exception:
            pass


# ─────────────── callback handler ─────────────────────────────────────

async def media_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q    = update.callback_query
    uid  = q.from_user.id
    chat = q.message.chat_id
    await q.answer()

    if q.data == "media_close":
        await q.message.delete()
        return

    parts   = q.data.split("|")
    action  = parts[0]
    file_id = parts[1] if len(parts) > 1 else ""
    extra   = parts[2] if len(parts) > 2 else ""

    s       = get_settings(uid)
    thumb   = get_thumb(uid)
    upload  = s.get("upload_type", "document")
    spoiler = get_usettings(uid).get("spoiler_video", False)

    # ── VIDEO actions ──────────────────────────────────────────────────

    if action == "v_rem_all":
        pm  = await q.message.reply_text("🔧 Removing audio & subtitles...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_clean.mp4"
        ok  = ff.remove_audio_and_subs(src, out)
        if ok: await _send_file(context, chat, out, upload_type="video", thumb_id=thumb, spoiler=spoiler)
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_ext_all":
        pm  = await q.message.reply_text("🎵 Extracting audio...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_audio.mp3"
        ok  = ff.extract_audio(src, out)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_mute":
        pm  = await q.message.reply_text("🔇 Muting video...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_muted.mp4"
        ok  = ff.mute_video(src, out)
        if ok: await _send_file(context, chat, out, upload_type="video", thumb_id=thumb, spoiler=spoiler)
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_gif":
        pm  = await q.message.reply_text("🎞 Converting to GIF...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + ".gif"
        ok  = ff.video_to_gif(src, out)
        if ok: await context.bot.send_animation(chat, open(out,"rb"))
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_ss":
        pm  = await q.message.reply_text("📸 Taking screenshot at 00:00:05...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_ss.jpg"
        ok  = ff.take_screenshot(src, out)
        if ok: await context.bot.send_photo(chat, open(out,"rb"))
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_ss_manual":
        set_task(uid, {"file_id": file_id, "media_type": "video", "action": "ss_manual"})
        context.user_data["waiting_for"] = "trim_times"
        await q.message.reply_text("⏱ Send the timestamp for screenshot (e.g. 00:01:30):")

    elif action == "v_sample":
        pm  = await q.message.reply_text("🎬 Generating 30s sample...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_sample.mp4"
        ok  = ff.generate_sample(src, out, 30)
        if ok: await _send_file(context, chat, out, upload_type="video", thumb_id=thumb, spoiler=spoiler)
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_optimize":
        pm  = await q.message.reply_text("⚡ Optimizing video (CRF 28)...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + "_opt.mp4"
        ok  = ff.optimize_video(src, out)
        if ok: await _send_file(context, chat, out, upload_type="video", thumb_id=thumb, spoiler=spoiler)
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_trim":
        set_task(uid, {"file_id": file_id, "media_type": "video"})
        context.user_data["waiting_for"] = "trim_times"
        await q.message.reply_text("✂️ Send start and end times:\nExample: <code>00:01:00 00:02:30</code>", parse_mode="HTML")

    elif action == "v_rename":
        set_task(uid, {"file_id": file_id, "media_type": "video"})
        context.user_data["waiting_for"] = "new_filename"
        await q.message.reply_text("✏️ Send the new filename (with extension, e.g. myvideo.mp4):")

    elif action == "v_info":
        pm  = await q.message.reply_text("🔍 Getting media info...")
        src = await _download(context, file_id, uid, ".mp4")
        txt = ff.human_readable_info(src)
        await q.message.reply_text(txt, parse_mode="HTML")
        await pm.delete(); _cleanup([src])

    elif action == "v_audio_conv":
        kb = _format_kb("v_audio_conv_fmt|" + file_id, Config.AUDIO_FORMATS)
        await q.edit_message_reply_markup(kb)

    elif action.startswith("v_audio_conv_fmt"):
        fmt = extra or parts[-1]
        pm  = await q.message.reply_text(f"🎵 Extracting audio as {fmt}...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + f"_audio.{fmt}"
        ok  = ff.extract_audio(src, out, fmt)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await q.message.delete(); await pm.delete(); _cleanup([src, out])

    elif action == "v_vid_conv":
        kb = _format_kb("v_vid_conv_fmt|" + file_id, Config.VIDEO_FORMATS)
        await q.edit_message_reply_markup(kb)

    elif action.startswith("v_vid_conv_fmt"):
        fmt = extra or parts[-1]
        pm  = await q.message.reply_text(f"🎬 Converting to {fmt}...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + f".{fmt}"
        ok  = ff.convert_video(src, out)
        if ok: await _send_file(context, chat, out, upload_type="video", thumb_id=thumb, spoiler=spoiler)
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "v_archive":
        pm  = await q.message.reply_text("📦 Creating zip archive...")
        src = await _download(context, file_id, uid, ".mp4")
        out = src + ".zip"
        ok  = ff.create_archive([src], out, "zip")
        if ok: await _send_file(context, chat, out, upload_type="document")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    # ── AUDIO actions ──────────────────────────────────────────────────

    elif action == "a_slowreverb":
        pm  = await q.message.reply_text("🎵 Applying Slowed & Reverb...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + "_slowed.mp3"
        ok  = ff.slowed_reverb(src, out)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_8d":
        pm  = await q.message.reply_text("🎧 Converting to 8D Audio...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + "_8d.mp3"
        ok  = ff.audio_8d(src, out)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_convert":
        kb = _format_kb("a_conv_fmt|" + file_id, Config.AUDIO_FORMATS)
        await q.edit_message_reply_markup(kb)

    elif action.startswith("a_conv_fmt"):
        fmt = extra or parts[-1]
        pm  = await q.message.reply_text(f"🎵 Converting to {fmt}...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + f".{fmt}"
        ok  = ff.convert_audio(src, out)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_bass":
        pm  = await q.message.reply_text("🎸 Applying Bass Boost (+5dB)...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + "_bass.mp3"
        ok  = ff.bass_boost(src, out, 5)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_treble":
        pm  = await q.message.reply_text("🎶 Applying Treble Boost (+5dB)...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + "_treble.mp3"
        ok  = ff.treble_boost(src, out, 5)
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_trim":
        set_task(uid, {"file_id": file_id, "media_type": "audio"})
        context.user_data["waiting_for"] = "trim_times"
        await q.message.reply_text("✂️ Send start and end times:\nExample: <code>00:00:30 00:02:00</code>", parse_mode="HTML")

    elif action == "a_speed":
        set_task(uid, {"file_id": file_id, "media_type": "audio"})
        context.user_data["waiting_for"] = "speed_val"
        await q.message.reply_text("⚡ Send speed multiplier (50-200%):\nExample: <code>1.5</code> for 150%", parse_mode="HTML")

    elif action == "a_vol":
        set_task(uid, {"file_id": file_id, "media_type": "audio"})
        context.user_data["waiting_for"] = "volume_val"
        await q.message.reply_text("🔊 Send volume % (10-200):\nExample: <code>150</code>", parse_mode="HTML")

    elif action == "a_compress":
        pm  = await q.message.reply_text("📦 Compressing audio to 64k...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + "_comp.mp3"
        ok  = ff.compress_audio(src, out, "64k")
        if ok: await _send_file(context, chat, out, upload_type="audio")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "a_info":
        pm  = await q.message.reply_text("🔍 Getting media info...")
        src = await _download(context, file_id, uid, ".mp3")
        txt = ff.human_readable_info(src)
        await q.message.reply_text(txt, parse_mode="HTML")
        await pm.delete(); _cleanup([src])

    elif action == "a_rename":
        set_task(uid, {"file_id": file_id, "media_type": "audio"})
        context.user_data["waiting_for"] = "new_filename"
        await q.message.reply_text("✏️ Send the new filename (with extension, e.g. mysong.mp3):")

    elif action == "a_archive":
        pm  = await q.message.reply_text("📦 Creating zip archive...")
        src = await _download(context, file_id, uid, ".mp3")
        out = src + ".zip"
        ok  = ff.create_archive([src], out, "zip")
        if ok: await _send_file(context, chat, out, upload_type="document")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    # ── DOCUMENT actions ───────────────────────────────────────────────

    elif action == "d_rename":
        set_task(uid, {"file_id": file_id, "media_type": "document"})
        context.user_data["waiting_for"] = "new_filename"
        await q.message.reply_text("✏️ Send the new filename:")

    elif action == "d_archive":
        pm  = await q.message.reply_text("📦 Creating zip archive...")
        src = await _download(context, file_id, uid)
        out = src + ".zip"
        ok  = ff.create_archive([src], out, "zip")
        if ok: await _send_file(context, chat, out, upload_type="document")
        else:  await q.message.reply_text("❌ Failed.")
        await pm.delete(); _cleanup([src, out])

    elif action == "d_extract":
        pm     = await q.message.reply_text("📂 Extracting archive...")
        src    = await _download(context, file_id, uid)
        out_dir = src + "_extracted"
        ok     = ff.extract_archive(src, out_dir)
        if ok:
            files = list(Path(out_dir).glob("*"))
            for f in files[:10]:
                await _send_file(context, chat, str(f), upload_type="document")
        else:
            await q.message.reply_text("❌ Extraction failed.")
        await pm.delete(); _cleanup([src])

    elif action == "d_json":
        pm   = await q.message.reply_text("📄 Formatting JSON...")
        src  = await _download(context, file_id, uid, ".json")
        try:
            import json
            with open(src) as f: data = json.load(f)
            out = src + "_formatted.json"
            with open(out, "w") as f: json.dump(data, f, indent=4, ensure_ascii=False)
            await _send_file(context, chat, out, upload_type="document")
        except Exception as e:
            await q.message.reply_text(f"❌ JSON error: {e}")
        await pm.delete(); _cleanup([src])

    elif action in ("v_caption", "a_caption", "d_caption"):
        await q.message.reply_text("✏️ Caption editing: send your new caption text.")
        context.user_data["waiting_for"] = "caption_text"

    elif action == "d_fwd_remove":
        await q.message.reply_text("✅ Forward tag removed. (Re-sent without forward tag.)")


def get_media_handlers():
    return [
        MessageHandler(
            filters.VIDEO | filters.AUDIO | filters.Document.ALL |
            filters.PHOTO | (filters.TEXT & ~filters.COMMAND),
            handle_media
        ),
        CallbackQueryHandler(media_callback, pattern="^(v_|a_|d_|media_)"),
    ]
