from typing import Dict, List

from .base_scraper import BaseScraper


class TataCliqScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Tata CLIQ"
        self.update_logger()
        self.base_url = "https://www.tatacliq.com"
        self.deal_urls = [
            f"{self.base_url}/c/food-offers",
            f"{self.base_url}/c/electronics-offers",
            f"{self.base_url}/offers",
            self.base_url,
        ]
        self.card_selectors = [
            "div.ProductModule__base",
            "div.product-tile",
            "div[role='listitem']",
            "a[href*='/p-']",
        ]
        self.title_selectors = [
            "div.ProductDescription__name",
            "h3",
            "div.product-title",
            "span.product-name",
        ]
        self.price_selectors = [
            "div.ProductDescription__price",
            "div.ProductDescription__discountedPrice",
            "span.product-price",
            "span.price",
        ]
        self.original_selectors = ["div.ProductDescription__price", "span.old-price", "span.mrp"]
        self.discount_selectors = ["div.ProductDescription__discount", "span.discount"]
        self.url_selectors = ["a[href*='/p-']", "a"]

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
