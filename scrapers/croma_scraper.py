from .base_scraper import BaseScraper
from typing import List, Dict

class CromaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Croma"
        self.deal_urls = [
            "https://www.croma.com/deals-of-the-day",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue
            
            products = soup.find_all('li', class_='product')[:15]
            
            for product in products:
                try:
                    link = product.find('a', class_='product-link')
                    if not link:
                        continue
                    
                    product_url = link.get('href', '')
                    if not product_url.startswith('http'):
                        product_url = 'https://www.croma.com' + product_url
                    
                    title = product.find('h3', class_='product-title')
                    if not title:
                        continue
                    
                    product_name = title.text.strip()
                    
                    price_elem = product.find('span', class_='amount')
                    original_elem = product.find('span', class_='old-price')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.25
                    
                    discount = self.calculate_discount(original_price, deal_price)
                    
                    if discount >= 15 and deal_price > 0:
                        deals.append({
                            'product_name': product_name[:100],
                            'deal_price': int(deal_price),
                            'original_price': int(original_price),
                            'discount': discount,
                            'url': product_url.split('?')[0],
                            'site': self.site_name
                        })
                except Exception as e:
                    print(f"Error parsing Croma product: {e}")
                    continue
        
        return deals[:15]
