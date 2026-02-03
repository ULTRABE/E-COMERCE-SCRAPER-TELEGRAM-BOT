from .base_scraper import BaseScraper
from typing import List, Dict

class VijaysalesScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Vijay Sales"
        self.deal_urls = [
            "https://www.vijaysales.com/deals-of-the-day",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue
            
            products = soup.find_all('div', class_='product-item')[:15]
            
            for product in products:
                try:
                    link = product.find('a', class_='product-item-link')
                    if not link:
                        continue
                    
                    product_url = link.get('href', '')
                    product_name = link.text.strip()
                    
                    price_elem = product.find('span', class_='price')
                    original_elem = product.find('span', class_='old-price')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.3
                    
                    discount = self.calculate_discount(original_price, deal_price)
                    
                    if discount >= 15 and deal_price > 0:
                        deals.append({
                            'product_name': product_name[:100],
                            'deal_price': int(deal_price),
                            'original_price': int(original_price),
                            'discount': discount,
                            'url': product_url,
                            'site': self.site_name
                        })
                except Exception as e:
                    print(f"Error parsing Vijay Sales product: {e}")
                    continue
        
        return deals[:15]
