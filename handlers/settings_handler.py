"""handlers/settings_handler.py"""
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.db import get_settings, update_settings, get_usettings, update_usettings, get_user


def _settings_keyboard(uid: int) -> InlineKeyboardMarkup:
    s = get_settings(uid)
    rows = [
        [InlineKeyboardButton(
            f"📁 Bulk Mode : {'On' if s.get('bulk_mode') else 'Off'}",
            callback_data="stg_bulk_mode"
        )],
        [InlineKeyboardButton(
            f"🖼 Thumbnail : {'Yes' if s.get('thumbnail', True) else 'No'}",
            callback_data="stg_thumbnail"
        )],
        [InlineKeyboardButton(
            f"✏️ Rename File : {'Yes' if s.get('rename_file', True) else 'No'}",
            callback_data="stg_rename_file"
        )],
        [InlineKeyboardButton("🔊 Upload as Audio",    callback_data="stg_upload_audio")],
        [InlineKeyboardButton("🎬 Upload as Video",    callback_data="stg_upload_video")],
        [InlineKeyboardButton("🎥 Stream Mapper",      callback_data="stg_stream_mapper")],
        [InlineKeyboardButton("⚙️ Video Metadata",     callback_data="stg_video_metadata")],
        [InlineKeyboardButton("⚙️ Mp3 Tag Setting",   callback_data="stg_mp3_tag")],
        [InlineKeyboardButton("⚙️ Audio Settings",    callback_data="stg_audio_settings")],
        [InlineKeyboardButton("⚙️ Reset Settings",    callback_data="stg_reset")],
        [InlineKeyboardButton("❌ Close Settings",     callback_data="stg_close")],
    ]
    return InlineKeyboardMarkup(rows)


def _usettings_keyboard(uid: int) -> InlineKeyboardMarkup:
    u = get_usettings(uid)
    rows = [
        [InlineKeyboardButton(
            f"📄 Caption Adder : {'On' if u.get('caption_adder') else 'Off'}",
            callback_data="ustg_caption_adder"
        )],
        [InlineKeyboardButton(
            f"📄 Words Remover : {'On' if u.get('words_remover') else 'Off'}",
            callback_data="ustg_words_remover"
        )],
        [InlineKeyboardButton(
            f"✏️ Rename Prefix : {'On' if u.get('rename_prefix') else 'Off'}",
            callback_data="ustg_rename_prefix"
        )],
        [InlineKeyboardButton(
            f"✏️ Rename Suffix : {'On' if u.get('rename_suffix') else 'Off'}",
            callback_data="ustg_rename_suffix"
        )],
        [InlineKeyboardButton(
            f"📄 Words Replacer : {'On' if u.get('words_replacer') else 'Off'}",
            callback_data="ustg_words_replacer"
        )],
        [InlineKeyboardButton(
            f"✏️ Caption Formatter : {'On' if u.get('caption_formatter') else 'Off'}",
            callback_data="ustg_caption_formatter"
        )],
        [InlineKeyboardButton(
            f"❌ Spoiler Covered Video",
            callback_data="ustg_spoiler_video"
        )],
        [InlineKeyboardButton(
            f"📁 File Split Size : {get_settings(uid).get('split_size','4GB')}",
            callback_data="ustg_split_size"
        )],
        [InlineKeyboardButton(
            f"🔗 Url Upload Mode : {get_settings(uid).get('url_mode','httpx')}",
            callback_data="ustg_url_mode"
        )],
        [InlineKeyboardButton(
            f"YTDL Filter : {get_settings(uid).get('ytdl_filter','mp4')}",
            callback_data="ustg_ytdl_filter"
        )],
        [InlineKeyboardButton("❌ Close", callback_data="ustg_close")],
    ]
    return InlineKeyboardMarkup(rows)


async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        "⚙️ <b>Config Bot Settings</b>",
        parse_mode="HTML",
        reply_markup=_settings_keyboard(uid)
    )


async def usettings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        "⚙️ <b>Config Bot Settings</b>",
        parse_mode="HTML",
        reply_markup=_usettings_keyboard(uid)
    )


async def settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = q.from_user.id
    await q.answer()
    data = q.data

    # ── /settings callbacks ─────────────────────────────────────────
    if data == "stg_bulk_mode":
        cur = get_settings(uid).get("bulk_mode", False)
        update_settings(uid, "bulk_mode", not cur)
        await q.edit_message_reply_markup(_settings_keyboard(uid))

    elif data == "stg_thumbnail":
        cur = get_settings(uid).get("thumbnail", True)
        update_settings(uid, "thumbnail", not cur)
        await q.edit_message_reply_markup(_settings_keyboard(uid))

    elif data == "stg_rename_file":
        cur = get_settings(uid).get("rename_file", True)
        update_settings(uid, "rename_file", not cur)
        await q.edit_message_reply_markup(_settings_keyboard(uid))

    elif data == "stg_upload_audio":
        update_settings(uid, "upload_type", "audio")
        await q.answer("Upload type set to Audio ✅", show_alert=True)

    elif data == "stg_upload_video":
        update_settings(uid, "upload_type", "video")
        await q.answer("Upload type set to Video ✅", show_alert=True)

    elif data == "stg_stream_mapper":
        await q.answer("Send stream mapping settings (e.g. 0:v 0:a 0:s)", show_alert=True)

    elif data == "stg_video_metadata":
        await q.answer("Video metadata editing coming soon!", show_alert=True)

    elif data == "stg_mp3_tag":
        await q.answer("Mp3 Tag editor – send your audio file!", show_alert=True)

    elif data == "stg_audio_settings":
        await q.answer("Audio settings – send an audio file to configure!", show_alert=True)

    elif data == "stg_reset":
        from database.db import update_user
        update_user(uid, {"settings": {
            "bulk_mode":   False,
            "thumbnail":   True,
            "rename_file": True,
            "upload_type": "document",
            "split_size":  "4GB",
            "url_mode":    "httpx",
            "ytdl_filter": "mp4",
        }})
        await q.edit_message_reply_markup(_settings_keyboard(uid))
        await q.answer("Settings reset ✅", show_alert=True)

    elif data == "stg_close":
        await q.message.delete()

    # ── /usettings callbacks ────────────────────────────────────────
    elif data == "ustg_caption_adder":
        cur = get_usettings(uid).get("caption_adder", False)
        update_usettings(uid, "caption_adder", not cur)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_words_remover":
        cur = get_usettings(uid).get("words_remover", False)
        update_usettings(uid, "words_remover", not cur)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_rename_prefix":
        context.user_data["waiting_for"] = "rename_prefix"
        await q.message.reply_text("Send the prefix text to add before filenames:")

    elif data == "ustg_rename_suffix":
        context.user_data["waiting_for"] = "rename_suffix"
        await q.message.reply_text("Send the suffix text to add after filenames:")

    elif data == "ustg_words_replacer":
        cur = get_usettings(uid).get("words_replacer", False)
        update_usettings(uid, "words_replacer", not cur)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_caption_formatter":
        cur = get_usettings(uid).get("caption_formatter", False)
        update_usettings(uid, "caption_formatter", not cur)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_spoiler_video":
        cur = get_usettings(uid).get("spoiler_video", False)
        update_usettings(uid, "spoiler_video", not cur)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_split_size":
        sizes = ["1GB", "2GB", "3GB", "4GB"]
        cur   = get_settings(uid).get("split_size", "4GB")
        nxt   = sizes[(sizes.index(cur) + 1) % len(sizes)] if cur in sizes else "4GB"
        update_settings(uid, "split_size", nxt)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_url_mode":
        modes = ["httpx", "wget", "requests"]
        cur   = get_settings(uid).get("url_mode", "httpx")
        nxt   = modes[(modes.index(cur) + 1) % len(modes)] if cur in modes else "httpx"
        update_settings(uid, "url_mode", nxt)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_ytdl_filter":
        fmts = ["mp4", "mkv", "webm", "mp3", "m4a"]
        cur  = get_settings(uid).get("ytdl_filter", "mp4")
        nxt  = fmts[(fmts.index(cur) + 1) % len(fmts)] if cur in fmts else "mp4"
        update_settings(uid, "ytdl_filter", nxt)
        await q.edit_message_reply_markup(_usettings_keyboard(uid))

    elif data == "ustg_close":
        await q.message.delete()


def get_settings_handlers():
    return [
        CommandHandler("settings",  settings_cmd),
        CommandHandler("usettings", usettings_cmd),
        CallbackQueryHandler(settings_callback, pattern="^(stg_|ustg_)"),
    ]
