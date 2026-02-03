from typing import Dict

class MessageFormatter:
    # Premium emoji placeholders - easy to customize
    EMOJI_DEAL = "🔥"  # Can be replaced with premium AnimatedAsianEmoji
    EMOJI_MONEY = "💰"  # Can be replaced with premium emoji
    EMOJI_SPARKLE = "✨"  # Can be replaced with premium emoji
    EMOJI_PARTY = "🎉"  # Can be replaced with premium emoji
    EMOJI_CART = "🛒"  # Can be replaced with premium emoji
    EMOJI_LINK = "🔗"  # Can be replaced with premium emoji
    EMOJI_ROCKET = "🚀"  # Can be replaced with premium emoji
    EMOJI_TAG = "🎯"  # Can be replaced with premium emoji
    EMOJI_FIRE = "🔥"  # Can be replaced with premium emoji
    EMOJI_DISCOUNT = "💸"  # Can be replaced with premium emoji
    EMOJI_STORE = "🛒"  # Can be replaced with premium emoji
    
    @staticmethod
    def format_deal(deal: Dict) -> str:
        product_name = deal.get('product_name', 'Unknown Product')
        deal_price = deal.get('deal_price', 0)
        original_price = deal.get('original_price', 0)
        discount = deal.get('discount', 0)
        url = deal.get('url', '')
        site = deal.get('site', 'Unknown')
        
        # Enhanced deal message with premium emoji support
        message = f"""{MessageFormatter.EMOJI_DEAL} HOT DEAL {MessageFormatter.EMOJI_DEAL}
━━━━━━━━━━━━━━━━━━
📦 {product_name}
💰 Deal: ₹{deal_price:,}
💵 MRP: ₹{original_price:,}
📉 Save: ₹{original_price - deal_price:,} ({discount}% OFF)
{MessageFormatter.EMOJI_LINK} {url}
━━━━━━━━━━━━━━━━━━
{MessageFormatter.EMOJI_CART} Buy Now! {MessageFormatter.EMOJI_ROCKET}
"""
        
        return message
    
    @staticmethod
    def format_deals_batch(deals: list) -> list:
        messages = []
        for deal in deals:
            messages.append(MessageFormatter.format_deal(deal))
        return messages
    
    @staticmethod
    def format_welcome_message(username: str, group_name: str) -> str:
        """Format welcome message with premium emoji support"""
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
