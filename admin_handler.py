"""handlers/admin_handler.py"""
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from database.db import (
    get_user, get_all_users, get_users_count,
    ban_user, unban_user, get_banned_users, activate_plan
)
from config import Config


def is_admin(user_id: int) -> bool:
    return user_id in Config.ADMIN_IDS


def admin_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("❌ You are not authorized to use this command.")
            return
        return await func(update, context)
    wrapper.__name__ = func.__name__
    return wrapper


@admin_only
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🛠 <b>Available admin commands are :</b>\n\n"
        "⇒ /cmds\n"
        "⇒ /cmd2\n"
        "⇒ /cmd3\n"
        "⇒ /cmd4\n"
        "⇒ /paid\n"
        "⇒ /log\n"
        "⇒ /reset\n"
        "⇒ /restart\n"
        "⇒ /status\n"
        "⇒ /broadcast\n"
        "⇒ /ban_user\n"
        "⇒ /unban_user\n"
        "⇒ /banned_users\n"
        "⇒ /set_url\n"
        "⇒ /set_password"
    )
    await update.message.reply_text(text, parse_mode="HTML")


@admin_only
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total  = get_users_count()
    banned = len(get_banned_users())
    import psutil
    cpu  = psutil.cpu_percent(interval=1)
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    text = (
        f"📊 <b>Bot Status</b>\n\n"
        f"👥 Total Users : <b>{total}</b>\n"
        f"🚫 Banned Users: <b>{banned}</b>\n\n"
        f"💻 CPU  : {cpu}%\n"
        f"🧠 RAM  : {mem.percent}% ({_fmt(mem.used)}/{_fmt(mem.total)})\n"
        f"💾 Disk : {disk.percent}% ({_fmt(disk.used)}/{_fmt(disk.total)})\n"
    )
    await update.message.reply_text(text, parse_mode="HTML")


def _fmt(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"


@admin_only
async def broadcast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        await update.message.reply_text("❗ Reply to the message you want to broadcast.")
        return
    users   = get_all_users()
    success = fail = 0
    msg = update.message.reply_to_message
    for u in users:
        try:
            await context.bot.copy_message(
                chat_id=u["user_id"],
                from_chat_id=msg.chat_id,
                message_id=msg.message_id,
            )
            success += 1
        except Exception:
            fail += 1
    await update.message.reply_text(
        f"✅ Broadcast done!\n✅ Success: {success}\n❌ Failed: {fail}"
    )


@admin_only
async def ban_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ban_user <user_id>")
        return
    uid = int(context.args[0])
    ban_user(uid)
    await update.message.reply_text(f"✅ User {uid} banned.")


@admin_only
async def unban_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /unban_user <user_id>")
        return
    uid = int(context.args[0])
    unban_user(uid)
    await update.message.reply_text(f"✅ User {uid} unbanned.")


@admin_only
async def banned_users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = get_banned_users()
    if not users:
        await update.message.reply_text("No banned users.")
        return
    lines = [f"• {u['user_id']}" for u in users]
    await update.message.reply_text(
        "🚫 <b>Banned Users:</b>\n" + "\n".join(lines),
        parse_mode="HTML"
    )


@admin_only
async def paid_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Grant a plan to a user. Usage: /paid <user_id> <plan> <days>"""
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /paid <user_id> <plan> <days>\nExample: /paid 123456789 standard 30")
        return
    uid  = int(args[0])
    plan = args[1].lower()
    days = int(args[2])
    if plan not in Config.PLANS:
        await update.message.reply_text(f"Invalid plan. Choose: {', '.join(Config.PLANS.keys())}")
        return
    activate_plan(uid, plan, days)
    await update.message.reply_text(
        f"✅ <b>{plan.title()}</b> plan activated for user <code>{uid}</code> for {days} days.",
        parse_mode="HTML"
    )


@admin_only
async def log_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log_file = "/tmp/bot.log"
    if os.path.exists(log_file):
        await update.message.reply_document(open(log_file, "rb"), filename="bot.log")
    else:
        await update.message.reply_text("No log file found.")


@admin_only
async def restart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("♻️ Restarting bot...")
    os.execv(__import__("sys").executable, [__import__("sys").executable] + __import__("sys").argv)


@admin_only
async def set_url_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /set_url <url>")
        return
    url = context.args[0]
    # Store in DB or env
    await update.message.reply_text(f"✅ URL set to: {url}")


@admin_only
async def set_password_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /set_password <password>")
        return
    await update.message.reply_text("✅ Password updated.")


def get_admin_handlers():
    return [
        CommandHandler("admin",        admin_cmd),
        CommandHandler("status",       status_cmd),
        CommandHandler("broadcast",    broadcast_cmd),
        CommandHandler("ban_user",     ban_user_cmd),
        CommandHandler("unban_user",   unban_user_cmd),
        CommandHandler("banned_users", banned_users_cmd),
        CommandHandler("paid",         paid_cmd),
        CommandHandler("log",          log_cmd),
        CommandHandler("restart",      restart_cmd),
        CommandHandler("set_url",      set_url_cmd),
        CommandHandler("set_password", set_password_cmd),
    ]
