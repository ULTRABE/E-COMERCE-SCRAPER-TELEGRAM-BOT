from .base_scraper import BaseScraper
from typing import List, Dict

class SnapdealScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Snapdeal"
        self.deal_urls = [
            "https://www.snapdeal.com/products/mobiles-mobile-phones",
            "https://www.snapdeal.com/products/mens-footwear",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.deal_urls:
            soup = self.get_page(url)
            if not soup:
                continue
            
            products = soup.find_all('div', class_='product-tuple-listing')[:10]
            
            for product in products:
                try:
                    link = product.find('a', class_='dp-widget-link')
                    if not link:
                        continue
                    
                    product_url = link.get('href', '')
                    
                    title = product.find('p', class_='product-title')
                    if not title:
                        continue
                    
                    product_name = title.text.strip()
                    
                    price_elem = product.find('span', class_='product-price')
                    original_elem = product.find('span', class_='product-desc-price')
                    discount_elem = product.find('div', class_='product-discount')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.6
                    
                    if discount_elem:
                        discount = int(''.join(filter(str.isdigit, discount_elem.text)))
                    else:
                        discount = self.calculate_discount(original_price, deal_price)
                    
                    image_url = self.extract_image_url(product)
                    
                    if discount >= 30 and deal_price > 0:
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
                    print(f"Error parsing Snapdeal product: {e}")
                    continue
        
        return deals[:15]
