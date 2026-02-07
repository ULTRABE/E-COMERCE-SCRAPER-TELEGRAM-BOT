from typing import Dict, List

from .base_scraper import BaseScraper


class ShopcluesScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "ShopClues"
        self.update_logger()
        self.base_url = "https://www.shopclues.com"
        self.deal_urls = [
            f"{self.base_url}/deals",
            f"{self.base_url}/offers",
            f"{self.base_url}/s/daily-deals",
            self.base_url,
        ]
        self.card_selectors = [
            "div.product",
            "div.product_card",
            "div.column.col3",
            "div.grid-product",
            "a[href*='/product/']",
        ]
        self.title_selectors = [
            "h2",
            "h3",
            "div.prod_name",
            "span.prod_name",
            "div.product-title",
        ]
        self.price_selectors = [
            "span.p_price",
            "span.price",
            "span.f_price",
            "div.price",
        ]
        self.original_selectors = ["span.old_price", "span.market-price", "span.discount", "span.strike"]
        self.discount_selectors = ["span.discount", "span.offer", "span[class*='off']"]
        self.url_selectors = ["a[href*='/product/']", "a"]

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
