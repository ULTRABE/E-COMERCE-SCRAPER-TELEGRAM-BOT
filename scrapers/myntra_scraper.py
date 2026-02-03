from .base_scraper import BaseScraper
from typing import List, Dict

class MyntraScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Myntra"
        self.categories = [
            "https://www.myntra.com/men-tshirts",
            "https://www.myntra.com/women-kurtas-kurtis-suits",
            "https://www.myntra.com/sports-shoes",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        for url in self.categories:
            soup = self.get_page(url)
            if not soup:
                continue
            
            products = soup.find_all('li', class_='product-base')[:5]
            
            for product in products:
                try:
                    link = product.find('a')
                    if not link:
                        continue
                    
                    product_url = 'https://www.myntra.com/' + link.get('href', '')
                    
                    title = product.find('h3', class_='product-brand')
                    subtitle = product.find('h4', class_='product-product')
                    
                    if not title:
                        continue
                    
                    product_name = title.text.strip()
                    if subtitle:
                        product_name += ' ' + subtitle.text.strip()
                    
                    price_elem = product.find('span', class_='product-discountedPrice')
                    original_elem = product.find('span', class_='product-strike')
                    discount_elem = product.find('span', class_='product-discountPercentage')
                    
                    if not price_elem:
                        continue
                    
                    deal_price = self.extract_price(price_elem.text)
                    original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.5
                    
                    if discount_elem:
                        discount = int(''.join(filter(str.isdigit, discount_elem.text)))
                    else:
                        discount = self.calculate_discount(original_price, deal_price)
                    
                    if discount >= 40 and deal_price > 0:
                        deals.append({
                            'product_name': product_name[:100],
                            'deal_price': int(deal_price),
                            'original_price': int(original_price),
                            'discount': discount,
                            'url': product_url.split('?')[0],
                            'site': self.site_name
                        })
                except Exception as e:
                    print(f"Error parsing Myntra product: {e}")
                    continue
        
        return deals[:15]
