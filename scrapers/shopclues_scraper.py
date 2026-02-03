from .base_scraper import BaseScraper
from typing import List, Dict

class ShopcluesScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "ShopClues"
        self.deal_urls = [
            "https://www.shopclues.com/wholesale.html",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue
            
            products = soup.find_all('div', class_='column')[:15]
            
            for product in products:
                try:
                    link = product.find('a')
                    if not link:
                        continue
                    
                    product_url = link.get('href', '')
                    if not product_url.startswith('http'):
                        product_url = 'https://www.shopclues.com' + product_url
                    
                    title = product.find('h2')
                    if not title:
                        continue
                    
                    product_name = title.text.strip()
                    
                    price_elem = product.find('span', class_='p_price')
                    original_elem = product.find('span', class_='og_price')
                    discount_elem = product.find('span', class_='discnt')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.7
                    
                    if discount_elem:
                        discount = int(''.join(filter(str.isdigit, discount_elem.text)))
                    else:
                        discount = self.calculate_discount(original_price, deal_price)
                    
                    image_url = self.extract_image_url(product)
                    
                    if discount >= 35 and deal_price > 0:
                        deals.append({
                            'product_name': product_name[:100],
                            'deal_price': int(deal_price),
                            'original_price': int(original_price),
                            'discount': discount,
                            'url': product_url,
                            'site': self.site_name,
                            'image_url': image_url
                        })
                except Exception as e:
                    print(f"Error parsing ShopClues product: {e}")
                    continue
        
        return deals[:15]
