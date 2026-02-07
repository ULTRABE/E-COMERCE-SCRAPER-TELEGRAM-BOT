import hashlib
from typing import Dict, List

import config
from database import Database


class DealProcessor:
    def __init__(self, db: Database):
        self.db = db

    def generate_deal_hash(self, deal: Dict) -> str:
        unique_string = f"{deal.get('site')}:{deal.get('url')}:{deal.get('deal_price')}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def filter_duplicates(self, deals: List[Dict]) -> List[Dict]:
        unique_deals = []

        for deal in deals:
            deal_hash = self.generate_deal_hash(deal)
            if self.db.is_duplicate_deal(deal_hash):
                continue

            unique_deals.append(deal)
            self.db.add_deal(deal_hash, deal.get("product_name", ""), deal.get("site", ""))

        return unique_deals

    def rank_deals(self, deals: List[Dict]) -> List[Dict]:
        def deal_score(deal: Dict) -> int:
            discount = int(deal.get("discount", 0) or 0)
            price = int(deal.get("deal_price", 0) or 0)
            return (discount * 10) + (10000 - min(price, 10000))

        return sorted(deals, key=deal_score, reverse=True)

    def process_deals(self, all_deals: List[Dict]) -> List[Dict]:
        valid = [d for d in all_deals if d.get("deal_price", 0) > 0 and d.get("url")]
        unique_deals = self.filter_duplicates(valid)
        ranked_deals = self.rank_deals(unique_deals)
        return ranked_deals[: config.MAX_DEALS_PER_RUN]
