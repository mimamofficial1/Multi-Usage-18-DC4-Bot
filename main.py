"""main.py – Entry point for Muzaffar Multi Usage Bot"""
import logging, os
from telegram.ext import ApplicationBuilder
from config import Config
from handlers.start_handler   import get_start_handlers
from handlers.admin_handler   import get_admin_handlers
from handlers.settings_handler import get_settings_handlers
from handlers.media_handler   import get_media_handlers
from handlers.url_handler     import get_url_handlers

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/tmp/bot.log"),
    ],
)
logger = logging.getLogger(__name__)

os.makedirs(Config.DOWNLOAD_DIR, exist_ok=True)


def main():
    if not Config.BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set in environment variables!")
    if not Config.MONGO_URI:
        raise ValueError("MONGO_URI is not set in environment variables!")

    app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

    # Register all handlers (order matters – more specific first)
    for h in get_start_handlers():
        app.add_handler(h)
    for h in get_admin_handlers():
        app.add_handler(h)
    for h in get_settings_handlers():
        app.add_handler(h)
    for h in get_url_handlers():
        app.add_handler(h)
    for h in get_media_handlers():
        app.add_handler(h)

    logger.info("🚀 Bot is starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
