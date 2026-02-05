from typing import Dict, List

from .base_scraper import BaseScraper


class MyntraScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Myntra"
        self.update_logger()
        self.base_url = "https://www.myntra.com"
        self.deal_urls = [
            f"{self.base_url}/sale",
            f"{self.base_url}/end-of-season-sale",
            f"{self.base_url}/new-arrivals",
            self.base_url,
        ]
        self.card_selectors = [
            "li.product-base",
            "div.product-base",
            "div.product-productMetaInfo",
            "a[href*='/']",
        ]
        self.title_selectors = [
            "h3.product-brand",
            "h4.product-product",
            "div.product-productMetaInfo h3",
            "div.product-productMetaInfo h4",
        ]
        self.price_selectors = [
            "span.product-discountedPrice",
            "span.product-price",
            "div.product-price",
        ]
        self.original_selectors = ["span.product-strike", "span.product-original-price"]
        self.discount_selectors = ["span.product-discountPercentage", "span.product-discount"]
        self.url_selectors = ["a[href]", "a"]

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
