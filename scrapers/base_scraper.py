import random
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config


class BaseScraper:
    def __init__(self):
        self.site_name = "Unknown"
        self.headers = {
            "User-Agent": config.USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
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

    def get_response(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(0.5, 1.2))
                proxy = self.get_next_proxy()
                kwargs = {"timeout": timeout}
                if proxy:
                    kwargs["proxies"] = proxy

                response = self.session.get(url, **kwargs)
                response.raise_for_status()
                return response
            except Exception as e:
                print(f"Error fetching {url} (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
        return None

    def get_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        response = self.get_response(url, timeout=timeout)
        if not response:
            return None
        return BeautifulSoup(response.text, "html.parser")

    def extract_image_url(self, element, base_url: str = "") -> str:
        if not element:
            return ""

        img = element.find("img")
        if not img:
            return ""

        img_url = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("srcset", "").split(" ")[0]
            or ""
        )
        if not img_url:
            return ""
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        if base_url:
            img_url = urljoin(base_url, img_url)
        return img_url

    def normalize_url(self, url: str, base_url: str) -> str:
        if not url:
            return base_url
        cleaned = url.split("?")[0]
        return urljoin(base_url, cleaned)

    def is_high_quality_image(self, image_url: str) -> bool:
        if not image_url:
            return False
        low_quality_hints = ["40x40", "60x60", "80x80", "thumbnail", "thumb", "icon"]
        lowered = image_url.lower()
        return not any(hint in lowered for hint in low_quality_hints)

    def extract_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0
        price_str = (
            price_str.replace("₹", "")
            .replace(",", "")
            .replace("Rs.", "")
            .replace("Rs", "")
            .strip()
        )
        try:
            return float("".join(filter(lambda x: x.isdigit() or x == ".", price_str)))
        except Exception:
            return 0.0

    def calculate_discount(self, original: float, deal: float) -> int:
        if original <= 0 or deal <= 0 or deal >= original:
            return 0
        return int(((original - deal) / original) * 100)

    def scrape(self) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement scrape method")
