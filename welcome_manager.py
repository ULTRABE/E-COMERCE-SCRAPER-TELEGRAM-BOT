from telegram import Update
from telegram.ext import ContextTypes
from database import Database
import config

class WelcomeManager:
    def __init__(self, db: Database):
        self.db = db
        
    def get_default_welcome_message(self, username: str, group_name: str) -> str:
        """Default welcome message with standard emojis"""
        return f"""🎉 WELCOME! 🎉
━━━━━━━━━━━━━━━━━━
Hello @{username}! 👋
Welcome to {group_name}! 🎊

🔥 Get best deals from:
• Flipkart
• Amazon
• Meesho
• Myntra
• AJIO
• Snapdeal
• ShopClues
• Croma
• Tata CLIQ
• Nykaa
• Lenskart
• Vijay Sales

Enjoy saving money! 💰✨
━━━━━━━━━━━━━━━━━━
"""
    
    def get_welcome_message(self, chat_id: int, username: str, group_name: str) -> str:
        """Get welcome message for a chat, fallback to default"""
        custom_message = self.db.get_welcome_message(chat_id)
        if custom_message:
            return custom_message.replace('{username}', f'@{username}').replace('{group_name}', group_name)
        return self.get_default_welcome_message(username, group_name)
    
    async def handle_welcome_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, auth_manager):
        if not update.message:
            return
        
        if not await auth_manager.check_authorization(update, context):
            return
        
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        
        if not auth_manager.is_owner(user_id):
            await update.message.reply_text("❌ Only the bot owner can configure welcome messages.")
            return
        
        if not context.args:
            current_message = self.db.get_welcome_message(chat_id)
            if current_message:
                await update.message.reply_text(
                    f"📌 Current welcome message:\n\n{current_message}"
                )
            else:
                await update.message.reply_text(
                    "ℹ️ No custom welcome message set. Using default.\n\n"
                    "Usage: /welcome <message> - Set custom welcome message\n"
                    "Use {username} and {group_name} as placeholders\n"
                    "Example: /welcome default - Reset to default"
                )
            return
        
        if context.args[0].lower() == "default":
            self.db.clear_welcome_message(chat_id)
            await update.message.reply_text("✅ Welcome message reset to default!")
            return
        
        custom_message = ' '.join(context.args)
        self.db.set_welcome_message(chat_id, custom_message)
        await update.message.reply_text("✅ Custom welcome message set!")
    
    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE, auth_manager):
        if not update.message or not update.message.new_chat_members:
            return
        
        chat_id = update.message.chat_id
        
        if not self.db.is_chat_authorized(chat_id):
            return
        
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                continue
            
            username = member.username or member.first_name or "new_member"
            group_name = update.message.chat.title or "this group"
            
            welcome_message = self.get_welcome_message(chat_id, username, group_name)
            
            await update.message.reply_text(welcome_message)