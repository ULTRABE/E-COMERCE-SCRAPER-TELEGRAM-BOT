import asyncio
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import config
from auth_manager import AuthManager
from database import Database
from keyword_manager import KeywordManager
from scheduler import DealScheduler
from welcome_manager import WelcomeManager


db = Database()
auth_manager = AuthManager(db)
keyword_manager = KeywordManager(db)
welcome_manager = WelcomeManager(db)


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def _channel_markup():
    if not config.CHANNEL_URL:
        return None
    return InlineKeyboardMarkup([[InlineKeyboardButton(config.CHANNEL_BUTTON_TEXT, url=config.CHANNEL_URL)]])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    welcome_message = (
        "✨ `\"INDIA DEALS PRO\"` ✨\n\n"
        "`\"Stores\"` → `Amazon` | `Flipkart` | `JioMart`\n"
        "`\"Mode\"` → `Live price-drop tracking`\n"
        "`\"Commands\"` → `/help` `/only` `/stats` `/welcome`\n"
        "`\"Tip\"` → `Use /only to track your niche products`"
    )
    await update.message.reply_text(welcome_message, reply_markup=_channel_markup(), disable_web_page_preview=True)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    help_message = (
        "📚 `\"COMMANDS\"`\n"
        "`\"/start\"` → `Bot intro`\n"
        "`\"/help\"` → `Commands list`\n"
        "`\"/auth\"` → `Owner authorize chat`\n"
        "`\"/addchannel <id>\"` → `Owner authorize channel`\n"
        "`\"/only <keywords>\"` → `Keyword filter`\n"
        "`\"/only clear\"` → `Clear filter`\n"
        "`\"/stats\"` → `Owner stats`\n"
        "`\"/welcome <message>\"` → `Owner welcome template`"
    )
    await update.message.reply_text(help_message, reply_markup=_channel_markup(), disable_web_page_preview=True)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    if not auth_manager.is_owner(user_id):
        await update.message.reply_text("❌ `\"Owner only command\"`", reply_markup=_channel_markup())
        return

    total_deals = db.get_stat("deals_sent")
    authorized_chats = len(db.get_authorized_chats())

    stats_message = (
        "📊 `\"BOT STATS\"`\n"
        f"`\"Deals sent\"` → `{total_deals:,}`\n"
        f"`\"Authorized chats\"` → `{authorized_chats}`\n"
        f"`\"Interval(sec)\"` → `{config.SCRAPE_INTERVAL_SECONDS}`\n"
        f"`\"Min discount\"` → `{config.MIN_DISCOUNT}%`"
    )
    await update.message.reply_text(stats_message)


async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await auth_manager.handle_auth(update, context)


async def addchannel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await auth_manager.handle_addchannel(update, context)


async def only_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    if not auth_manager.is_owner(user_id):
        await update.message.reply_text("❌ `\"Owner only command\"`")
        return

    if not await auth_manager.check_authorization(update, context):
        return

    await keyword_manager.handle_only_command(update, context)


async def welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await welcome_manager.handle_welcome_command(update, context, auth_manager)



async def scrapenow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    if not auth_manager.is_owner(update.message.from_user.id):
        await update.message.reply_text("❌ `\"Owner only command\"`")
        return

    scheduler = context.application.bot_data.get("scheduler")
    if not scheduler:
        await update.message.reply_text("⚠️ `\"Scheduler not ready\"`")
        return

    await update.message.reply_text("⏱️ `\"Manual live scrape started\"`")
    await scheduler.scrape_and_send_deals()


async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "🔒 `\"Bot not authorized in this chat\"`\n`\"Ask owner to run /auth\"`"
            )
        else:
            await welcome_manager.handle_new_member(update, context, auth_manager)


async def post_init(application: Application):
    scheduler = DealScheduler(application.bot, db)
    scheduler.start()
    application.bot_data["scheduler"] = scheduler


def main():
    logger.info("Starting Indian E-commerce Deal Bot...")

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return

    if not config.OWNER_ID:
        logger.error("OWNER_ID not found in environment variables")
        return

    application = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("addchannel", addchannel_command))
    application.add_handler(CommandHandler("only", only_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("welcome", welcome_command))
    application.add_handler(CommandHandler("scrapenow", scrapenow_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))

    logger.info("Bot started successfully!")
    logger.info("Scraping interval: %s seconds", config.SCRAPE_INTERVAL_SECONDS)
    logger.info("Owner ID: %s", config.OWNER_ID)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
