from typing import Dict, List

from .base_scraper import BaseScraper


class NykaaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Nykaa"
        self.update_logger()
        self.base_url = "https://www.nykaa.com"
        self.deal_urls = [
            f"{self.base_url}/offers",
            f"{self.base_url}/sale",
            f"{self.base_url}/all-products",
            self.base_url,
        ]
        self.card_selectors = [
            "div.css-1rd7vky",
            "div.css-1mjn6sv",
            "div[class*='ProductCard']",
            "a[href*='/p/']",
        ]
        self.title_selectors = [
            "div.css-1jwq2q5",
            "div[class*='title']",
            "h3",
            "h4",
        ]
        self.price_selectors = [
            "span.css-111z9ua",
            "span[class*='price']",
            "div[class*='price'] span",
        ]
        self.original_selectors = ["span[class*='mrp']", "span[class*='strike']"]
        self.discount_selectors = ["span[class*='off']", "span[class*='discount']"]
        self.url_selectors = ["a[href*='/p/']", "a"]

    def scrape(self) -> List[Dict]:
        deals: List[Dict] = []
        soup, used_url = self.get_page_from_urls(self.deal_urls)
        if not soup:
            self.logger.error("%s: unable to fetch any deal page", self.site_name)
            return deals

        cards = self.select_all(soup, self.card_selectors)
        self.logger.info("%s: found %s cards from %s", self.site_name, len(cards), used_url)

        for card in cards[:40]:
            deal = self.build_deal(
                card,
                self.base_url,
                self.title_selectors,
                self.price_selectors,
                self.url_selectors,
                self.original_selectors,
                self.discount_selectors,
            )
            if deal:
                deals.append(deal)

        self.logger.info("%s: parsed %s deals", self.site_name, len(deals))
        return deals[:15]
