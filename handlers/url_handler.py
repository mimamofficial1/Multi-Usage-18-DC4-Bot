"""handlers/url_handler.py"""
import os, re
from pathlib import Path
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters
from database.db import get_user, get_settings, get_task, set_task, clear_task
from helpers.downloader import (
    download_file, download_with_ytdlp,
    download_gdrive, shorten_url, unshorten_url, is_direct_link
)
from config import Config


def _url_keyboard(url: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton("1️⃣ Extract Archive (zip/rar/7z)", callback_data=f"url_extract|{url}")],
        [InlineKeyboardButton("2️⃣ 🔗 URL Uploader (Link → File)", callback_data=f"url_upload|{url}")],
        [InlineKeyboardButton("3️⃣ Link Shortener",               callback_data=f"url_shorten|{url}")],
        [InlineKeyboardButton("4️⃣ Link Unshortener",             callback_data=f"url_unshorten|{url}")],
        [InlineKeyboardButton("5️⃣ Google Drive Downloader",      callback_data=f"url_gdrive|{url}")],
        [InlineKeyboardButton("6️⃣ YT / Social Downloader",       callback_data=f"url_ytdl|{url}")],
        [InlineKeyboardButton("❌ Close",                          callback_data="url_close")],
    ]
    return InlineKeyboardMarkup(rows)


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg  = update.message
    uid  = msg.from_user.id
    user = get_user(uid)
    if user.get("banned"):
        return
    url = msg.text.strip()
    if not url.startswith("http"):
        return
    await msg.reply_text(
        f"🔗 <b>URL detected!</b>\n<code>{url[:80]}</code>\n\nChoose an option:",
        parse_mode="HTML",
        reply_markup=_url_keyboard(url)
    )


async def url_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = q.from_user.id
    await q.answer()

    if q.data == "url_close":
        await q.message.delete()
        return

    parts  = q.data.split("|", 1)
    action = parts[0]
    url    = parts[1] if len(parts) > 1 else ""
    chat   = q.message.chat_id
    s      = get_settings(uid)

    if action == "url_shorten":
        short = shorten_url(url)
        await q.message.reply_text(f"🔗 Shortened URL:\n<code>{short}</code>", parse_mode="HTML")

    elif action == "url_unshorten":
        final = unshorten_url(url)
        await q.message.reply_text(f"🔗 Final URL:\n<code>{final}</code>", parse_mode="HTML")

    elif action == "url_upload":
        pm = await q.message.reply_text("⏳ Downloading file from URL...")
        dest = os.path.join(Config.DOWNLOAD_DIR, str(uid))
        mode = s.get("url_mode", "httpx")
        path = download_file(url, dest) if mode == "httpx" else None
        if not path:
            path = download_file(url, dest)
        if path and os.path.exists(path):
            await context.bot.send_document(chat, open(path, "rb"),
                                            caption=f"✅ Downloaded: {Path(path).name}")
            os.remove(path)
        else:
            await q.message.reply_text("❌ Download failed. Check the URL.")
        await pm.delete()

    elif action == "url_gdrive":
        pm   = await q.message.reply_text("⏳ Downloading from Google Drive...")
        dest = os.path.join(Config.DOWNLOAD_DIR, str(uid))
        path = download_gdrive(url, dest)
        if path and os.path.exists(path):
            await context.bot.send_document(chat, open(path, "rb"),
                                            caption=f"✅ {Path(path).name}")
            os.remove(path)
        else:
            await q.message.reply_text("❌ Google Drive download failed.")
        await pm.delete()

    elif action == "url_ytdl":
        pm   = await q.message.reply_text("⏳ Downloading with yt-dlp...")
        dest = os.path.join(Config.DOWNLOAD_DIR, str(uid))
        fmt  = s.get("ytdl_filter", "mp4")
        path = download_with_ytdlp(url, dest, fmt)
        if path and os.path.exists(path):
            ext = Path(path).suffix.lower().lstrip(".")
            if ext in Config.VIDEO_FORMATS:
                await context.bot.send_video(chat, open(path, "rb"),
                                             caption=f"✅ {Path(path).name}",
                                             supports_streaming=True)
            elif ext in Config.AUDIO_FORMATS:
                await context.bot.send_audio(chat, open(path, "rb"),
                                             caption=f"✅ {Path(path).name}")
            else:
                await context.bot.send_document(chat, open(path, "rb"),
                                                caption=f"✅ {Path(path).name}")
            os.remove(path)
        else:
            await q.message.reply_text("❌ yt-dlp download failed. Check the URL.")
        await pm.delete()

    elif action == "url_extract":
        pm   = await q.message.reply_text("⏳ Downloading & extracting archive...")
        dest = os.path.join(Config.DOWNLOAD_DIR, str(uid))
        path = download_file(url, dest)
        if path and os.path.exists(path):
            out_dir = path + "_extracted"
            from helpers.ffmpeg_helper import extract_archive
            ok = extract_archive(path, out_dir)
            if ok:
                files = list(Path(out_dir).glob("*"))[:10]
                for f in files:
                    await context.bot.send_document(chat, open(str(f), "rb"))
            else:
                await q.message.reply_text("❌ Extraction failed.")
            os.remove(path)
        else:
            await q.message.reply_text("❌ Download failed.")
        await pm.delete()


async def bulk_url_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    task = get_task(uid)
    if task:
        kb = [[InlineKeyboardButton("🚫 Cancel Task", callback_data="bulk_cancel")]]
        await update.message.reply_text(
            "⚠️ Please wait until the previous task completes Or Cancel the previous task\n\n"
            "★ If you want Use, Then first cancel your previous task.\n\n"
            "★ Use command /cancel",
            reply_markup=InlineKeyboardMarkup(kb)
        )
        return
    await update.message.reply_text(
        "📋 <b>Bulk URL Uploader</b>\n\n"
        "Send multiple URLs, one per line.\n"
        "Format: <code>filename | url</code>\n\n"
        "Example:\n<code>myvideo.mp4 | https://example.com/video.mp4</code>\n\n"
        "Send /cancel to stop.",
        parse_mode="HTML"
    )
    set_task(uid, {"action": "bulk_url", "urls": []})
    context.user_data["waiting_for"] = "bulk_urls"


async def bulk_url_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    if q.data == "bulk_cancel":
        clear_task(q.from_user.id)
        await q.message.edit_text("✅ Task cancelled.")


def get_url_handlers():
    return [
        CommandHandler("bulk_url", bulk_url_cmd),
        CallbackQueryHandler(url_callback, pattern="^url_"),
        CallbackQueryHandler(bulk_url_callback, pattern="^bulk_"),
    ]
