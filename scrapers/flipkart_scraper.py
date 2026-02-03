from .base_scraper import BaseScraper
from typing import List, Dict

class FlipkartScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Flipkart"
        self.deal_urls = [
            "https://www.flipkart.com/offers-list/content?screen=dynamic&pk=themeViews%3DDealoftheDay~widgetType%3DdealOfTheDay~contentType%3Dneo&wid=2.dealOfTheDay.OMU_RHS_DOTD",
        ]
    
    def scrape(self) -> List[Dict]:
        deals = []
        
        url = "https://www.flipkart.com/offers-store"
        soup = self.get_page(url)
        if not soup:
            return deals
        
        deal_items = soup.find_all('a', {'class': '_1fQZEK'})[:15]
        
        for item in deal_items:
            try:
                product_url = 'https://www.flipkart.com' + item.get('href', '')
                
                title_elem = item.find('div', class_='_4rR01T')
                if not title_elem:
                    continue
                
                product_name = title_elem.text.strip()
                
                price_elem = item.find('div', class_='_30jeq3')
                original_elem = item.find('div', class_='_3I9_wc')
                discount_elem = item.find('div', class_='_3Ay6sb')
                
                if not price_elem:
                    continue
                
                deal_price = self.extract_price(price_elem.text)
                original_price = self.extract_price(original_elem.text) if original_elem else deal_price * 1.4
                
                if discount_elem:
                    discount_text = discount_elem.text.strip()
                    discount = int(''.join(filter(str.isdigit, discount_text)))
                else:
                    discount = self.calculate_discount(original_price, deal_price)
                
                if discount >= 30 and deal_price > 0:
                    deals.append({
                        'product_name': product_name,
                        'deal_price': int(deal_price),
                        'original_price': int(original_price),
                        'discount': discount,
                        'url': product_url.split('?')[0],
                        'site': self.site_name
                    })
            except Exception as e:
                print(f"Error parsing Flipkart deal: {e}")
                continue
        
        return deals[:15]
