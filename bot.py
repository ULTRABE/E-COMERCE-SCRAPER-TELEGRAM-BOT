import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import config
from database import Database
from auth_manager import AuthManager
from keyword_manager import KeywordManager
from scheduler import DealScheduler

db = Database()
auth_manager = AuthManager(db)
keyword_manager = KeywordManager(db)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    welcome_message = """
🛍️ **Welcome to Indian E-commerce Deal Bot!**

I automatically scrape deals from 8+ major Indian e-commerce sites and send them to authorized groups/channels.

**Commands:**
/start - Show this message
/help - Get help
/auth - (Owner only) Authorize bot in this group
/only <keywords> - Filter deals by keywords
/only clear - Clear keyword filters
/stats - Show bot statistics

**How it works:**
1. Bot must be authorized by owner using /auth
2. Deals are automatically scraped every 20 minutes
3. Only fresh, high-discount deals are sent
4. Use /only to filter deals by your interests

**Sites covered:**
Amazon, Flipkart, Myntra, AJIO, Snapdeal, ShopClues, Croma, Vijay Sales
"""
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    help_message = """
📚 **Help & Commands**

**Authorization:**
- Bot works only in authorized groups/channels
- Only the bot owner can authorize using /auth
- Once authorized, deals will be sent automatically

**Filtering Deals:**
- Use `/only shoes iPhone laptop` to only receive deals matching these keywords
- Use `/only clear` to remove filters and get all deals
- Keywords are case-insensitive

**Examples:**
- `/only smartphone` - Only phone deals
- `/only shoes sneakers` - Footwear deals
- `/only laptop electronics` - Tech deals

**Automatic Scraping:**
- Runs every 20 minutes
- Covers 8+ major e-commerce sites
- Only sends new deals (no duplicates)
- Minimum 30% discount filter

Need help? Contact the bot owner.
"""
    await update.message.reply_text(help_message)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    if not await auth_manager.check_authorization(update, context):
        return
    
    total_deals = db.get_stat('deals_sent')
    authorized_chats = len(db.get_authorized_chats())
    
    stats_message = f"""
📊 **Bot Statistics**

🎯 Total deals sent: {total_deals:,}
👥 Authorized chats: {authorized_chats}
⏰ Scrape interval: {config.SCRAPE_INTERVAL} minutes
🛒 Sites monitored: 8

Bot is running and active! 🚀
"""
    await update.message.reply_text(stats_message)

async def auth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await auth_manager.handle_auth(update, context)

async def only_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    if not await auth_manager.check_authorization(update, context):
        return
    
    await keyword_manager.handle_only_command(update, context)

async def handle_new_chat_members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.new_chat_members:
        return
    
    for member in update.message.new_chat_members:
        if member.id == context.bot.id:
            await update.message.reply_text(
                "🔒 This bot is not authorized in this group. "
                "Ask the bot owner to send /auth here to enable deal notifications."
            )

async def post_init(application: Application):
    scheduler = DealScheduler(application.bot, db)
    scheduler.start()
    application.bot_data['scheduler'] = scheduler

def main():
    print("Starting Indian E-commerce Deal Bot...")
    
    if not config.BOT_TOKEN:
        print("Error: BOT_TOKEN not found in environment variables")
        return
    
    if not config.OWNER_ID:
        print("Error: OWNER_ID not found in environment variables")
        return
    
    application = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("auth", auth_command))
    application.add_handler(CommandHandler("only", only_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_chat_members))
    
    print("Bot started successfully!")
    print(f"Scraping interval: {config.SCRAPE_INTERVAL} minutes")
    print(f"Owner ID: {config.OWNER_ID}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
