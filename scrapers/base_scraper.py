import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import config
import time
import random

class BaseScraper:
    def __init__(self):
        self.site_name = "Unknown"
        self.headers = {
            'User-Agent': config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.proxies = []
        self.current_proxy_index = 0
    
    def set_proxies(self, proxies: List[Dict]):
        self.proxies = proxies
        self.current_proxy_index = 0
    
    def get_next_proxy(self) -> Optional[Dict]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy
    
    def get_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                proxy = self.get_next_proxy()
                
                if proxy:
                    response = self.session.get(url, timeout=timeout, proxies=proxy)
                else:
                    response = self.session.get(url, timeout=timeout)
                
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except Exception as e:
                print(f"Error fetching {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
        return None
    
    def extract_image_url(self, element) -> str:
        if not element:
            return ""
        
        img = element.find('img')
        if img:
            img_url = img.get('src') or img.get('data-src') or img.get('data-lazy-src') or ""
            if img_url and img_url.startswith('//'):
                img_url = 'https:' + img_url
            return img_url
        return ""
    
    def extract_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0
        price_str = price_str.replace('₹', '').replace(',', '').replace('Rs.', '').replace('Rs', '').strip()
        try:
            return float(''.join(filter(lambda x: x.isdigit() or x == '.', price_str)))
        except:
            return 0.0
    
    def calculate_discount(self, original: float, deal: float) -> int:
        if original == 0 or deal == 0:
            return 0
        return int(((original - deal) / original) * 100)
    
    def scrape(self) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement scrape method")
