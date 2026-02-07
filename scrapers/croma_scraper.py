from typing import Dict, List

from .base_scraper import BaseScraper


class CromaScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Croma"
        self.update_logger()
        self.base_url = "https://www.croma.com"
        self.deal_urls = [
            f"{self.base_url}/c/offers",
            f"{self.base_url}/offers",
            f"{self.base_url}/promotions",
            self.base_url,
        ]
        self.card_selectors = [
            "li.product-item",
            "div.product",
            "div.product__list",
            "div[data-testid='product']",
            "a[href*='/p/']",
        ]
        self.title_selectors = [
            "h3",
            "h2",
            "div.product-title",
            "div.product__title",
        ]
        self.price_selectors = [
            "span.amount",
            "span.new-price",
            "span.price",
            "div.product__price span",
        ]
        self.original_selectors = ["span.mrp", "span.old-price", "span.strike"]
        self.discount_selectors = ["span.discount", "span[class*='off']"]
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
