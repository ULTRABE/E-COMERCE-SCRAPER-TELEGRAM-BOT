from typing import Dict, List

from .base_scraper import BaseScraper


class SnapdealScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Snapdeal"
        self.update_logger()
        self.base_url = "https://www.snapdeal.com"
        self.deal_urls = [
            f"{self.base_url}/offers",
            f"{self.base_url}/deals",
            f"{self.base_url}/products/discount",
            self.base_url,
        ]
        self.card_selectors = [
            "div.product-tuple-listing",
            "div.product-tuple-description",
            "div.product-tuple",
            "a[href*='/product/']",
        ]
        self.title_selectors = [
            "p.product-title",
            "p.product-desc-rating",
            "a.dp-widget-link",
            "div.product-title",
        ]
        self.price_selectors = [
            "span.product-price",
            "span.lfloat.product-price",
            "span.discounted-price",
        ]
        self.original_selectors = ["span.product-desc-price", "span.product-price"]
        self.discount_selectors = ["span.product-discount", "span.discount"]
        self.url_selectors = ["a.dp-widget-link", "a[href*='/product/']", "a"]

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
