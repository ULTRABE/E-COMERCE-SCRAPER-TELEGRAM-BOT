from .base_scraper import BaseScraper
from typing import List, Dict

class AmazonScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Amazon India"
        self.deal_urls = [
            "https://www.amazon.in/gp/goldbox",
            "https://www.amazon.in/deals",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue
            
            deal_items = soup.find_all('div', {'data-deal-id': True})[:10]
            
            for item in deal_items:
                try:
                    title_elem = item.find('a', {'aria-label': True})
                    if not title_elem:
                        continue
                    
                    product_name = title_elem.get('aria-label', '').strip()
                    product_url = 'https://www.amazon.in' + title_elem.get('href', '')
                    
                    price_elem = item.find('span', class_='a-price-whole')
                    original_elem = item.find('span', class_='a-text-price')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.3
                    
                    discount = self.calculate_discount(original_price, deal_price)
                    image_url = self.extract_image_url(item)
                    
                    if discount >= 30 and deal_price > 0:
                        deals.append({
                            'product_name': product_name,
                            'deal_price': int(deal_price),
                            'original_price': int(original_price),
                            'discount': discount,
                            'url': product_url.split('?')[0],
                            'site': self.site_name,
                            'image_url': image_url
                        })
                except Exception as e:
                    print(f"Error parsing Amazon deal: {e}")
                    continue
        
        return deals[:15]
