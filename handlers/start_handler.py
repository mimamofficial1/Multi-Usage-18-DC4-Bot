"""handlers/start_handler.py"""
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.db import get_user, is_plan_active, activate_plan, get_thumb, save_thumb, delete_thumb
from config import Config


START_TEXT = """
<b>These are some Basic commands</b>

/buttons_adder – Add button to Telegram message.
/forward – Forward message to Channel/Group
/web – Enjoy YouTube, Instagram, Spotify & more without leaving Telegram
/slogin – Login with session string
/slogout – Logout Session string
/dublicates – Remove duplicate lines from txt file
/html – HTML to txt converter
/merge – Merge videos from URLs
/yt – YT channel/playlist link
/mongo_clone – MongoDB Cloner
/timezone – Set timezone
"""

DISCLAIMER_TEXT = """
<b>Legal Disclaimer</b>

This legal disclaimer ("Disclaimer") applies to the use of our Bot, its services, and interactions with the bot. By using Bot, you agree to the terms and conditions outlined in this Disclaimer.

<b>1. Purpose of Bot:</b>
This Telegram bot is designed to facilitate the download of publicly available files from the internet, Some video and Audio related tools. We do not host or store any files, nor do we endorse or support any illegal activities.

<b>2. User Responsibilities:</b>
You, the user, are solely responsible for ensuring the legality of the files you request and download through Bot. It is your responsibility to comply with all applicable laws and regulations.

<b>3. No Data Collection:</b>
Bot does not collect, store, or have access to any incoming or outgoing user data. Your privacy is important to us, and we respect it.

<b>4. Prohibited Activities:</b>
Bot strictly prohibits the use of the bot for illegal activities, including but not limited to downloading, distributing, or sharing illegal materials, copyrighted content without proper authorization, or any other activities that violate the law.

<b>5. Security and Disclaimer of Liability:</b>
While we take reasonable steps to ensure the safety and functionality of Bot, we do not guarantee the security or safety of downloaded files. You use the bot at your own risk.

Bot and its developers are not liable for any damages or legal consequences resulting from your use of the bot.

<b>6. Changes to Disclaimer:</b>
This Disclaimer may be updated or modified at any time without prior notice. It is your responsibility to review this Disclaimer regularly for any changes.

<b>7. Contact Information:</b>
If you have any questions or concerns about Bot or this Disclaimer, please contact us at @Chitranjan6gBot
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_user = get_user(user.id)
    if db_user.get("banned"):
        await update.message.reply_text("❌ You are banned from using this bot.")
        return

    kb = [
        [InlineKeyboardButton("🏠 Home", callback_data="home"),
         InlineKeyboardButton("⚡ Functions", callback_data="functions")],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ]
    await update.message.reply_text(
        START_TEXT, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def disclaimer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("🏠 Home", callback_data="home"),
           InlineKeyboardButton("⚡ Functions", callback_data="functions")],
          [InlineKeyboardButton("❌ Close", callback_data="close")]]
    await update.message.reply_text(
        DISCLAIMER_TEXT, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    text = (
        f"<b><u>User Details :</u></b>\n\n"
        f"🌿 <b>First Name :</b> {u.first_name}\n"
        f"👤 <b>User Id :</b> <code>{u.id}</code>\n"
        f"😊 <b>Username :</b> @{u.username or 'N/A'}\n"
        f"🔗 <b>User Link :</b> <a href='tg://user?id={u.id}'>{u.first_name}</a>\n"
        f"⭐ <b>Telegram Premium :</b> {u.is_premium}\n"
        f"📋 <b>Language Code :</b> {u.language_code or 'en'}\n\n"
        f"If you need user id, Then just tap and copy."
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def upgrade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u    = update.effective_user
    user = get_user(u.id)
    plan = user.get("plan", "free")
    active = is_plan_active(user)
    expires = user.get("expires")
    activated = user.get("activated")

    if active and plan != "free":
        remaining = (expires - datetime.utcnow()) if expires else None
        rem_str = ""
        if remaining:
            total_secs = int(remaining.total_seconds())
            days = total_secs // 86400
            hours = (total_secs % 86400) // 3600
            mins  = (total_secs % 3600) // 60
            secs  = total_secs % 60
            rem_str = f"{days} days, {hours:02}:{mins:02}:{secs:02}"

        text = (
            f"Hello {u.first_name} 👋\n"
            f"✨ <b>Your Subscription is Active!</b>\n\n"
            f"🆔 <b>User ID:</b> {u.id}\n"
            f"💎 <b>Current Plan:</b> {plan.title()}\n"
            f"📅 <b>Plan Validity:</b> 30 Days\n\n"
            f"⏳ <b>Remaining:</b> {rem_str}\n"
            f"📅 <b>Plan Expires On:</b> {expires.strftime('%Y-%m-%d') if expires else 'N/A'}\n"
            f"🟢 <b>Activated On:</b> {activated.strftime('%Y-%m-%d %H:%M:%S') if activated else 'N/A'}\n\n"
            f"ℹ️ Want to upgrade or check pricing?\n"
            f"Use /plan anytime to explore available plans.\n\n"
            f"Need help? Contact @Chitranjan6G."
        )
    else:
        text = (
            f"Hello {u.first_name} 👋\n\n"
            f"🆔 <b>User ID:</b> {u.id}\n"
            f"📦 <b>Current Plan:</b> Free\n\n"
            f"💎 <b>Available Plans:</b>\n"
            f"• Standard – ₹99/month\n"
            f"• Premium  – ₹199/month\n\n"
            f"Use /plan to check plans & pricing.\n"
            f"Need help? Contact @Chitranjan6G."
        )
    kb = [[InlineKeyboardButton("❌ Close", callback_data="close")]]
    await update.message.reply_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def plan_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "💎 <b>Available Plans</b>\n\n"
        "🆓 <b>Free Plan</b>\n"
        "  • 2 GB file size limit\n"
        "  • Basic features\n\n"
        "⭐ <b>Standard – ₹99/month</b>\n"
        "  • 4 GB file size limit\n"
        "  • All features\n"
        "  • Priority support\n\n"
        "💎 <b>Premium – ₹199/month</b>\n"
        "  • 4 GB file size limit\n"
        "  • All features\n"
        "  • Bulk mode\n"
        "  • Premium support\n\n"
        "Contact @Chitranjan6G to upgrade."
    )
    await update.message.reply_text(text, parse_mode="HTML")


async def show_thumb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    thumb = get_thumb(update.effective_user.id)
    if thumb:
        await update.message.reply_photo(thumb, caption="✅ This is your saved thumbnail.")
    else:
        await update.message.reply_text("❌ No thumbnail saved. Send a photo to save it.")


async def del_thumb_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    delete_thumb(update.effective_user.id)
    await update.message.reply_text("🗑 Thumbnail deleted successfully.")


async def json_formatter_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📄 JSON Formatter", url="https://jsonformatter.curiousconcept.com/")],
        [InlineKeyboardButton("❌ Close", callback_data="close")],
    ]
    await update.message.reply_text(
        "For Formatting a JSON file/txt, Click below Button 👇",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    from database.db import clear_task
    clear_task(uid)
    context.user_data.clear()
    await update.message.reply_text("✅ Task cancelled successfully.")


# ─── callback query router ─────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    if data == "home":
        kb = [[InlineKeyboardButton("🏠 Home", callback_data="home"),
               InlineKeyboardButton("⚡ Functions", callback_data="functions")],
              [InlineKeyboardButton("❌ Close", callback_data="close")]]
        await q.edit_message_text(START_TEXT, parse_mode="HTML",
                                  reply_markup=InlineKeyboardMarkup(kb))

    elif data == "functions":
        text = (
            "⚡ <b>Functions</b>\n\n"
            "Send any <b>Video, Audio, Document or URL</b> to see available options!\n\n"
            "🎬 Video: 19 tools\n"
            "🎵 Audio: 17 tools\n"
            "📄 Document: 7 tools\n"
            "🔗 URL: 6 tools"
        )
        kb = [[InlineKeyboardButton("🔙 Back", callback_data="home"),
               InlineKeyboardButton("❌ Close", callback_data="close")]]
        await q.edit_message_text(text, parse_mode="HTML",
                                  reply_markup=InlineKeyboardMarkup(kb))

    elif data == "close":
        await q.message.delete()


def get_start_handlers():
    return [
        CommandHandler("start",          start),
        CommandHandler("disclaimer",     disclaimer),
        CommandHandler("info",           info_cmd),
        CommandHandler("upgrade",        upgrade_cmd),
        CommandHandler("plan",           plan_cmd),
        CommandHandler("show_thumb",     show_thumb_cmd),
        CommandHandler("del_thumb",      del_thumb_cmd),
        CommandHandler("json_formatter", json_formatter_cmd),
        CommandHandler("cancel",         cancel_cmd),
        CallbackQueryHandler(button_handler),
    ]
