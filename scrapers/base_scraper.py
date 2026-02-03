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
    
    def get_page(self, url: str, timeout: int = 10) -> Optional[BeautifulSoup]:
        try:
            time.sleep(random.uniform(1, 3))
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
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
