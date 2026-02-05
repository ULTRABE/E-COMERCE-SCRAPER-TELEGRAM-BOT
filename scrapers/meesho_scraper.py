from typing import Dict, List

from .base_scraper import BaseScraper


class MeeshoScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.site_name = "Meesho"
        self.update_logger()
        self.base_url = "https://www.meesho.com"
        self.deal_urls = [
            f"{self.base_url}/offers",
            f"{self.base_url}/deals",
            self.base_url,
        ]
        self.card_selectors = [
            "div[data-testid='product-card']",
            "a[href*='/product/']",
            "div[class*='ProductCard']",
            "div[class*='ProductList'] a",
        ]
        self.title_selectors = [
            "p[class*='ProductTitle']",
            "p[class*='Text__StyledText']",
            "div[class*='product-title']",
            "h3",
        ]
        self.price_selectors = [
            "span[class*='ProductPrice']",
            "h5",
            "span[class*='price']",
        ]
        self.original_selectors = ["span[class*='strike']", "span[class*='Original']", "span[class*='mrp']"]
        self.discount_selectors = ["span[class*='discount']", "span[class*='off']"]
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
