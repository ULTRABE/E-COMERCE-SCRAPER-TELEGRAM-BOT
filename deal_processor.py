from typing import List, Dict
import hashlib
from database import Database

class DealProcessor:
    def __init__(self, db: Database):
        self.db = db
    
    def generate_deal_hash(self, deal: Dict) -> str:
        unique_string = f"{deal['site']}:{deal['product_name']}:{deal['deal_price']}"
        return hashlib.md5(unique_string.encode()).hexdigest()
    
    def filter_duplicates(self, deals: List[Dict]) -> List[Dict]:
        unique_deals = []
        
        for deal in deals:
            deal_hash = self.generate_deal_hash(deal)
            
            if not self.db.is_duplicate_deal(deal_hash):
                unique_deals.append(deal)
                self.db.add_deal(deal_hash, deal['product_name'], deal['site'])
        
        return unique_deals
    
    def rank_deals(self, deals: List[Dict]) -> List[Dict]:
        def deal_score(deal):
            discount = deal.get('discount', 0)
            price = deal.get('deal_price', 0)
            
            score = discount * 10
            
            if price > 5000:
                score += 20
            elif price > 1000:
                score += 10
            
            return score
        
        return sorted(deals, key=deal_score, reverse=True)
    
    def process_deals(self, all_deals: List[Dict]) -> List[Dict]:
        unique_deals = self.filter_duplicates(all_deals)
        ranked_deals = self.rank_deals(unique_deals)
        return ranked_deals[:20]
