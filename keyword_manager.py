from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from typing import List

class KeywordManager:
    def __init__(self, db: Database):
        self.db = db
    
    async def handle_only_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return
        
        chat_id = update.message.chat_id
        
        if not context.args:
            keywords = self.db.get_keywords(chat_id)
            if keywords:
                await update.message.reply_text(
                    f"📌 Current filters: {', '.join(keywords)}\n\n"
                    "Use /only clear to remove filters."
                )
            else:
                await update.message.reply_text(
                    "ℹ️ No keyword filters set.\n\n"
                    "Usage: /only <keywords>\n"
                    "Example: /only shoes iPhone laptop"
                )
            return
        
        if context.args[0].lower() == "clear":
            self.db.clear_keywords(chat_id)
            await update.message.reply_text("✅ Keyword filters cleared! You'll receive all deals now.")
            return
        
        keywords = [arg.lower() for arg in context.args]
        self.db.set_keywords(chat_id, keywords)
        await update.message.reply_text(
            f"✅ Filters set! You'll only receive deals matching: {', '.join(keywords)}"
        )
    
    def matches_keywords(self, chat_id: int, product_name: str) -> bool:
        keywords = self.db.get_keywords(chat_id)
        if not keywords:
            return True
        
        product_lower = product_name.lower()
        return any(keyword in product_lower for keyword in keywords)
