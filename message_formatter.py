from typing import Dict

class MessageFormatter:
    @staticmethod
    def format_deal(deal: Dict) -> str:
        product_name = deal.get('product_name', 'Unknown Product')
        deal_price = deal.get('deal_price', 0)
        original_price = deal.get('original_price', 0)
        discount = deal.get('discount', 0)
        url = deal.get('url', '')
        site = deal.get('site', 'Unknown')
        
        message = f"""```
🎯 {product_name}

💰 Deal Price: ₹{deal_price:,}
💸 Real Price: ₹{original_price:,}
🔥 Discount: {discount}% OFF

🛒 Site: {site}
```
🔗 [Buy Now]({url})"""
        
        return message
    
    @staticmethod
    def format_deals_batch(deals: list) -> list:
        messages = []
        for deal in deals:
            messages.append(MessageFormatter.format_deal(deal))
        return messages
