from typing import Dict, List

from .base_scraper import BaseScraper


class AjioScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "AJIO"
        self.update_logger()
        self.base_url = "https://www.ajio.com"
        self.deal_urls = [
            f"{self.base_url}/sale",
            f"{self.base_url}/deals",
            f"{self.base_url}/end-of-season-sale",
            self.base_url,
        ]
        self.card_selectors = [
            "div.item",
            "div.product-listing",
            "div[class*='item']",
            "a[href*='/p/']",
        ]
        self.title_selectors = [
            "div.nameCls",
            "div.brand",
            "div.name",
            "span.name",
            "div[class*='name']",
        ]
        self.price_selectors = [
            "span.price",
            "div.price",
            "span.offer-price",
            "div[class*='price']",
        ]
        self.original_selectors = ["span.orginal-price", "span.original-price", "span.old-price"]
        self.discount_selectors = ["span.discount", "span.offer", "span[class*='off']"]
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
