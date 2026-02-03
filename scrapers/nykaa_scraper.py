from .base_scraper import BaseScraper
from typing import List, Dict
import re

class NykaaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Nykaa"
        self.base_url = "https://www.nykaa.com"
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        try:
            # Nykaa deals page
            url = "https://www.nykaa.com/offers"
            soup = self.get_page(url)
            
            if not soup:
                return deals
            
            # Find product cards
            product_cards = soup.find_all('div', class_='ProductCard')
            
            for card in product_cards[:10]:  # Limit to 10 deals
                try:
                    product_name = card.find('div', class_='ProductCard__name')
                    deal_price = card.find('div', class_='ProductCard__price')
                    original_price = card.find('div', class_='ProductCard__mrp')
                    
                    if product_name and deal_price:
                        name = product_name.text.strip()
                        price = self.extract_price(deal_price.text)
                        mrp = self.extract_price(original_price.text) if original_price else price * 1.3  # Estimate
                        
                        if price > 0 and mrp > price:
                            discount = self.calculate_discount(mrp, price)
                            
                            if discount >= 30:  # Only high discount deals
                                deals.append({
                                    'product_name': name,
                                    'deal_price': int(price),
                                    'original_price': int(mrp),
                                    'discount': discount,
                                    'url': self.base_url,
                                    'site': self.site_name
                                })
                except Exception as e:
                    print(f"Error parsing Nykaa product: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error in Nykaa scraper: {e}")
        
        return deals