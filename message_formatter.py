from typing import Dict


class MessageFormatter:
    # Premium emoji placeholders - you can replace these with premium custom emoji.
    EMOJI_DEAL = "🔥"
    EMOJI_MONEY = "💰"
    EMOJI_LINK = "🔗"
    EMOJI_DISCOUNT = "💸"
    EMOJI_STORE = "🏬"
    EMOJI_NEW = "✨"

    @staticmethod
    def format_deal(deal: Dict) -> str:
        product_name = deal.get("product_name", "Unknown Product")[:80]
        deal_price = int(deal.get("deal_price", 0) or 0)
        original_price = int(deal.get("original_price", 0) or 0)
        discount = int(deal.get("discount", 0) or 0)
        url = deal.get("url", "")
        site = deal.get("site", "Unknown")

        savings = max(original_price - deal_price, 0)

        return (
            f"{MessageFormatter.EMOJI_DEAL} `\"LIVE DEAL\"` {MessageFormatter.EMOJI_NEW}\n"
            f"`\"Product\"` → `{product_name}`\n"
            f"`\"Now\"` {MessageFormatter.EMOJI_MONEY} `₹{deal_price:,}`\n"
            f"`\"Was\"` ~₹{original_price:,}~ | `\"Off\"` {MessageFormatter.EMOJI_DISCOUNT} `{discount}%`\n"
            f"`\"Save\"` `₹{savings:,}`\n"
            f"`\"Store\"` {MessageFormatter.EMOJI_STORE} `{site}`\n"
            f"`\"Link\"` {MessageFormatter.EMOJI_LINK} {url}"
        )

    @staticmethod
    def format_welcome_message(username: str, group_name: str) -> str:
        return (
            "✨ `\"PREMIUM DEAL BOT\"` ✨\n"
            f"`\"Hello\"` @{username}\n"
            f"`\"Group\"` `{group_name}`\n\n"
            "`\"Stores\"` → `Amazon` | `Flipkart` | `JioMart`\n"
            "`\"Commands\"` → `/start` `/help` `/only` `/stats`\n"
            "`\"Status\"` → `Live price-drop alerts enabled`"
        )
