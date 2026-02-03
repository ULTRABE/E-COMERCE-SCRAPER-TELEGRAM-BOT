from telegram import Update
from telegram.ext import ContextTypes
from database import Database
import config

class AuthManager:
    def __init__(self, db: Database):
        self.db = db
    
    def is_owner(self, user_id: int) -> bool:
        return user_id == config.OWNER_ID
    
    async def handle_auth(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return
        
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        chat_title = update.message.chat.title or update.message.chat.first_name or "Private Chat"
        
        if not self.is_owner(user_id):
            await update.message.reply_text(
                "❌ Only the bot owner can authorize this bot in groups/channels."
            )
            return
        
        self.db.authorize_chat(chat_id, chat_title, user_id)
        await update.message.reply_text(
            "✅ Bot authorized! I'll start sending deals now.\n\n"
            "Use /only <keywords> to filter deals by keywords.\n"
            "Use /only clear to remove filters."
        )
    
    async def handle_addchannel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return
        
        user_id = update.message.from_user.id
        
        if not self.is_owner(user_id):
            await update.message.reply_text(
                "❌ Only the bot owner can authorize channels."
            )
            return
        
        if not context.args or len(context.args) < 1:
            await update.message.reply_text(
                "❌ Please provide a chat ID.\n\n"
                "Usage: /addchannel <chat_id>\n"
                "Example: /addchannel -1001234567890"
            )
            return
        
        try:
            target_chat_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid chat ID. It should be a number.")
            return
        
        try:
            chat = await context.bot.get_chat(target_chat_id)
            chat_title = chat.title or chat.first_name or "Unknown Chat"
            
            self.db.authorize_chat(target_chat_id, chat_title, user_id)
            await update.message.reply_text(
                f"✅ Channel/Group authorized!\n\n"
                f"Chat: {chat_title}\n"
                f"ID: {target_chat_id}\n\n"
                "Deals will be sent automatically."
            )
        except Exception as e:
            await update.message.reply_text(
                f"❌ Failed to authorize channel.\n\n"
                f"Error: {str(e)}\n\n"
                "Make sure the bot is added to the channel/group and has posting permissions."
            )
    
    async def check_authorization(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not update.message:
            return False
        
        chat_id = update.message.chat_id
        
        if self.db.is_chat_authorized(chat_id):
            return True
        
        await update.message.reply_text(
            "🔒 This bot is not authorized in this group. Ask the bot owner to send /auth here."
        )
        return False
