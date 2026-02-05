import json
import logging
import random
import time
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import config


class BaseScraper:
    def __init__(self):
        self.site_name = "Unknown"
        self.headers = dict(config.BETTER_HEADERS)
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.proxies: List[Dict[str, str]] = []
        self.current_proxy_index = 0
        self.max_retries = 3
        self.request_delay_range = (1.0, 2.5)
        self.proxy_manager = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def update_logger(self):
        self.logger = logging.getLogger(self.site_name)

    def set_proxy_manager(self, proxy_manager) -> None:
        self.proxy_manager = proxy_manager

    def set_proxies(self, proxies: List[Dict[str, str]]):
        self.proxies = proxies or []
        self.current_proxy_index = 0
        self.logger.debug("%s proxies configured for %s", len(self.proxies), self.site_name)

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        if not self.proxies:
            return None
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        return proxy

    def _delay_request(self) -> None:
        time.sleep(random.uniform(*self.request_delay_range))

    def _looks_blocked(self, text: str) -> bool:
        lowered = text.lower()
        block_terms = ["captcha", "verify you are human", "robot check", "access denied"]
        return any(term in lowered for term in block_terms)

    def _log_response(self, url: str, response: requests.Response, proxy: Optional[Dict[str, str]]):
        proxy_info = "proxy" if proxy else "direct"
        self.logger.info(
            "[%s] %s %s status=%s size=%s",
            self.site_name,
            proxy_info,
            url,
            response.status_code,
            len(response.content or b""),
        )

    def _fetch_url(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        last_error = None
        for attempt in range(1, self.max_retries + 1):
            proxy = self.get_next_proxy()
            proxy_options = [proxy] if proxy else [None]
            if proxy:
                proxy_options.append(None)
            for proxy_option in proxy_options:
                try:
                    self._delay_request()
                    response = self.session.get(
                        url,
                        timeout=timeout,
                        proxies=proxy_option,
                        allow_redirects=True,
                    )
                    self._log_response(url, response, proxy_option)
                    if response.status_code >= 400:
                        raise requests.HTTPError(
                            f"{response.status_code} status for {url}",
                            response=response,
                        )
                    if self._looks_blocked(response.text):
                        raise requests.HTTPError("Blocked by anti-bot", response=response)
                    if "login" in response.url.lower():
                        self.logger.warning("%s redirected to login page: %s", self.site_name, response.url)
                        return None
                    if proxy_option and self.proxy_manager:
                        self.proxy_manager.mark_proxy_success(proxy_option)
                    return BeautifulSoup(response.text, "html.parser")
                except requests.RequestException as exc:
                    last_error = exc
                    if proxy_option and self.proxy_manager:
                        self.proxy_manager.mark_proxy_failed(proxy_option)
                    self.logger.warning(
                        "Attempt %s/%s failed for %s (%s)",
                        attempt,
                        self.max_retries,
                        url,
                        exc,
                    )
                    if proxy_option is None:
                        break
            self.logger.debug("Retrying %s after failure", url)
        if last_error:
            self.logger.error("Giving up on %s: %s", url, last_error)
        return None

    def get_page(self, url: str, timeout: int = 15) -> Optional[BeautifulSoup]:
        return self._fetch_url(url, timeout=timeout)

    def get_page_from_urls(self, urls: Sequence[str], timeout: int = 15) -> Tuple[Optional[BeautifulSoup], Optional[str]]:
        for url in urls:
            soup = self._fetch_url(url, timeout=timeout)
            if soup:
                self.logger.info("%s succeeded with URL: %s", self.site_name, url)
                return soup, url
            self.logger.warning("%s failed with URL: %s", self.site_name, url)
        return None, None

    def select_first(self, element: BeautifulSoup, selectors: Sequence[str]):
        for selector in selectors:
            found = element.select_one(selector)
            if found:
                return found
        return None

    def select_all(self, element: BeautifulSoup, selectors: Sequence[str]) -> List:
        for selector in selectors:
            found = element.select(selector)
            if found:
                return found
        return []

    def extract_text(self, element: BeautifulSoup, selectors: Sequence[str], attr: Optional[str] = None) -> str:
        if not element:
            return ""
        target = self.select_first(element, selectors)
        if not target:
            return ""
        if attr:
            return (target.get(attr) or "").strip()
        return target.get_text(strip=True)

    def extract_url(self, element: BeautifulSoup, selectors: Sequence[str], base_url: str) -> str:
        if not element:
            return ""
        if hasattr(element, "get"):
            href = element.get("href") or element.get("data-href") or element.get("data-url")
            if href:
                return self.make_absolute_url(base_url, href)
        for selector in selectors:
            target = element.select_one(selector)
            if not target:
                continue
            href = target.get("href") or target.get("data-href") or target.get("data-url")
            if href:
                return self.make_absolute_url(base_url, href)
        return ""

    def make_absolute_url(self, base_url: str, url: str) -> str:
        if not url:
            return ""
        return urljoin(base_url, url)

    def extract_image_url(self, element) -> str:
        if not element:
            return ""
        img = element.find("img")
        if not img:
            return ""
        img_url = (
            img.get("src")
            or img.get("data-src")
            or img.get("data-lazy-src")
            or img.get("data-original")
        )
        if not img_url:
            srcset = img.get("srcset") or ""
            if srcset:
                img_url = srcset.split(",")[-1].strip().split(" ")[0]
        if not img_url:
            dynamic = img.get("data-a-dynamic-image")
            if dynamic:
                try:
                    img_url = next(iter(json.loads(dynamic).keys()))
                except (json.JSONDecodeError, StopIteration):
                    img_url = ""
        if img_url and img_url.startswith("//"):
            img_url = "https:" + img_url
        return img_url or ""

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
        except (TypeError, ValueError):
            return 0.0

    def extract_discount(self, discount_str: str) -> int:
        if not discount_str:
            return 0
        digits = "".join(filter(str.isdigit, discount_str))
        return int(digits) if digits else 0

    def calculate_discount(self, original: float, deal: float) -> int:
        if original == 0 or deal == 0:
            return 0
        return int(((original - deal) / original) * 100)

    def build_deal(
        self,
        card,
        base_url: str,
        title_selectors: Sequence[str],
        price_selectors: Sequence[str],
        url_selectors: Sequence[str],
        original_selectors: Sequence[str],
        discount_selectors: Sequence[str],
    ) -> Optional[Dict]:
        product_name = self.extract_text(card, title_selectors)
        if not product_name:
            return None
        price_text = self.extract_text(card, price_selectors)
        if not price_text:
            return None
        deal_price = self.extract_price(price_text)
        if deal_price <= 0:
            return None
        original_text = self.extract_text(card, original_selectors)
        original_price = self.extract_price(original_text) if original_text else 0
        if original_price <= 0 or original_price < deal_price:
            original_price = max(deal_price, deal_price * 1.2)
        discount_text = self.extract_text(card, discount_selectors)
        discount = self.extract_discount(discount_text)
        if discount == 0:
            discount = self.calculate_discount(original_price, deal_price)
        product_url = self.extract_url(card, url_selectors, base_url) or base_url
        image_url = self.extract_image_url(card)
        return {
            "product_name": product_name,
            "deal_price": int(deal_price),
            "original_price": int(original_price),
            "discount": discount,
            "url": product_url.split("?")[0],
            "site": self.site_name,
            "image_url": image_url,
        }

    def scrape(self) -> List[Dict]:
        raise NotImplementedError("Subclasses must implement scrape method")
