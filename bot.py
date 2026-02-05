import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import config
from auth_manager import AuthManager
from database import Database
from keyword_manager import KeywordManager
from scheduler import DealScheduler
from welcome_manager import WelcomeManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger("deal-bot")

db = Database()
auth_manager = AuthManager(db)
keyword_manager = KeywordManager(db)
welcome_manager = WelcomeManager(db)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    is_owner = auth_manager.is_owner(user_id)

    welcome_message = """
🛍️ **Welcome to Indian E-commerce Deal Bot!**

I automatically scrape deals from 12+ major Indian e-commerce sites and send them to authorized groups/channels.

**Commands:**
/start - Show this message
/help - Get help
/auth - (Owner only) Authorize bot in this group
/addchannel <chat_id> - (Owner only) Authorize channel by ID
/only <keywords> - (Owner only) Filter deals by keywords
/only clear - (Owner only) Clear keyword filters
/stats - (Owner only) Show bot statistics
/welcome <message> - (Owner only) Set custom welcome message
/welcome default - Reset to default welcome

**How it works:**
1. Bot must be authorized by owner using /auth
2. Deals are automatically scraped every 3 minutes
3. Only fresh, high-discount deals are sent
4. Use /only to filter deals by your interests
5. New members get welcome messages automatically

**Sites covered:**
Amazon, Flipkart, Myntra, AJIO, Snapdeal, ShopClues, Croma, Vijay Sales, Meesho, Tata CLIQ, Nykaa, Lenskart
"""

    if not is_owner and config.CHANNEL_URL:
        keyboard = [[InlineKeyboardButton("🚀 JOIN CHANNEL", url=config.CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id
    is_owner = auth_manager.is_owner(user_id)

    help_message = """
📚 **Help & Commands**

**Authorization:**
- Bot works only in authorized groups/channels
- Only the bot owner can authorize using /auth or /addchannel
- Once authorized, deals will be sent automatically

**Filtering Deals:**
- Use `/only shoes iPhone laptop` to only receive deals matching these keywords
- Use `/only clear` to remove filters and get all deals
- Keywords are case-insensitive
- (Owner only)

**Welcome Messages:**
- New members automatically receive welcome messages
- Owner can customize welcome message with `/welcome <message>`
- Use `{username}` and `{group_name}` as placeholders
- Reset with `/welcome default`

**Examples:**
- `/only smartphone` - Only phone deals
- `/only shoes sneakers` - Footwear deals
- `/only laptop electronics` - Tech deals
- `/welcome Hello {username}! Welcome to {group_name}!` - Custom welcome

**Automatic Scraping:**
- Runs every 3 minutes
- Covers 12+ major e-commerce sites
- Only sends new deals (no duplicates)
- Minimum 30% discount filter

Need help? Contact the bot owner.
"""

    if not is_owner and config.CHANNEL_URL:
        keyboard = [[InlineKeyboardButton("🚀 JOIN CHANNEL", url=config.CHANNEL_URL)]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(help_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_message)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    user_id = update.message.from_user.id

    if not auth_manager.is_owner(user_id):
        if config.CHANNEL_URL:
            keyboard = [[InlineKeyboardButton("🚀 JOIN CHANNEL", url=config.CHANNEL_URL)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "❌ Only the bot owner can view statistics.",
                reply_markup=reply_markup,
            )
        else:
            await update.message.reply_text("❌ Only the bot owner can view statistics.")
        return

    total_deals = db.get_stat("deals_sent")
    authorized_chats = len(db.get_authorized_chats())

    stats_message = f"""
📊 **Bot Statistics**

🎯 Total deals sent: {total_deals:,}
👥 Authorized chats: {authorized_chats}
⏰ Scrape interval: {config.SCRAPE_INTERVAL} minutes
🛒 Sites monitored: 12

Bot is running and active! 🚀
"""
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
        await update.message.reply_text("❌ Only the bot owner can manage keyword filters.")
        return

    if not await auth_manager.check_authorization(update, context):
        return

    await keyword_manager.handle_only_command(update, context)


async def welcome_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await welcome_manager.handle_welcome_command(update, context, auth_manager)


async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return

    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "🔒 This bot is not authorized in this group. "
                "Ask the bot owner to send /auth here to enable deal notifications."
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
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))

    logger.info("Bot started successfully!")
    logger.info("Scraping interval: %s minutes", config.SCRAPE_INTERVAL)
    logger.info("Owner ID: %s", config.OWNER_ID)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
